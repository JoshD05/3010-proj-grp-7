#!/usr/bin/python3
import psycopg2
import psycopg2.extras
import cgi

conn = psycopg2.connect("host=localhost dbname=dashboard user=webuser1 password=student")
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
        .search-container {
            margin-bottom: 20px;
            text-align: center;
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
    form = cgi.FieldStorage()
    faculty_filter = form.getvalue('faculty', '').strip()
    year_filter = form.getvalue('year', '').strip()
    semester_filter = form.getvalue('semester', '').strip()

    try:
        query = """
        SELECT 
            cs.prefix,
            cs.number,
            c.title,
            c.ch,
            cs.enrollment,
            CASE 
                WHEN cs.prefix = 'CSCI' AND cs.number >= 5000 THEN (c.ch * cs.enrollment)/186.23
                WHEN cs.prefix = 'CSCI' AND cs.number < 5000 THEN (c.ch * cs.enrollment)/406.24
                WHEN cs.prefix = 'SENG' AND cs.number >= 5000 THEN (c.ch * cs.enrollment)/90.17
                WHEN cs.prefix = 'SENG' AND cs.number < 5000 THEN (c.ch * cs.enrollment)/232.25
                WHEN cs.prefix = 'DASC' THEN (c.ch * cs.enrollment)/186.23
                ELSE 0
            END AS fte
        FROM 
            dep_course_sched cs
        JOIN 
            dep_courses c ON cs.prefix = c.prefix AND cs.number = c.number
        WHERE 
            1=1
        """
        params = []

        if faculty_filter:
            query += " AND cs.instructor ILIKE %s"
            params.append(f'%{faculty_filter}%')
        if year_filter:
            query += " AND cs.year = %s"
            params.append(year_filter)
        if semester_filter:
            query += " AND cs.semester ILIKE %s"
            params.append(f'%{semester_filter}%')

        query += " ORDER BY cs.prefix, cs.number"
        
        cursor.execute(query, params)
        
        print("<div class='content'>")
        print("<h2>FTE Calculations</h2>")
        
        print("""
        <div class="search-container">
            <form method="get" action="fte.py">
                <input type="text" name="faculty" placeholder="Filter by faculty..." value="{}">
                <input type="text" name="year" placeholder="Filter by year..." value="{}">
                <input type="text" name="semester" placeholder="Filter by semester..." value="{}">
                <input type="submit" value="Search">
            </form>
        </div>
        """.format(faculty_filter, year_filter, semester_filter))
        
        print("<table>")
        
        # Table headers
        print("<tr>")
        headers = ['Course', 'Title', 'Credit Hours', 'Enrollment', 'FTE']
        for header in headers:
            print(f"<th>{header}</th>")
        print("</tr>")
        
        # Rows
        results = cursor.fetchall()
        total_fte = 0
        for row in results:
            print("<tr>")
            course = f"{row[0]} {row[1]}"
            print(f"<td>{course}</td>")
            print(f"<td>{row[2]}</td>")
            print(f"<td>{row[3]}</td>")
            print(f"<td>{row[4]}</td>")
            print(f"<td>{row[5]:.4f}</td>")
            total_fte += row[5]
            print("</tr>")
        
        # Total row
        print("<tr style='font-weight: bold; background-color: #e8f4f8;'>")
        print("<td colspan='4'>Total FTE</td>")
        print(f"<td>{total_fte:.4f}</td>")
        print("</tr>")
        
        print("</table>")
        print("</div>")

    except Exception as e:
        print(f"<p>Error: {e}</p>")

calculate_fte()

cursor.close()
conn.close()

print("</body></html>")
