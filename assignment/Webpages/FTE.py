#!/usr/bin/python3
import psycopg2
import psycopg2.extras
import os

conn = psycopg2.connect("host=192.168.56.30 dbname=dashboard user=webuser1 password=student")
cursor = conn.cursor()

print("Content-type: text/html\n\n")
print("""
<html>
<head>
    <title>ECU CS Faculty FTE</title>
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
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">ECU CS Faculty FTE</div>
        <div class="navbar-links">
            <a href="csdashboard.py">Home</a>
            <a href="faculty.py">Faculty</a>
            <a href="courses.py">Courses</a>
            <a href="fte.py">FTE</a>
        </div>
    </div>
""")

def create_fte_table():
    try:
        query = """
        SELECT 
            f.honorific, 
            f.first, 
            f.last, 
            cs.year, 
            cs.semester,
            cs.course_code,
            cs.ch,
            cs.enrollment
        FROM 
            dep_faculty f
        JOIN 
            dep_course_sched cs ON f.id = cs.instructor
        ORDER BY 
            f.last, f.first, cs.year, cs.semester
        """
        
        cursor.execute(query)
        results = cursor.fetchall()

        print("<h2>Faculty FTE Calculations</h2>")
        print("<table>")
        print("<tr>")
        print("<th>Name</th>")
        print("<th>Year</th>")
        print("<th>Semester</th>")
        print("<th>Course Code</th>")
        print("<th>CH</th>")
        print("<th>Enrollment</th>")
        print("<th>FTE</th>")
        print("</tr>")

        for row in results:
            # Unpack the row
            honorific, first, last, year, semester, course_code, ch, enrollment = row

            # Combine name 
            name = f"{honorific} {first} {last}".strip()

            # Default FTE divisor
            fte_divisor = 186.23

            # Determine FTE divisor based on course code
            if course_code.startswith('CSCI'):
                fte_divisor = 186.23 if 'G' in course_code else 406.24
            elif course_code.startswith('SENG'):
                fte_divisor = 90.17 if 'G' in course_code else 232.25
            elif course_code.startswith('DASC'):
                fte_divisor = 186.23

            # Calculate FTE
            fte = (ch * enrollment) / fte_divisor

            print("<tr>")
            print(f"<td>{name}</td>")
            print(f"<td>{year}</td>")
            print(f"<td>{semester}</td>")
            print(f"<td>{course_code}</td>")
            print(f"<td>{ch}</td>")
            print(f"<td>{enrollment}</td>")
            print(f"<td>{fte:.2f}</td>")
            print("</tr>")

        print("</table>")

    except Exception as e:
        print(f"<p>Error: {e}</p>")

create_fte_table()

cursor.close()
conn.close()

print("</body></html>")