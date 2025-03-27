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
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 5px;
            margin-bottom: 20px;
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

def create_faculty_table():
    """
    Create a detailed view of the faculty table with search capability
    """
    # Check if there's a search parameter in the URL
    import os
    search_term = os.environ.get('QUERY_STRING', '').replace('search=', '').strip()

    try:
        # Prepare the query based on whether there's a search term
        if search_term:
            # Search across all columns
            query = """
            SELECT * FROM dep_faculty 
            WHERE 
                cast(id as text) ILIKE %s OR 
                cast(honorific as text) ILIKE %s OR
                cast(first as text) ILIKE %s OR 
                cast(last as text) ILIKE %s OR
                cast(email as text) ILIKE %s OR 
                cast(rank as text) ILIKE %s OR 
                cast(research_interests as text) ILIKE %s
            """
            search_param = f'%{search_term}%'
            cursor.execute(query, (search_param, search_param, search_param, search_param, search_param, search_param, search_param))
            print(f"<h2>Search Results for '{search_term}'</h2>")
        else:
            # If no search term, fetch all faculty
            cursor.execute("SELECT * FROM dep_faculty")
            print("<h2>Faculty Directory</h2>")

        # Add search form
        print("""
        <div class="search-container">
            <form method="get" action="faculty.py">
                <input type="text" name="search" placeholder="Search faculty..." value="{0}">
                <input type="submit" value="Search">
            </form>
        </div>
        """.format(search_term))

        # Fetch results
        results = cursor.fetchall()

        # Print table
        print("<table>")
        
        # Print headers
        if results:
            print("<tr>")
            for col in cursor.description:
                print(f"<th>{col.name}</th>")
            print("</tr>")

            # Print rows
            for row in results:
                print("<tr>")
                for value in row:
                    print(f"<td>{value if value is not None else 'N/A'}</td>")
                print("</tr>")
        else:
            # If no results found
            print(f"<tr><td colspan='{len(cursor.description)}'>No faculty members found.</td></tr>")
        
        print("</table>")

    except Exception as e:
        print(f"<p>Error: {e}</p>")

# Display faculty table
create_faculty_table()

# Close connection
cursor.close()
conn.close()

print("</body></html>")