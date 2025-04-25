#!/usr/bin/python3
import psycopg2
import psycopg2.extras

conn = psycopg2.connect("host=localhost dbname=dashboard user=webuser1 password=student")
cursor = conn.cursor()

print("Content-type: text/html\n\n")
print("""
<html>
<head>
    <title>ECU CS Course Directory</title>
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
        .column-visibility {
            margin-bottom: 20px;
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">ECU CS Course Directory</div>
        <div class="navbar-links">
            <a href="csdashboard.py">Home</a>
            <a href="faculty.py">Faculty</a>
            <a href="courses.py">Courses</a>
            <a href="fte.py">FTE</a>
        </div>
    </div>
""")

def create_courses_table():
    """
    Create a view of the courses table
    """
    try:
        query = "SELECT prefix ||' '|| number AS number, title, GU, CH, frequency, active, description FROM dep_courses"
        cursor.execute(query)
        
        print("<div class='content'>")
        print("<h2>Course Info</h2>")
        
        print("<table>")
        
        print("<tr>")
        headers = ['Number', 'Title', 'GU', 'CH', 'Frequency', 'Active', 'Description']
        for header in headers:
            print(f"<th>{header}</th>")
        print("</tr>")
        
        # Rows
        results = cursor.fetchall()
        for row in results:
            print("<tr>")
            for value in row:
                # Yes/No
                if isinstance(value, bool):
                    value = 'Yes' if value else 'No'
                print(f"<td>{value if value is not None else 'N/A'}</td>")
            print("</tr>")
        
        print("</table>")
        print("</div>")

    except Exception as e:
        print(f"<p>Error: {e}</p>")

create_courses_table()

cursor.close()
conn.close()

print("</body></html>")
