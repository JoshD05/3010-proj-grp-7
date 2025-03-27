#!/usr/bin/python3
import psycopg2
import psycopg2.extras

class Faculty:
    def __init__(self, *args):
        """
        Initialize with a variable number of arguments based on the actual database columns
        """
        self.attributes = list(args)

    def to_html_row(self):
        """
        Generate an HTML table row with all attributes
        """
        return "<tr>" + "".join(f"<td>{str(attr) if attr is not None else 'N/A'}</td>" for attr in self.attributes) + "</tr>"

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

def get_table_columns(table_name):
    """
    Retrieve column names for a specific table
    """
    conn = connect_to_database()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 0;")
        column_names = [desc.name for desc in cursor.description]
        cursor.close()
        conn.close()
        return column_names
    except (Exception, psycopg2.Error) as error:
        print("Content-type: text/html\n\n")
        print("<html><body>")
        print(f"<h1>Database Column Error for {table_name}</h1>")
        print(f"<p>Error: {error}</p>")
        print("</body></html>")
        return []

def get_faculty_data(table_name='dep_faculty'):
    """
    Retrieve faculty data from the specified table
    """
    conn = connect_to_database()
    if not conn:
        return [], []

    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name};")
        column_names = [desc.name for desc in cursor.description]
        results = cursor.fetchall()
        
        faculty_list = [Faculty(*row) for row in results]
        
        cursor.close()
        conn.close()
        return column_names, faculty_list
    except (Exception, psycopg2.Error) as error:
        print("Content-type: text/html\n\n")
        print("<html><body>")
        print(f"<h1>Database Query Error</h1>")
        print(f"<p>Error: {error}</p>")
        print("</body></html>")
        return [], []

def search_faculty(table_name, search_term):
    """
    Search for faculty members based on a search term
    """
    conn = connect_to_database()
    if not conn:
        return [], []

    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 0;")
        column_names = [desc.name for desc in cursor.description]
        
        # dynamic search condition
        search_conditions = " OR ".join([f"CAST({col} AS TEXT) ILIKE %s" for col in column_names])
        search_params = [f"%{search_term}%"] * len(column_names)
        
        # Execute search query
        cursor.execute(f"""
            SELECT * FROM {table_name}
            WHERE {search_conditions}
        """, search_params)
        
        results = cursor.fetchall()
        faculty_list = [Faculty(*row) for row in results]
        
        cursor.close()
        conn.close()
        return column_names, faculty_list
    except (Exception, psycopg2.Error) as error:
        print("Content-type: text/html\n\n")
        print("<html><body>")
        print(f"<h1>Database Search Error</h1>")
        print(f"<p>Error: {error}</p>")
        print("</body></html>")
        return [], []

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

def print_faculty_table(column_names, faculty_list):
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
    """)
    
    for col in column_names:
        print(f"<th>{col}</th>")
    
    print("""
            </tr>
        </thead>
        <tbody>
    """)
    
    if not faculty_list:
        print(f"<tr><td colspan='{len(column_names)}'>No faculty members found.</td></tr>")
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
    form = cgi.FieldStorage()
    
    print_html_header()
    
    table_name = 'dep_faculty'
    
    search_term = form.getvalue('search')
    
    if search_term:
        column_names, faculty_list = search_faculty(table_name, search_term)
        print(f"<h2>Search Results for '{search_term}'</h2>")
    else:
        column_names, faculty_list = get_faculty_data(table_name)
        print("<h2>Faculty Directory</h2>")
    
    print_faculty_table(column_names, faculty_list)
    
    print("</body></html>")

if __name__ == "__main__":
    main()