import os
import time
import datetime
from datetime import date
from infermedica import *
import secrets
from flask import Flask
from PIL import Image
from flask import render_template, request, session, url_for, flash, redirect
import hashlib
from forms import RegistrationForm, LoginForm, ChangePassForm, UpdateUserForm
from connection import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '71a924bd8cc5c7250a4fd7314f3d2faa'

#==========================================================================
# Encrypt the password field to a 64 bit hexadecimal


def encrypt(strToHash):
    encoded = hashlib.sha256(str.encode(strToHash))
    return encoded.hexdigest()

# Return True if hashed password field matched with database


def verify(strToVerify, compareTo):
    encoded = (hashlib.sha256(str.encode(strToVerify))).hexdigest()
    return (encoded == compareTo)

# used for registratation and changing username


def getUser():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM user WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    current_user = User(data["fname"], data["lname"], username,
                        data["password"], data["gender"], data["addr_street"],
                        data["addr_city"], data["addr_state"], data["addr_zip"],
                        data["email"], data["dob"], data["period_start"],
                        data["subscribed"], data["mfaEnabled"])
    cursor.close()
    return current_user

#===========================================================================


class User():

    def __init__(self, fName, lName, username, password, gender, addr_street,
                 addr_city, addr_state, addr_zip, email, dob, period_start,
                 subscribed, mfaEnabled):
        self.firstName = fName
        self.lastName = lName
        self.username = username
        self.password = password
        self.gender = gender
        self.addr_street = addr_street
        self.addr_city = addr_city
        self.addr_state = addr_state
        self.addr_zip = addr_zip
        self.email = email
        self.dob = dob
        self.period_start = period_start
        self.subscribed = subscribed
        self.mfaEnabled = mfaEnabled


@app.route("/")
@app.route("/home")
def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))  

    return render_template('home.html')

# only accessible if logged in
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' in session:
        current_user = getUser()
        return render_template('dashboard.html', title='Dashboard', 
            current_user=current_user, isLoggedin=True)
    else:
        return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    form = RegistrationForm()
    isLoggedin = False
    if request.method == 'POST':
        if form.validate_on_submit():  
            # the function validate_on_submit() is a member function of FlaskForm
            # check that the user information doesn't already exist
            firstName = form.first_name.data
            lastName = form.last_name.data
            username = form.username.data
            gender = form.gender.data
            password_hashed = encrypt(form.password.data)
            addr_street = form.addr_street.data
            addr_city = form.addr_city.data
            addr_state = form.addr_state.data
            addr_zip = form.addr_zip.data
            email = form.email.data
            dob = form.dob.data

            # create and execute query
            cursor = conn.cursor()
            ins = 'INSERT INTO user(fname,lname,username,gender,password,addr_street,addr_city,\
            addr_state, addr_zip, email, dob, subscribed, mfaEnabled) \
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,0)'
            cursor.execute(ins, (firstName, lastName, username, gender, 
                password_hashed, addr_street, addr_city, addr_state, addr_zip, 
                email, dob))
            # save changes to database
            conn.commit()
            cursor.close()
            # notify the user of successful creation of account
            flash(f'Account Created for {form.username.data}! You Can Now Log In!', 'success')  
            return redirect(url_for('login'))
        else:
            flash('Please Check the Errors Below.', 'danger')
    return render_template('register.html', title='Register', form=form, isLoggedin=isLoggedin)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():  # no errors when inputting data and no empty fields
        # fetch data from the form
        username = form.username.data
        password_to_check = form.password.data

        cursor = conn.cursor()
        # execute query
        query = cursor.execute("SELECT * FROM user WHERE username = %s", username)

        if(query > 0):  # sts in the database
            # get stored hashed password
            data = cursor.fetchone()
            password_correct = data['password']
            # Compare the passwords
            if verify(password_to_check, password_correct):
                # Valid User
                session['logged_in'] = True
                session['username'] = username
                cursor.close()
                flash("You Have Successfully Logged In!", "success")
                return redirect(url_for("dashboard"))
            else:  # passwords do not match

                flash('Login Unsuccessful. Please Check Username and Password.', 'danger')
                # we don't want to flash the password being incorrect, 
                # but just highliight it and display it as an error underneath the password field

            # close connection
            cursor.close()
        else:  # no results with the specified username in the database
            flash('Login Unsuccessful. No Account Exists With That Username.', 'danger')
            cursor.close()

    return render_template('login.html', title='Login', form=form)


