#!/usr/bin/python3
import psycopg2
import psycopg2.extras

# Database connection
conn = psycopg2.connect("host=192.168.56.30 dbname=dashboard user=webuser1 password=student")
cursor = conn.cursor()

print("Content-type: text/html\n\n")
print("""
<html>
<head>
    <title>ECU CS Faculty Directory</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .navbar {
            overflow: hidden;
            background-color: #1E90FF;
            color: white;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            padding: 10px 20px;
        }
        .navbar-brand {
            font-size: 20px;
            font-weight: bold;
        }
        .navbar-links a {
            color: white;
            text-decoration: none;
            margin-left: 15px;
            transition: color 0.3s ease;
        }
        .navbar-links a:hover {
            color: #e0e0e0;
        }
        .content {
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
        }
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-bottom: 20px;
            box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
            background-color: white;
        }
        table th {
            background-color: #f2f2f2;
            color: #333;
            font-weight: bold;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #ddd;
        }
        table td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        table tr:hover {
            background-color: #f5f5f5;
        }
        h2 {
            color: #333;
            border-bottom: 2px solid #1E90FF;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        .table-container {
            overflow-x: auto;
            border-radius: 5px;
        }
        .search-container {
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">ECU CS Faculty Directory</div>
        <div class="navbar-links">
            <a href="csdashboard.py">Home</a>
            <a href="faculty.py">Faculty</a>
            <a href="courses.py">Courses</a>
            <a href="fte.py">FTE</a>
        </div>
    </div>
""")

def create_faculty_table():
    """
    Create a view of the faculty table with search and sort capability
    """
    # Check if there's a search parameter in the URL
    import os
    query_string = os.environ.get('QUERY_STRING', '')
    
    # Parse parameters
    params = {}
    for param in query_string.split('&'):
        if '=' in param:
            key, value = param.split('=')
            params[key] = value
    
    # Extract search term and sorting parameters
    search_term = params.get('search', '').strip()
    sort_by = params.get('sort_by', '').strip()
    sort_order = params.get('sort_order', 'ASC').strip().upper()

    try:
        # Validate sort columns
        valid_sort_columns = ['last', 'rank', 'first', 'id']
        if sort_by and sort_by not in valid_sort_columns:
            sort_by = None

        # Prepare the query based on whether there's a search term
        if search_term:
            # Search across all columns
            query = """
            SELECT * FROM dep_faculty 
            WHERE 
                cast(id as text) ILIKE %s OR 
                cast(honorific as text) ILIKE %s OR
                cast(first as text) ILIKE %s OR 
                cast(mi as text) ILIKE %s OR
                cast(last as text) ILIKE %s OR
                cast(email as text) ILIKE %s OR 
                cast(phone as text) ILIKE %s OR
                cast(office as text) ILIKE %s OR
                cast(research_interests as text) ILIKE %s OR
                cast(rank as text) ILIKE %s OR 
                cast(remarks as text) ILIKE %s OR
                cast(currently_employed as text) ILIKE %s
            """
            # Add sorting if specified
            if sort_by:
                query += f" ORDER BY {sort_by} {sort_order}"
            
            search_param = f'%{search_term}%'
            cursor.execute(query, 
                (search_param,)*12
            )
            print(f"<h2>Search Results for '{search_term}'</h2>")
        else:
            # If no search term, fetch all faculty
            query = "SELECT * FROM dep_faculty"
            
            # Add sorting if specified
            if sort_by:
                query += f" ORDER BY {sort_by} {sort_order}"
            
            cursor.execute(query)
            print("<h2>Faculty Directory</h2>")

        # Add search and sort form
        print("""
        <div class="search-container">
            <form method="get" action="faculty.py">
                <input type="text" name="search" placeholder="Search faculty..." value="{0}">
                <select name="sort_by">
                    <option value="">Sort By...</option>
                    <option value="last" {1}>Last Name</option>
                    <option value="rank" {2}>Rank</option>
                    <option value="first" {3}>First Name</option>
                </select>
                <select name="sort_order">
                    <option value="ASC" {4}>Ascending</option>
                    <option value="DESC" {5}>Descending</option>
                </select>
                <input type="submit" value="Search/Sort">
            </form>
        </div>
        """.format(
            search_term or '', 
            'selected' if sort_by == 'last' else '',
            'selected' if sort_by == 'rank' else '',
            'selected' if sort_by == 'first' else '',
            'selected' if sort_order == 'ASC' else '',
            'selected' if sort_order == 'DESC' else ''
        ))

        # Fetch results
        results = cursor.fetchall()

        # Print table
        print("<table>")
        
        # Print headers
        if results:
            print("<tr>")
            for col in cursor.description:
                print(f"<th>{col.name}</th>")
            print("</tr>")

            # Print rows
            for row in results:
                print("<tr>")
                for value in row:
                    print(f"<td>{value if value is not None else 'N/A'}</td>")
                print("</tr>")
        else:
            # If no results found
            print(f"<tr><td colspan='{len(cursor.description)}'>No faculty members found.</td></tr>")
        
        print("</table>")

    except Exception as e:
        print(f"<p>Error: {e}</p>")

# Display faculty table
create_faculty_table()

# Close connection
cursor.close()
conn.close()

print("</body></html>")