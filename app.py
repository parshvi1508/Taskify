from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.exceptions import BadRequest
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'taskify_db'
DB_USER = 'taskify_user'
DB_PASSWORD = 'key_taskify'
DB_HOST = 'localhost'

def db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST
        )
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
    return conn

@app.route('/')
def index():
    conn = db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM tasks;")
        tasks = cursor.fetchall()
        conn.close()
        tasks = [{'id': row[0], 'title': row[1], 'description': row[2]} for row in tasks]
        return render_template('index.html', tasks=tasks)
    else:
        return "Error connecting to database"

@app.route('/add_task', methods=['POST'])
def add_task():
    try:
        title = request.form['title']
        description = request.form['description']
        conn = db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (title, description) VALUES (%s, %s);", (title, description))
            conn.commit()
            conn.close()
            flash('Task added successfully!', 'success')
        else:
            flash('Error connecting to database', 'error')
    except (psycopg2.Error, BadRequest) as e:
        flash(f'Error adding task: {str(e)}', 'error')
    return redirect(url_for('index'))

    
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    try:
        conn = db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id=%s;", (task_id,))
            conn.commit()
            conn.close()
            flash('Task deleted successfully!', 'success')
        else:
            flash('Error connecting to database', 'error')
    except (psycopg2.Error, BadRequest) as e:
        flash(f'Error deleting task: {str(e)}', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