@app.route("/changePassword", methods=['GET', 'POST'])
def changePassword():
    # should be logged in already
    # user enters current password
    if 'logged_in' in session:
        form = ChangePassForm()
        if form.validate_on_submit():
            # get information from form
            currentPass = form.currentPass.data
            newPass = form.newPassword.data
            # create cursor
            cursor = conn.cursor()
            # verify current password
            username = session['username']
            query = 'SELECT * FROM Person WHERE username = %s'
            cursor.execute(query, (username))
            # query must return something since the user is already logged in
            data = cursor.fetchone()
            password_correct = data['password']
            if verify(currentPass, password_correct):

                # passwords match, update current password
                newPassHashed = encrypt(newPass)
                if currentPass == newPassHashed:
                    flash('Your new password must be different from your current password', 'warning')
                    return redirect(url_for('changePassword'))
                # can now update the password to database
                query = 'UPDATE Person SET password=%s WHERE username=%s'
                cursor.execute(query, (newPassHashed, username))
                conn.commit()
                cursor.close()
                session.clear()  # must login again
                flash('Your Password Has Been Updated', 'success')
                return redirect(url_for('login'))
            else:
                cursor.close()
                flash('Incorrect Password, Could Not Change Password', 'danger')
                return redirect(url_for('login'))
        return render_template('changePassword', title='Change Password', form=form, isLoggedin=True)
    return redirect(url_for('home'))


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if 'logged_in' in session:
        session.clear()
        flash('You Have Been Successfully Logged Out.', 'success')
    return redirect(url_for('home'))


@app.route("/settings")
def settings():
    if 'logged_in' in session:
        render_template('settings.html', title='Settings')
    else:
        return redirect(url_for('home'))

@app.route("/report")
def report():
    if 'logged_in' in session:
        return render_template('report.html', title='Report', isLoggedin=True)
    else:
        return redirect(url_for('home'))

@app.route("/uploadRecords")
def uploadRecords():
    if 'logged_in' in session:
        return render_template('uploadRecords.html', title='Upload Medical Records', 
            isLoggedin=True)
    else:
        return redirect(url_for('home'))

@app.route("/viewRecords")
def viewRecords():
    if 'logged_in' in session:
        # fetch the records for the user 
        current_user = getUser()
        cursor = conn.cursor()

        return render_template('viewRecords.html', title='View Medical Records', isLoggedin=True)
    else:
        return redirect(url_for('home'))

@app.route("/insertData") # testing purposes 
def insertData():
    if 'logged_in' in session:
        current_user = getUser()
        if request.form:
            username = current_user.username
            symptoms = request.form['symptoms']



@app.route("/shareRecords")
def shareRecords():
    if 'logged_in' in session:
        return render_template('shareRecords.html', title='Share Medical Records', isLoggedin=True)
    else:
        return redirect(url_for('home'))


@app.route("/resources")
def resources():
    if 'logged_in' in session:
        return render_template('resources.html', title='Health Resources', isLoggedin=True)
    else:
        return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
def account():
    if 'logged_in' in session:
        current_user = getUser()
        return render_template('account.html', title='Account', isLoggedin=True, 
            current_user=current_user)
    else:
        return redirect(url_for('home'))

@app.route("/diagnosis")
def diagnosis():
    if 'logged_in' in session:
        return render_template('diagnosis.html', title='Diagnosis & Treatment', isLoggedin=True)
    else:
        return redirect(url_for('home'))

    
def calcAge(birth,today):
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

def stringFromSympt(sympt):
    returnStr = ""
    for i in range(len(sympt)):
        if i == (len(sympt)-1):
            returnStr += str(sympt[i])
        else:
            returnStr = returnStr + str(sympt[i]) + ", "
            returnStr += " "
    return returnStr

