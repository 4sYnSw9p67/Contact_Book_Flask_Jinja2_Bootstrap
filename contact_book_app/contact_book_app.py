from flask import Flask, redirect, url_for, request, abort, render_template, session
from datetime import timedelta
import hashlib
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)


@app.route('/')
def mainpage():
    if not 'username' in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if not 'username' in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # TODO: if form is empty, show warning
        fullname = ("{} {}".format(
            request.form['firstName'], request.form['lastName']))
        birthday = request.form['birthday']
        address = ("{}, {} {}, {}".format(
            request.form['address'], request.form['city'], request.form['zip'], request.form['country']))
        email = request.form['email']
        phone = ("{} {}".format(
            request.form['code'], request.form['phone']))
        profession = request.form['profession']
        interests = request.form['interests']
        db = sqlite3.connect('database.db')
        conn = db.cursor()
        conn.execute("INSERT INTO CONTACTS (fullname, birthday, address, email, phone, profession, interests) values(?, ?, ?, ?, ?, ?, ?)",
                     (fullname, birthday, address, email, phone, profession, interests))
        db.commit()
        db.close()
        # TODO: implement with JS and delete template
        return render_template('add-entry-success.html')
    elif request.method == 'GET':
        return render_template('add-entry.html')
    else:
        return render_template('error-page.html')


@app.route('/edit', methods=['GET', 'POST'])
def edit_entry():
    if not 'username' in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        contactbook_content = getContactBookContent()
        return render_template('edit-entry.html', contactsdb=contactbook_content)
    elif request.method == 'POST':
        selectedForUpdate = request.form.getlist('entry-to-edit')
        if not selectedForUpdate:
            contactbook_content = getContactBookContent()
            # TODO: implement a AJAX warning alert with jQuery and delete template
            return render_template('edit-entry-warning.html', contactsdb=contactbook_content)
        db = sqlite3.connect('database.db')
        conn = db.cursor()
        for contactID in selectedForUpdate:
            new_name = request.form['name_' + contactID]
            new_birthday = request.form['birthday_' + contactID]
            new_address = request.form['address_' + contactID]
            new_email = request.form['email_' + contactID]
            new_phone = request.form['phone_' + contactID]
            new_profession = request.form['profession_' + contactID]
            new_interests = request.form['interests_' + contactID]
            conn.execute("""UPDATE CONTACTS
                               SET fullname = ?, birthday = ?, address = ?, email = ?, phone = ?, profession = ?, interests = ?
                               WHERE contact_id == ?""", (new_name, new_birthday, new_address, new_email, new_phone, new_profession, new_interests, contactID))
            db.commit()
        db.close()
        contactbook_content = getContactBookContent()
        # TODO: implement a AJAX success alert with jQuery and delete template
        return render_template('edit-entry-success.html', contactsdb=contactbook_content)
    else:
        return render_template('error-page.html')


@app.route('/search', methods=['GET', 'POST'])
def search_entry():
    if not 'username' in session:
        return redirect(url_for('login'))
    contactbook_content = getContactBookContent()
    if request.method == 'GET':
        contactbook_content = getContactBookContent()
        return render_template('search.html', contactsdb=contactbook_content)
    else:
        return render_template('error-page.html')


filecontext = []
@app.route('/remove', methods=['GET', 'POST'])
def remove_entry():
    if not 'username' in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        contactbook_content = getContactBookContent()
        return render_template('remove-entry.html', contactsdb=contactbook_content)
    elif request.method == 'POST':
        selectedForRemoval = request.form.getlist('entry-to-remove')
        if not selectedForRemoval:
            contactbook_content = getContactBookContent()
            # TODO: implement a AJAX warning alert with jQuery and delete template
            return render_template('remove-entry-warning.html', contactsdb=contactbook_content)
        db = sqlite3.connect('database.db')
        conn = db.cursor()
        for contactID in selectedForRemoval:
            conn.execute(
                'DELETE FROM CONTACTS WHERE contact_id == ?', contactID)
            db.commit()
        db.close()
        contactbook_content = getContactBookContent()
        # TODO: implement a AJAX success alert with jQuery and delete template
        return render_template('remove-entry-success.html', contactsdb=contactbook_content)
    else:
        return render_template('error-page.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        db = sqlite3.connect('database.db')
        conn = db.cursor()
        emailForm = request.form['email']
        passwordForm = (hashlib.md5(
            (request.form['password']).encode())).hexdigest()
        conn.execute(
            "SELECT password from USERS where email = '%s'" % emailForm)
        passwordDB = conn.fetchone()
        db.close()
        if passwordForm == passwordDB[0]:
            session['username'] = emailForm
            return redirect(url_for('mainpage'))
        return abort(401)
    else:
        return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    global session
    session.pop('username', None)
    return redirect(url_for('login'))


def getContactBookContent():
    contactbook_content_by_id = {}
    db = sqlite3.connect('database.db')
    conn = db.cursor()
    conn.execute("""SELECT * FROM CONTACTS""")
    contacts = conn.fetchall()
    db.commit()
    db.close()
    for contact in contacts:
        contactbook_content_by_id[int(contact[0])] = contact
    return contactbook_content_by_id


if __name__ == '__main__':
    db = sqlite3.connect('database.db')
    conn = db.cursor()
    conn.execute("create table if not exists CONTACTS (contact_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, fullname text, birthday text, address text, email text, phone text, profession text, interests text)")
    conn.execute(
        "create table if not exists USERS (user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, password text NOT NULL)")
    db.commit()
    conn.execute(
        "INSERT OR IGNORE INTO USERS VALUES (1, 'admin@mail.com', '{}')".format((hashlib.md5('password'.encode())).hexdigest()))
    db.commit()
    db.close()
    app.run(port=5555, debug=True)
