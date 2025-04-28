#!/usr/bin/python3
import psycopg2
import psycopg2.extras
import cgi

class FTECalculator:
    @staticmethod
    def calculate_fte(prefix, number, ch, enrollment):
        if prefix == 'CSCI':
            if number >= 5000:
                return (ch * enrollment) / 186.23
            else:
                return (ch * enrollment) / 406.24
        elif prefix == 'SENG':
            if number >= 5000:
                return (ch * enrollment) / 90.17
            else:
                return (ch * enrollment) / 232.25
        elif prefix == 'DASC':
            return (ch * enrollment) / 186.23
        return 0

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
            f.honorific || ' ' || f.first || ' ' || f.last AS faculty_name,
            cs.year,
            cs.semester,
            cs.prefix,
            cs.number,
            c.ch,
            cs.enrollment
        FROM 
            dep_course_sched cs
        JOIN 
            dep_courses c ON cs.prefix = c.prefix AND cs.number = c.number
        JOIN 
            dep_faculty f ON cs.instructor::integer = f.id
        WHERE 
            1=1
        """
        params = []

        if faculty_filter:
            query += " AND (f.honorific || ' ' || f.first || ' ' || f.last) ILIKE %s"
            params.append(f'%{faculty_filter}%')
        if year_filter:
            query += " AND cs.year = %s"
            params.append(year_filter)
        if semester_filter:
            query += " AND cs.semester ILIKE %s"
            params.append(f'%{semester_filter}%')

        query += " ORDER BY cs.year DESC, cs.semester, f.last, f.first"
        
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
        headers = ['Faculty', 'Year', 'Semester', 'FTE']
        for header in headers:
            print(f"<th>{header}</th>")
        print("</tr>")
        
        # Process results
        results = cursor.fetchall()
        processed_results = {}
        for row in results:
            faculty_name = row[0]
            year = row[1]
            semester = row[2]
            prefix = row[3]
            number = row[4]
            ch = row[5]
            enrollment = row[6]
            
            key = (faculty_name, year, semester)
            if key not in processed_results:
                processed_results[key] = 0
            
            processed_results[key] += FTECalculator.calculate_fte(prefix, number, ch, enrollment)
        
        # Display results
        total_fte = 0
        for (faculty_name, year, semester), fte in processed_results.items():
            print("<tr>")
            print(f"<td>{faculty_name if faculty_name is not None else 'N/A'}</td>")
            print(f"<td>{year if year is not None else 'N/A'}</td>")
            print(f"<td>{semester if semester is not None else 'N/A'}</td>")
            print(f"<td>{fte:.4f}</td>")
            total_fte += fte
            print("</tr>")
        
        # Total row
        print("<tr style='font-weight: bold; background-color: #e8f4f8;'>")
        print("<td colspan='3'>Total FTE</td>")
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
