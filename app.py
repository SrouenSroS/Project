from flask import Flask, render_template, request, redirect,url_for,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'locahost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user_system'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password =request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s',(email, password))
        user = cursor.fetchone()
        if user:
            if user['role'] == 'admin':
                session['loggedin'] = True
                session['userid'] = user['userid']
                session['name'] = user['name']
                session['email'] = user['email']
                mesage = 'Logged in successfully !'
                return redirect(url_for('users'))
            else:
               mesage = 'Only admin can login' 
        else:
            mesage = 'please enter correct email / password !'
    return render_template('login.html', mesage = mesage)
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('login'))
@app.route("/users", methods = ['GET','POST'])
def user():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        return render_template("users.html", users = users)
    return redirect(url_for('login'))

@app.route("/view", methods = ['GET', 'POST'])
def view():
    if 'loggedin' in session:
        viewUserid = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = % s', (viewUserid))
        user = cursor.fetchone()
        return render_template("view.html", user = user)
    return redirect(url_for('login'))

@app.route("/ password_change", methods = ['GET','POST'])
def password_change():
    mesage = ''
    if 'loggedin' in session:
        changePasswordid = request.args.get('userid')
        if request.method == 'POST' and 'password' in request.form and 'confirm_pass' in request.form and 'userid' in request.form:
            password = request.form['password']
            confirm_pass = request.form['confirm_pass']
            userid = request.form['userid']
            if not password or not confirm_pass:
                mesage = 'please fill out the form !'
            elif password != confirm_pass:
                mesage = 'Confirm_password if not equal !'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE user SET password =% s WHERE userid =% s',(password,(userid,(confirm_pass))))
                mysql.connection.commit()
                mesage = 'Password upddate !'
        elif request.method == 'POST':
            mesage = 'Please fill out the form !'
        return render_template("password_change.html",mesage =mesage, changePasswordid = changePasswordid)
    return redirect(url_for('login'))
@app.route("/delete", methods = ['GET'])
def delete():
    if 'loggedin' in session:
        deleteUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM user WHERE iuser = % s',(deleteUserId, ))
        mysql.connection.commit()
        return redirect(url_for('users'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        country = request.form['country']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            message = 'User already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not userName or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s)', (userName, email, role, country))
            mysql.connection.commit()
            message = 'You have successfully registered!'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html', message = message)
@app.route("/edit", methods=['GET', 'POST'])
def edit():
    msg = ''
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = %s', (editUserId,))
        editUser = cursor.fetchone()

        if request.method == 'POST' and 'name' in request.form and 'userid' in request.form and 'role' in request.form and 'country' in request.form:
            userName = request.form['name']
            role = request.form['role']
            country = request.form['country']
            userId = request.form['userid']

            # Validate userName to contain only alphanumeric characters
            if not re.match(r'[A-Za-z0-9]+', userName):
                msg = 'Name must contain only characters and numbers!'
            else:
                # Update user information in the database
                cursor.execute('UPDATE user SET name=%s, role=%s, country=%s WHERE userid=%s', (userName, role, country, userId))
                mysql.connection.commit()
                msg = 'User updated!'
                return redirect(url_for('users'))

        elif request.method == 'POST':
            msg = 'Please fill out the form!'

        return render_template('edit.html', msg=msg, editUser=editUser)

    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
