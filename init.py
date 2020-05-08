import os
import time
import os
import datetime
from datetime import date
from infermedica import *
import secrets
import pdfkit    # library to generate pdf 
from flask import Flask
from flask import render_template, request, session, url_for, flash, redirect, make_response
import hashlib
from forms import RegistrationForm, LoginForm, UpdateUserForm, UploadDocumentForm, ShareRecordsForm
from connection import *
# email libraries and dependencies
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

app = Flask(__name__)
app.config['SECRET_KEY'] = '71a924bd8cc5c7250a4fd7314f3d2faa'

UPLOAD_DIR = os.path.join(os.getcwd(), "static/uploads")
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
                        data["password"], data["sex"], data["addr_street"],
                        data["addr_city"], data["addr_state"], data["addr_zip"],
                        data["email"], data["dob"], data["period_start"],
                        data["subscribed"], data["mfaEnabled"])
    cursor.close()
    return current_user

#===========================================================================


class User():

    def __init__(self, fName, lName, username, password, sex, addr_street,
                 addr_city, addr_state, addr_zip, email, dob, period_start,
                 subscribed, mfaEnabled):
        self.firstName = fName
        self.lastName = lName
        self.username = username
        self.password = password
        self.sex = sex
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
        return render_template('dashboard.html', title='Dashboard', current_user=current_user, isLoggedin=True)
    else:
        return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    form = RegistrationForm()
    isLoggedin = False
    if request.method == 'POST':
        if form.validate_on_submit():  # the function validate_on_submit() is a member function of FlaskForm
            # check that the user information doesn't already exist
            firstName = form.first_name.data
            lastName = form.last_name.data
            username = form.username.data
            sex = form.sex.data
            password_hashed = encrypt(form.password.data)
            addr_street = form.addr_street.data
            addr_city = form.addr_city.data
            addr_state = form.addr_state.data
            addr_zip = form.addr_zip.data
            email = form.email.data
            dob = form.dob.data

            # create and execute query
            cursor = conn.cursor()
            ins = 'INSERT INTO user(fname,lname,username,sex,password,addr_street,addr_city,\
            addr_state, addr_zip, email, dob, subscribed, mfaEnabled) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,0)'
            cursor.execute(ins, (firstName, lastName, username, sex, password_hashed, addr_street, addr_city, addr_state, addr_zip, email, dob))
            # save changes to database
            conn.commit()
            cursor.close()
            # notify the user of successful creation of account
            flash(f'Account created for {form.username.data}! You can now log in!', 'success')  
            return redirect(url_for('login'))
        else:
            flash('Please check the errors below.', 'danger')
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
                flash("You have successfully logged in!", "success")
                return redirect(url_for("dashboard"))
            else:  # passwords do not match

                flash('Login unsuccessful. Please check uername and password.', 'danger')
                # we don't want to flash the password being incorrect, but just highliight it and display it as an error underneath the password field

            # close connection
            cursor.close()
        else:  # no results with the specified username in the database
            flash('Login unsuccessful. No account exists with that username.', 'danger')
            cursor.close()

    return render_template('login.html', title='Login', form=form)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if 'logged_in' in session:
        session.clear()
        flash('You have been successfully logged out.', 'success')
    return redirect(url_for('home'))


@app.route("/diagnosisHistory", methods=['GET', 'POST'])
def diagnosisHistory():
    if 'logged_in' in session:
        current_user = getUser()
        username = current_user.username
        cursor = conn.cursor()
        if request.method == 'POST': # delete the selected recordID
            recordID = request.form['recordID']
            delete = 'DELETE FROM diagnosis WHERE recordID = %s'
            cursor.execute(delete, (recordID))
            conn.commit()
            flash('The selected record has been removed.', 'success')
            return redirect(url_for('diagnosisHistory'))
        # fetch the records from diagnosis 
        query = 'SELECT recordID, symptoms, illness, illness2, illness3, timestamp FROM diagnosis WHERE username=%s'
        cursor.execute(query, (username))
        records = cursor.fetchall()
        # parse data 
        for record in records: # each record is a row {}
            symptoms = record['symptoms'] # ; separated
            record['symptoms'] = symptoms.split(';')
            query = 'SELECT remedy FROM treatment WHERE illness=%s'
            cursor.execute(query, (record['illness']))
            data = cursor.fetchone()
            if (data): # a treatment exists 
                record['treatments'] = []
                treatments = data['remedy'].split(';')
                for result in treatments:
                    treatment = {}
                    resultSplit = result.split(':')
                    treatment['treatment'] = resultSplit[0]
                    if len(resultSplit) == 2:
                        treatment['options'] = resultSplit[1].split(',')
                    record['treatments'].append(treatment)
            else: # a treatment does not exist 
                record['none'] = True
        return render_template('diagnosisHistory.html', title='Diagnosis History', isLoggedin=True, records=records)
    else:
        return redirect(url_for('home'))

