#!/usr/bin/python3
import psycopg2
import psycopg2.extras
import cgi

class Faculty:
    def __init__(self, name, department, email, phone, office):
        self.name = name
        self.department = department
        self.email = email
        self.phone = phone
        self.office = office
    
    def to_html_row(self):
        return f"""
        <tr>
            <td>{self.name}</td>
            <td>{self.department}</td>
            <td>{self.email}</td>
            <td>{self.phone}</td>
            <td>{self.office}</td>
        </tr>"""

# Database connection
conn = psycopg2.connect("host=192.168.56.30 dbname=dashboard user=webuser1 password=student")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

print("Content-type: text/html\n\n")
print("""
<html>
<head>
    <title>Faculty Search</title>
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
        .search-box {
            margin: 20px;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="csdashboard.py">Home</a>
        <a href="faculty.py">Faculty</a>
    </div>
    <div class="search-box">
        <form method="GET" action="faculty.py">
            <input type="text" name="search" placeholder="Search faculty by name..." 
                   value="{}" style="padding: 8px; width: 300px;">
            <input type="submit" value="Search" style="padding: 8px 15px;">
        </form>
    </div>
    <table>
        <tr>
            <th>Name</th>
            <th>Department</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Office</th>
        </tr>
""".format(cgi.FieldStorage().getvalue('search', '')))

# search
form = cgi.FieldStorage()
search_term = form.getvalue('search', '')

query = """
    SELECT name, department, email, phone, office 
    FROM dep_faculty 
    WHERE name ILIKE %s
    ORDER BY name
"""
cursor.execute(query, (f'%{search_term}%',))

for record in cursor.fetchall():
    faculty = Faculty(
        name=record['name'],
        department=record['department'],
        email=record['email'],
        phone=record['phone'],
        office=record['office']
    )
    print(faculty.to_html_row())

print("""
    </table>
</body>
</html>
""")

cursor.close()
conn.close()
