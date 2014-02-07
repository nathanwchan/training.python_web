from flask import Flask
from flask import g
from flask import render_template
from flask import abort
from flask import request
from flask import url_for
from flask import redirect
from flask import session
from flask import flash
import sqlite3
from contextlib import closing

app = Flask(__name__)

app.config.from_pyfile('microblog.cfg')


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_database_connection():
    db = getattr(g, 'db', None)
    if db is None:
        g.db = db = connect_db()
    return db


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def write_entry(title, text):
    con = get_database_connection()
    con.execute('insert into entries (title, text) values (?, ?)',
                [title, text])
    con.commit()


def get_all_entries():
    con = get_database_connection()
    cur = con.execute('SELECT title, text FROM entries ORDER BY id DESC')
    return [dict(title=row[0], text=row[1]) for row in cur.fetchall()]

def get_all_users():
    con = get_database_connection()
    cur = con.execute('SELECT username, password FROM users ORDER BY id DESC')
    return [dict(username=row[0], password=row[1]) for row in cur.fetchall()]

def user_is_logged_in(username, password, register_user=False):
    con = get_database_connection()
    cur = con.execute('SELECT username, password FROM users WHERE username = ?',
            [username])
    data = cur.fetchall()
    if len(data) > 0: # username exists in DB
        if data[0][1] == password: # password matches, login succeeded
            session['username'] = username
            session['password'] = password
            flash('You are logged in')
            return True
        # username exists in DB, but password doesn't match
        flash('Incorrect password')
        return False
    elif register_user: # username doesn't exist in the DB, create the user
        flash('Welcome, %s' % username)
        return create_login(username, password)

def create_login(username, password):
    con = get_database_connection()
    con.execute('insert into users (username, password) values (?, ?)',
                [username, password])
    con.commit()
    session['username'] = username
    session['password'] = password
    return True

@app.route('/')
def attempt_login():
    username = session.get('username', 'username_that_does_not_exist')
    password = session.get('password', 'password_that_does_not_exist')
    print 'username [%s] password [%s]' % (username, password)
    if user_is_logged_in(username, password):
        return redirect(url_for('show_entries'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['username'] = None
    session['password'] = None
    flash('You have logged out')
    return redirect(url_for('login'))

@app.route('/entries')
def show_entries():
    entries = get_all_entries()
    users = get_all_users()
    return render_template('show_entries.html',
            entries=entries,
            users=users,
            current_username=session.get('username', 'ERROR'))


@app.route('/login', methods=['POST'])
def login_post():
    try:
        if user_is_logged_in(request.form['username'], request.form['password'],
                register_user=True):
            return redirect(url_for('show_entries'))
    except sqlite3.Error as e:
        flash('Error: %s' % e)
    return render_template('login.html', password_error=True)


@app.route('/add', methods=['POST'])
def add_entry():
    try:
        write_entry(request.form['title'], request.form['text'])
        flash('New entry posted')
    except sqlite3.Error as e:
        flash('Error: %s' % e)
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(debug=True)