#Displays the results of the diagnosis
@app.route('/diagnosisReport', methods=['GET', 'POST'])
def diagnosisReport():
    api= infermedica_api.API(app_id='52457f85', app_key='95f03f5398a3b0358795540117d4f376')
    symptDesc = request.form["Symptoms"]
    currUser = getUser()
    currAge = calcAge(currUser.dob,date.today())
    gendAge = (currUser.gender.lower(),str(currAge))
    req = diagnose(api,gendAge,parser(api,str(symptDesc)))
    if req == None:
        return render_template('diagnosis.html', title='Diagnosis & Treatment', 
            isLoggedin=True, reattempt="No symptoms, please provide further details")
    lstIll = conditions(req[0])
    lstSympt = req[1]
    strSympt = stringFromSympt(lstSympt)
    if (lstIll[0] == "" and lstIll[1] == "" and lstIll[2] == ""):
        #if no conditions were found, more symptoms are needed
        return render_template('diagnosis.html', title='Diagnosis & Treatment', 
            isLoggedin=True, reattempt="No illnesses were discovered, please enter more symptoms")
    cursor = conn.cursor()
    ins = 'INSERT INTO diagnosis(username,symptoms,illness,illness2,illness3) VALUES(%s,%s,%s,%s,%s)'
    cursor.execute(ins, (currUser.username, strSympt, lstIll[0], lstIll[1], lstIll[2]))
    query = cursor.execute("SELECT * FROM treatment WHERE illness = %s", lstIll[0])
    data = cursor.fetchone()
    #The corresponding Illness to Treatment
    #data[remedy] will return the corresponding treatment
    strRemedy = "No natural treatment for the above diagnosis exists in our database\
     at this moment. Please consult your primary care physician or check our Health Resources \
     page for further information. Thank you."
    if data:
        strRemedy = data["remedy"]
        conn.commit()
        cursor.close()
    return render_template('results.html', name = currUser.firstName, gender = currUser.gender, age = currAge, 
        diagOne= lstIll[0], diagTwo = lstIll[1], diagThree = lstIll[2], treatments = strRemedy)

def save_picture(form_picture):

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilePics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_picture2(form_picture):

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/posts', picture_fn)
    output_size = (400, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account/edit", methods=['GET', 'POST'])
def update():
    if 'logged_in' in session:
        form = UpdateUserForm()
        current_user = getUser()
        if request.method == 'GET':  # fill in form with information in database
            form.first_name.data = current_user.firstName
            form.last_name.data = current_user.lastName
            form.username.data = current_user.username
            form.gender.data = current_user.gender
            form.email.data = current_user.email
            form.addr_street.data = current_user.addr_street
            form.addr_city.data = current_user.addr_city
            form.addr_state.data = current_user.addr_state
            form.addr_zip.data = current_user.addr_zip
        elif request.method == 'POST':
            if form.validate_on_submit():
                currentUsername = session['username']
                firstName = form.first_name.data
                lastName = form.last_name.data
                username = form.username.data
                gender = form.gender.data
                email = form.email.data
                addr_street = form.addr_street.data
                addr_city = form.addr_city.data
                addr_state = form.addr_state.data
                addr_zip = form.addr_zip.data
                cursor = conn.cursor()
                update = 'UPDATE user SET fName=%s, lName=%s, username=%s, gender=%s, email=%s, \
                    addr_street=%s, addr_city=%s, addr_state=%s, addr_zip=%s WHERE username=%s'
                cursor.execute(update, (firstName, lastName, username, gender, email, addr_street,
                    addr_city, addr_state, addr_zip, currentUsername))
                session['username'] = username
                conn.commit()
                cursor.close()
                flash('Your Account Has Been Successfully Updated!', 'success')  
                return redirect(url_for('update'))
            else:
                flash('Please Check the Errors Below.', 'danger')

        return render_template('edit.html', title='Edit Account', form=form, 
            current_user=current_user, isLoggedin=True)
    else:
        return redirect(url_for('home'))


# #==================================================================================


if __name__ == "__main__":
    app.run(debug=True)
