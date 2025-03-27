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
    <title>Database Tables</title>
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
        .table-container {
            margin: 0 auto;
            max-width: 90%;
            overflow-x: auto;
        }
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h2 {
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="csdashboard.py">Home</a>
        <a href="faculty.py">Faculty</a>
    </div>
""")

tables = ['dep_course_sched', 'dep_faculty', 'department_course_directors', 
         'faculty_dates', 'faculty_standard', 'prerequisites', 'staff']

def create_table(table_name):
    cursor.execute(f"SELECT * FROM {table_name};")
    results = cursor.fetchall()
    if results:
        print(f"<h2>{table_name.replace('_', ' ').title()}</h2>")
        print("<div class='table-container'>")
        print("<table>")
        print("<tr>")
        for col in cursor.description:
            print(f"<th>{col.name.replace('_', ' ').title()}</th>")
        print("</tr>")
        for row in results:
            print("<tr>")
            for value in row:
                print(f"<td>{value if value is not None else 'N/A'}</td>")
            print("</tr>")
        print("</table>")
        print("</div>")
    else:
        print(f"<p>No data found in {table_name}</p>")

print("<div class='content'>")
for table in tables:
    create_table(table)
print("</div>")

# Close connection
cursor.close()
conn.close()

print("</body></html>")