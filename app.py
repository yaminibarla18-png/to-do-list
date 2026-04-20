from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# 🔹 Create DB
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        completed INTEGER
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# 🔐 Register
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username,password) VALUES(?,?)",(username,password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# 🔐 Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/')
    
    return render_template('login.html')

# 🔓 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# 🏠 Home
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id=?",(session['user_id'],))
    tasks = cur.fetchall()
    conn.close()

    return render_template('index.html', tasks=tasks)

# ➕ Add Task
@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks(user_id,title,completed) VALUES(?,?,0)",
                    (session['user_id'], title))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add.html')

# ✅ Complete
@app.route('/complete/<int:id>')
def complete(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET completed=1 WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect('/')

# ❌ Delete
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)