@app.route("/generateReport", methods=['GET', 'POST'])
def generateReport():
    if 'logged_in' in session:
        if request.form:
            current_user = getUser()
            currAge = calcAge(current_user.dob,date.today())
            user = {}
            user['firstName'] = current_user.firstName
            user['lastName'] = current_user.lastName
            user['age'] = currAge
            user['sex'] = current_user.sex
            ts = time.time()
            current_time = datetime.datetime.fromtimestamp(ts).strftime("%d/%m/%Y %I:%M:%S %p") # current time 
            recordIds = request.form.getlist("checked") # contains the ids of chosen records
            chosenRecords = []
            cursor = conn.cursor()
            for recordID in recordIds:
                query = 'SELECT symptoms, illness, illness2, illness3, timestamp FROM diagnosis WHERE recordID=%s'
                cursor.execute(query, (recordID)) # will return something
                diagnosis = cursor.fetchone()
                symptoms = diagnosis['symptoms'] # ; separated
                diagnosis['symptoms'] = symptoms.split(';')
                query2 = 'SELECT remedy FROM treatment WHERE illness=%s'
                cursor.execute(query2, (diagnosis['illness']))
                data = cursor.fetchone()
                if (data): # a treatment exists 
                    diagnosis['treatments'] = []
                    treatments = data['remedy'].split(';')
                    for result in treatments:
                        treatment = {}
                        resultSplit = result.split(':')
                        treatment['treatment'] = resultSplit[0]
                        if len(resultSplit) == 2:
                            treatment['options'] = resultSplit[1].split(',')
                        diagnosis['treatments'].append(treatment)
                else: # a treatment does not exist 
                    diagnosis['none'] = True
                chosenRecords.append(diagnosis)

            total = len(chosenRecords)
            rendered = render_template('reportTemplate.html', records=chosenRecords, current_time=current_time, total=total, user=user)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=report.pdf'
            return response 
    else:
        return redirect(url_for('home'))

@app.route("/uploadRecords", methods=['GET', 'POST'])
def uploadRecords():
    if 'logged_in' in session:
        form = UploadDocumentForm()
        current_user = getUser()
        if form.validate_on_submit():
            filename = form.document.data.filename
            filepath = os.path.join(UPLOAD_DIR, filename)
            form.document.data.save(filepath)
            description = form.description.data
            cursor = conn.cursor()
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            ins = 'INSERT INTO document(documentOwner, filePath, description,timestamp) VALUES(%s, %s, %s, %s)'
            cursor.execute(ins, (current_user.username, filename, description, timestamp))
            conn.commit()
            cursor.close()
            flash('Your document has been successfully uploaded!', 'success')
            return redirect(url_for('uploadRecords'))
        return render_template('uploadRecords.html', title='Upload Medical Records', isLoggedin=True, form=form)
    else:
        return redirect(url_for('home'))

@app.route("/viewRecords", methods=['GET', 'POST']) # attachments of user uploaded test results etc. 
def viewRecords():
    if 'logged_in' in session:
        current_user = getUser()
        username = current_user.username
        cursor = conn.cursor()
        if request.method == 'POST': # delete the selected document ID
            documentID = request.form['documentID']
            delete = 'DELETE FROM document WHERE documentID = %s'
            cursor.execute(delete, (documentID))
            conn.commit()
            return redirect(url_for('viewRecords'))
        # fetch documents for the user 
        query = 'SELECT documentID, filePath, description, timestamp FROM document WHERE documentOwner = %s'
        cursor.execute(query, (username))
        data = cursor.fetchall()
        cursor.close()
        return render_template('viewRecords.html', title='View Medical Records', isLoggedin=True, records=data)
    else:
        return redirect(url_for('home'))
 
def getFileRecords(username):
    files = []
    cursor = conn.cursor()
    query = 'SELECT documentID, filePath, description, timestamp FROM document WHERE documentOwner = %s'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    cursor.close()
    for i in range(len(data)):
        result = data[i].get('filePath') + ', ' + data[i].get('description')
        files.append((data[i].get('filePath'), result))
    return files



@app.route("/shareRecords", methods=['GET', 'POST'])
def shareRecords():
    if 'logged_in' in session:
        form = ShareRecordsForm()
        current_user = getUser()
        username = current_user.username
        files = getFileRecords(username)
        has_records = False
        if len(files) > 0:
            has_records = True
        form.select.choices = files
        
        if request.method == 'GET':  # fill in form with information in database
            form.user_email.data = current_user.email

        if form.validate_on_submit():

            receiver_address = form.recipient.data
            user_email = form.user_email.data
            user_password = form.user_password.data
            subject = form.subject.data
            body = form.body.data

            fileToSend = form.select.data
            filePath = UPLOAD_DIR + '/' + fileToSend
            msg = MIMEMultipart()
            msg['From'] = user_email
            msg['To'] = receiver_address
            msg['Subject'] = subject
            msg['Date'] = formatdate(localtime=True)
            msg.attach(MIMEText(body))
            part = MIMEBase('application', "octet-stream")
            with open(filePath, 'rb') as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 
                            'attachment; filename="{}"'.format(fileToSend))
            msg.attach(part)
            smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            try:
                smtp.login(user_email, user_password)
            except smtplib.SMTPAuthenticationError:
                flash('The email or password for the sender is not valid. Please try again.', 'danger')
                return redirect(url_for('shareRecords'))

            try:
                smtp.sendmail(user_email, receiver_address, msg.as_string())
            except smtplib.SMTPServerDisconnected:
                flash('The email server has disconnected unexpectedly. Please try again.', 'danger')
                return redirect(url_for('shareRecords'))
            except smtplib.SMTPRecipientsRefused:
                flash('The recipient refused to accept the email. Please try again.', 'danger')
                return redirect(url_for('shareRecords'))

            smtp.quit()

            flash('The email has been sent successfully!', 'success')
            # attempted = False
            return redirect(url_for('shareRecords'))

        return render_template('shareRecords.html', title='Share Medical Records', isLoggedin=True, form=form, has_records=has_records)
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
            returnStr = returnStr + str(sympt[i]) + ';'
    return returnStr

