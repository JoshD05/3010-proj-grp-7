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
    <title>ECU CS Dashboard</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .navbar {
            overflow: hidden;
            background-color: #1E90FF;  /* Dodger Blue */
            color: white;
            display: flex;
            justify-content: space-between;
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
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">ECU CS Dashboard</div>
        <div class="navbar-links">
            <a href="csdashboard.py">Home</a>
            <a href="faculty.py">Faculty</a>
        </div>
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