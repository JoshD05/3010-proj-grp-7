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
    <title>Faculty Directory</title>
    <style>
        .navbar {
            overflow: hidden;
            background-color: #333;
            margin-bottom: 20px;
        }
        .navbar a {
            float: left;
            display: block;
            color: white;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none;
        }
        .navbar a:hover {
            background-color: #ddd;
            color: black;
        }
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 5px;
            margin-bottom: 20px;
        }
        .search-container {
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="csdashboard.py">Home</a>
        <a href="faculty.py">Faculty</a>
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