#Displays the results of the diagnosis
@app.route('/diagnosisReport', methods=['GET', 'POST'])
def diagnosisReport():
    api= infermedica_api.API(app_id='52457f85', app_key='95f03f5398a3b0358795540117d4f376')
    symptDesc = request.form["Symptoms"]
    currUser = getUser()
    currAge = calcAge(currUser.dob,date.today())
    gendAge = (currUser.sex.lower(),str(currAge))
    req = diagnose(api,gendAge,parser(api,str(symptDesc)))
    if req == None:
        flash('The symptoms you entered could not be recognized. Please try again.', 'danger')
        return render_template('diagnosis.html', title='Diagnosis & Treatment ', isLoggedin=True, accepted=True)
    lstIll = conditions(req[0])
    lstSympt = req[1]
    strSympt = stringFromSympt(lstSympt)
    if (lstIll[0] == "" and lstIll[1] == "" and lstIll[2] == ""):
        #if no conditions were found, more symptoms are needed
        flash('The symptoms you entered could not be recognized. Please try again.', 'danger')
        return render_template('diagnosis.html', title='Diagnosis & Treatment ', isLoggedin=True, accepted=True)
    cursor = conn.cursor()
    ins = 'INSERT INTO diagnosis(username,symptoms,illness,illness2,illness3) VALUES(%s,%s,%s,%s,%s)'
    cursor.execute(ins, (currUser.username, strSympt, lstIll[0], lstIll[1], lstIll[2]))
    conn.commit()
    query = cursor.execute("SELECT * FROM treatment WHERE illness = %s", lstIll[0])
    data = cursor.fetchone()
    cursor.close()
    #data[remedy] will return the corresponding treatment
    strDisplay = [] 
    if data:
        strRemedy = data["remedy"]
        treatments = strRemedy.split(';') # separates into list of treatments 
        for result in treatments:
            treatment = {}                # create a treatment object
            resultSplit = result.split(':') # separates into treatment and options
            treatment['treatment'] = resultSplit[0]
            if len(resultSplit) == 2:
                treatment['options'] = resultSplit[1].split(',')
            strDisplay.append(treatment)   # add treatment object to strDisplay 

    strBlank = "No natural treatment for the above diagnosis exists in our database\
        at this moment. Please consult your Primary Care Physician."

    return render_template('diagnosisResults.html', name = currUser.firstName, sex = currUser.sex, age = currAge,
     diagOne= lstIll[0], diagTwo = lstIll[1], diagThree = lstIll[2], treatments = strDisplay, blank = strBlank, isLoggedin=True)


@app.route("/diagnosis", methods=['GET'])
def diagnosis():
    if 'logged_in' in session:
        return render_template('diagnosis.html', title='Diagnosis & Treatment ', isLoggedin=True, accepted=False)
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
        return render_template('account.html', title='Account', isLoggedin=True, current_user=current_user)
    else:
        return redirect(url_for('home'))

@app.route("/account/edit", methods=['GET', 'POST'])
def update():
    if 'logged_in' in session:
        form = UpdateUserForm()
        current_user = getUser()
        if request.method == 'GET':  # fill in form with information in database
            form.first_name.data = current_user.firstName
            form.last_name.data = current_user.lastName
            form.username.data = current_user.username
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
                email = form.email.data
                addr_street = form.addr_street.data
                addr_city = form.addr_city.data
                addr_state = form.addr_state.data
                addr_zip = form.addr_zip.data
                cursor = conn.cursor()
                update = 'UPDATE user SET fName=%s, lName=%s, username=%s, email=%s, \
                    addr_street=%s, addr_city=%s, addr_state=%s, addr_zip=%s WHERE username=%s'
                cursor.execute(update, (firstName, lastName, username, email, addr_street,
                    addr_city, addr_state, addr_zip, currentUsername))
                session['username'] = username
                conn.commit()
                cursor.close()
                flash('Your account has been successfully updated!', 'success')  
                return redirect(url_for('update'))
            else:
                flash('Please check the errors below.', 'danger')

        return render_template('edit.html', title='Edit Account', form=form, current_user=current_user, isLoggedin=True)
    else:
        return redirect(url_for('home'))


# #==================================================================================


if __name__ == "__main__":
    app.run(debug=True)