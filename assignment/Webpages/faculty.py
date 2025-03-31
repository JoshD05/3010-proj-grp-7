#!/usr/bin/python3
import psycopg2
import psycopg2.extras
import cgi

# Connect to the database
conn = psycopg2.connect("host=192.168.56.30 dbname=dashboard user=webuser1 password=student")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
    # Parsing using cgi over os
    form = cgi.FieldStorage()
    
    search_term = form.getvalue('search', '').strip()
    sort_by = form.getvalue('sort_by', '').strip()
    sort_order = form.getvalue('sort_order', 'ASC').strip().upper()

    try:
        valid_sort_columns = ['last', 'rank', 'first', 'id']
        if sort_by and sort_by not in valid_sort_columns:
            sort_by = 'last'  # Default to last name if invalid sort field

        # sort the results in Python
        if search_term:
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
            search_param = f'%{search_term}%'
            cursor.execute(query, (search_param,)*12)
            print(f"<h2>Search Results for '{search_term}'</h2>")
        else:
            query = "SELECT * FROM dep_faculty"
            cursor.execute(query)
            print("<h2>Faculty Directory</h2>")

        # results as dictionaries
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # list of dictionaries for easier manipulation
        faculty_list = []
        for row in results:
            faculty_dict = {}
            for i, column in enumerate(columns):
                faculty_dict[column] = row[i]
            faculty_list.append(faculty_dict)
        
        # Sort
        if sort_by:
            reverse_sort = sort_order == 'DESC'

            faculty_list.sort(
                key=lambda x: (x[sort_by] is None, x[sort_by] if x[sort_by] is not None else ""),
                reverse=reverse_sort
            )

        print("""
        <div class="search-container">
            <form method="get" action="faculty.py">
                <input type="text" name="search" placeholder="Search faculty..." value="{}">
                <select name="sort_by">
                    <option value="">Sort By...</option>
                    <option value="last" {}>Last Name</option>
                    <option value="rank" {}>Rank</option>
                    <option value="first" {}>First Name</option>
                </select>
                <select name="sort_order">
                    <option value="ASC" {}>Ascending</option>
                    <option value="DESC" {}>Descending</option>
                </select>
                <input type="submit" value="Search/Sort">
            </form>
        </div>
        """.format(
            search_term, 
            'selected' if sort_by == 'last' else '',
            'selected' if sort_by == 'rank' else '',
            'selected' if sort_by == 'first' else '',
            'selected' if sort_order == 'ASC' else '',
            'selected' if sort_order == 'DESC' else ''
        ))

        # results table
        if faculty_list:
            print("<table>")
            # Headers
            print("<tr>")
            for column in columns:
                print(f"<th>{column}</th>")
            print("</tr>")

            # Rows
            for faculty in faculty_list:
                print("<tr>")
                for column in columns:
                    value = faculty[column]
                    print(f"<td>{value if value is not None else 'N/A'}</td>")
                print("</tr>")
            print("</table>")
        else:
            print("<p>No faculty members found.</p>")

    except Exception as e:
        print(f"<p>Error: {e}</p>")

create_faculty_table()

cursor.close()
conn.close()

print("</body></html>")