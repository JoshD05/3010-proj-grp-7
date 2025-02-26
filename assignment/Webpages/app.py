from flask import Flask, render_template_string
import psycopg2
import psycopg2.extras

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect("host=192.168.56.30 dbname=dashboard user=webuser1 password=student")
    return conn

@app.route('/')
def display_tables():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    tables = ['dep_course_sched', 'dep_faculty', 'department_course_directors', 'faculty_dates', 'faculty_standard', 'prerequisites', 'staff']
    
    all_tables_data = []
    for table in tables:
        cursor.execute(f"SELECT * FROM {table};")
        results = cursor.fetchall()
        if results:
            columns = [col.name for col in cursor.description]
            all_tables_data.append({'name': table, 'columns': columns, 'data': results})
        else:
            all_tables_data.append({'name': table, 'columns': [], 'data': []})
    
    cursor.close()
    conn.close()
    
    html_template = '''
    <html>
    <head>
        <title>Database Tables</title>
        <style>
            table, th, td {border: 1px solid black; border-collapse: collapse; padding: 5px;}
        </style>
    </head>
    <body>
        {% for table in tables %}
            <h2>{{ table.name }}</h2>
            {% if table.data %}
                <table>
                    <tr>
                        {% for col in table.columns %}
                            <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                    {% for row in table.data %}
                        <tr>
                            {% for value in row %}
                                <td>{{ value }}</td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p>No data found in {{ table.name }}</p>
            {% endif %}
        {% endfor %}
    </body>
    </html>
    '''
    
    return render_template_string(html_template, tables=all_tables_data)

if __name__ == '__main__':
    app.run(debug=True)
