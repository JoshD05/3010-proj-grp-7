#!/usr/bin/python3
import psycopg2
import psycopg2.extras
import cgi
import cgitb
cgitb.enable()

class Faculty:
    def __init__(self, id, first_name, last_name, email, title, department, phone, office, research_interests):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.title = title
        self.department = department
        self.phone = phone
        self.office = office
        self.research_interests = research_interests

    def to_html_row(self):
        """
        Generate an HTML table row for the faculty member
        """
        return f"""
        <tr>
            <td>{self.first_name} {self.last_name}</td>
            <td>{self.title}</td>
            <td>{self.department}</td>
            <td>{self.email}</td>
            <td>{self.phone}</td>
            <td>{self.office}</td>
            <td>{self.research_interests or 'N/A'}</td>
        </tr>
        """

def connect_to_database():
    """
    Establish a connection to the PostgreSQL database
    """
    try:
        conn = psycopg2.connect(
            host="192.168.56.30", 
            dbname="dashboard", 
            user="webuser1", 
            password="student"
        )
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Content-type: text/html\n\n")
        print("<html><body>")
        print(f"<h1>Database Connection Error</h1>")
        print(f"<p>Error: {error}</p>")
        print("</body></html>")
        return None

def get_all_faculty():
    """
    Retrieve all faculty members from the database
    """
    conn = connect_to_database()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT id, first_name, last_name, email, title, 
                   department, phone, office, research_interests 
            FROM faculty_standard
        """)
        faculty_list = []
        for row in cursor.fetchall():
            faculty_list.append(Faculty(
                row['id'], row['first_name'], row['last_name'], 
                row['email'], row['title'], row['department'], 
                row['phone'], row['office'], row['research_interests']
            ))
        
        cursor.close()
        conn.close()
        return faculty_list
    except (Exception, psycopg2.Error) as error:
        print("Content-type: text/html\n\n")
        print("<html><body>")
        print(f"<h1>Database Query Error</h1>")
        print(f"<p>Error: {error}</p>")
        print("</body></html>")
        return []

def search_faculty(search_term):
    """
    Search for faculty members based on a search term
    """
    conn = connect_to_database()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Search across multiple fields
        cursor.execute("""
            SELECT id, first_name, last_name, email, title, 
                   department, phone, office, research_interests 
            FROM faculty_standard
            WHERE lower(first_name) LIKE lower(%s) OR 
                  lower(last_name) LIKE lower(%s) OR 
                  lower(department) LIKE lower(%s) OR 
                  lower(research_interests) LIKE lower(%s)
        """, (f'%{search_term}%', f'%{search_term}%', 
               f'%{search_term}%', f'%{search_term}%'))
        
        faculty_list = []
        for row in cursor.fetchall():
            faculty_list.append(Faculty(
                row['id'], row['first_name'], row['last_name'], 
                row['email'], row['title'], row['department'], 
                row['phone'], row['office'], row['research_interests']
            ))
        
        cursor.close()
        conn.close()
        return faculty_list
    except (Exception, psycopg2.Error) as error:
        print("Content-type: text/html\n\n")
        print("<html><body>")
        print(f"<h1>Database Search Error</h1>")
        print(f"<p>Error: {error}</p>")
        print("</body></html>")
        return []

def print_html_header():
    """
    Print the HTML header with navigation and styles
    """
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
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
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

def print_faculty_table(faculty_list):
    """
    Print the faculty table 
    """
    print("""
    <div class="search-container">
        <form method="get" action="faculty.py">
            <input type="text" name="search" placeholder="Search faculty...">
            <input type="submit" value="Search">
        </form>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Title</th>
                <th>Department</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Office</th>
                <th>Research Interests</th>
            </tr>
        </thead>
        <tbody>
    """)
    
    if not faculty_list:
        print("<tr><td colspan='7'>No faculty members found.</td></tr>")
    else:
        for faculty in faculty_list:
            print(faculty.to_html_row())
    
    print("""
        </tbody>
    </table>
    """)

def main():
    """
    Main function to handle faculty page display and search
    """
    # Parse form data
    form = cgi.FieldStorage()
    
    # Print HTML header
    print_html_header()
    
    # Check if there's a search term
    search_term = form.getvalue('search')
    
    if search_term:
        # Perform search
        faculty_list = search_faculty(search_term)
        print(f"<h2>Search Results for '{search_term}'</h2>")
    else:
        # Get all faculty if no search term
        faculty_list = get_all_faculty()
        print("<h2>Faculty Directory</h2>")
    
    # Print faculty table
    print_faculty_table(faculty_list)
    
    print("</body></html>")

# Run the main function
if __name__ == "__main__":
    main()