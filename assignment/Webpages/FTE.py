#!/usr/bin/python3
import psycopg2

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

def calculate_fte():
    """
    Calculate and display faculty FTE based on courses taught
    """
    try:
        query = """
        SELECT 
            f.honorific || ' ' || f.first || ' ' || f.last AS professor_name,
            cs.year,
            cs.semester,
            SUM(
                CASE 
                    WHEN c.prefix = 'CSCI' AND c.number >= 5000 THEN (c.CH * c.enrollment)/186.23
                    WHEN c.prefix = 'CSCI' AND c.number < 5000 THEN (c.CH * c.enrollment)/406.24
                    WHEN c.prefix = 'SENG' AND c.number >= 5000 THEN (c.CH * c.enrollment)/90.17
                    WHEN c.prefix = 'SENG' AND c.number < 5000 THEN (c.CH * c.enrollment)/232.25
                    WHEN c.prefix = 'DASC' THEN (c.CH * c.enrollment)/186.23
                    ELSE 0
                END
            ) AS fte
        FROM 
            department_course_directors dcd
        JOIN 
            dep_faculty f ON dcd.coursedirectorid = f.id
        JOIN 
            dep_course_sched cs ON dcd.prefix = cs.prefix AND dcd.number = cs.number
        JOIN 
            dep_courses c ON cs.prefix = c.prefix AND cs.number = c.number
        GROUP BY 
            f.honorific, f.first, f.last, cs.year, cs.semester
        ORDER BY 
            cs.year DESC, cs.semester, f.last, f.first
        """
        
        cursor.execute(query)
        
        print("<div class='content'>")
        print("<h2>Faculty FTE Calculations</h2>")
        
        print("<table>")
        
        # Table headers
        print("<tr>")
        headers = ['Professor Name', 'Year', 'Semester', 'FTE']
        for header in headers:
            print(f"<th>{header}</th>")
        print("</tr>")
        
        # Rows
        results = cursor.fetchall()
        for row in results:
            print("<tr>")
            # Format first three columns normally
            for i in range(3):
                print(f"<td>{row[i] if row[i] is not None else 'N/A'}</td>")
            # Format FTE with 2 decimal places
            print(f"<td>{row[3]:.2f if row[3] is not None else 'N/A'}</td>")
            print("</tr>")
        
        print("</table>")
        print("</div>")

    except Exception as e:
        print(f"<p>Error: {e}</p>")

calculate_fte()

cursor.close()
conn.close()

print("</body></html>")