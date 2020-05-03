'''
Directory tree:
Home (reroutes to dashboard if logged in)
--> About, Login, Register
if logged in: (reroutes to home otherwise)
    Dashboard (View all photos of following and personal photos)
    --> About
    --> Edit Account
    --> Logout
    --> Follow
    --> ManageRequests
        - FollowRequests
        - TagRequests
    --> MyGroups
    Logout
    --> Redirects to Home
    User (View all personal photos and group information)
'''
import os
import time
import datetime
import secrets
from flask import Flask
from PIL import Image
from flask import render_template, request, session, url_for, flash, redirect
import hashlib
from forms import RegistrationForm, LoginForm, ChangePassForm, \
    FollowRequestForm, ManageFollowRequestForm, UpdateUserForm, CreateGroupForm, \
    ManageGroupForm, CreatePostForm, TagUserForm, ManageTagRequestForm
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
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    current_user = User(data["fname"], data["lname"], username,
                        data["password"], data["bio"], data["avatar"], data["isPrivate"])
    cursor.close()
    return current_user


def getTagRequests():
    requests = []
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT photoID FROM Tag WHERE username = %s AND acceptedTag = 0'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for i in range(len(data)):
        requests.append((i, data[i].get('photoID')))
    cursor.close()
    return requests


def getFollowRequests():
    requests = []
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT followerUsername FROM Follow WHERE followeeUsername = %s AND acceptedFollow = 0'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for i in range(len(data)):
        requests.append((i, data[i].get('followerUsername')))
    cursor.close()
    return requests


def getGroups(username):
    # returns a list containing the names of the groups owned by 'username'
    groupNames = []
    cursor = conn.cursor()
    query = 'SELECT groupName FROM CloseFriendGroup WHERE groupOwner = %s'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for i in range(len(data)):
        groupNames.append((i, data[i].get('groupName')))
    cursor.close()
    return groupNames


def getMembers(groupName, groupOwner):  # used for the group form
    members = []  # we want a simple tupple array with position and username
    cursor = conn.cursor()
    # everyone other than the owner (who is also a member)
    query = 'SELECT username FROM Belong WHERE groupName = %s AND groupOwner =%s'
    cursor.execute(query, (groupName, groupOwner))
    data = cursor.fetchall()
    for i in range(len(data)):
        members.append((i, data[i].get('username')))
    cursor.close()
    return members
#===========================================================================


class User():

    def __init__(self, fName, lName, username, password, bio, avatar, isPrivate):
        self.firstName = fName
        self.lastName = lName
        self.username = username
        self.password = password
        self.bio = bio
        self.avatar = url_for('static', filename='profilePics/' + str(avatar))
        self.isPrivate = isPrivate
        self.followers = []
        self.following = []
        self.numberOfFollowers = 0
        self.numberOfFollowing = 0

    def getFollowers(self):
        cursor = conn.cursor()
        query = 'SELECT followerUsername FROM Follow WHERE followeeUsername = %s AND acceptedFollow = 1'
        cursor.execute(query, (self.username))
        data = cursor.fetchall()
        for i in range(len(data)):
            self.followers.append((i, data[i].get('followerUsername')))
        self.numberOfFollowers = len(self.followers)
        cursor.close()

    def getFollowing(self):
        cursor = conn.cursor()
        query = 'SELECT followeeUsername FROM Follow WHERE followerUsername = %s AND acceptedFollow = 1'
        cursor.execute(query, (self.username))
        data = cursor.fetchall()
        for i in range(len(data)):
            self.following.append((i, data[i].get('followeeUsername')))
        self.numberOfFollowing = len(self.following)
        cursor.close()


@app.route("/")
@app.route("/home")
def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))  

    return render_template('home.html', title='Home')

# only accessible if logged in


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' in session:
        current_user = getUser()
        username = current_user.username
        # fetch photos
        '''
        User can view photos if:
        1. User is the owner of the photo
        2. The photo is allFollowers and User is a follower of the owner
        3. The photo is not allFollowers and the User is in a closefriendgroup that the photo has been shared with
        '''
        cursor = conn.cursor()
        query = 'SELECT photoID,photoOwner, caption, timestamp, filePath FROM Photo AS p1 WHERE photoOwner = %s OR photoID IN (SELECT photoID FROM Photo WHERE photoOwner != %s AND allFollowers = 1 AND photoOwner IN (SELECT followeeUsername FROM follow WHERE followerUsername = %s AND followeeUsername = photoOwner AND acceptedFollow = 1)) OR photoID IN (SELECT photoID FROM share NATURAL JOIN belong NATURAL JOIN photo WHERE username = %s AND photoOwner != %s) ORDER BY timestamp DESC'

        cursor.execute(query, (username, username, username, username, username))
        data = cursor.fetchall()

        # modify data to include the first and last names of the tagees
        for post in data:  # post is a dictionary
            query = 'SELECT fname, lname FROM Tag NATURAL JOIN Person NATURAL JOIN Photo WHERE acceptedTag = 1 AND photoID = %s'
            cursor.execute(query, (post['photoID']))
            result = cursor.fetchall()
            if (result):
                post['tagees'] = result
                # print(post)

        cursor.close()
        # clean up data
        return render_template('dashboard.html', title='Dashboard', current_user=current_user, isLoggedin=True, posts=data)
    else:
        return redirect(url_for('home'))


@app.route("/about")
def about():
    isLoggedin = False
    if 'logged_in' in session:
        isLoggedin = True
    # Will contain project information
    return render_template('about.html', title='About', isLoggedin=isLoggedin)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    isLoggedin = False
    if 'logged_in' in session:
        return redirect(url_for('home'))
    if form.validate_on_submit():  # the function valifate_on_submit() is a member function of FlaskForm
        # check that the user information doesn't already exist
        firstName = form.first_name.data
        lastName = form.last_name.data
        username = form.username.data
        password_hashed = encrypt(form.password.data)
        # create and execute query
        cursor = conn.cursor()
        ins = 'INSERT INTO Person(fname,lname,username,password,avatar,isPrivate) VALUES(%s,%s,%s,%s,"default.jpg",1)'
        cursor.execute(ins, (firstName, lastName, username, password_hashed))
        # save changes to database
        conn.commit()
        cursor.close()
        # notify the user of successful creation of account
        flash(f'Account created for {form.username.data}! You can now login', 'success')  # the second argument taken by the flash function indicates the type of result our message is

        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form, isLoggedin=isLoggedin)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # no errors when inputting data and no empty fields
        # fetch data from the form
        username = form.username.data
        password_to_check = form.password.data

        cursor = conn.cursor()
        # execute query
        query = cursor.execute("SELECT * FROM Person WHERE username = %s", username)

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
                flash("You Have Successfuly Logged in", "success")
                return redirect(url_for("dashboard"))
            else:  # passwords do not match

                flash('Login Unsuccessful. Please check username and password.', 'danger')
                # we don't want to flash the password being incorrect, but just highliight it and display it as an error underneath the password field

            # close connection
            cursor.close()
        else:  # no results with the specified username in the database
            flash('Login Unsuccessful. No Account Exists With That Username.', 'danger')
            cursor.close()

    return render_template('login.html', title='Login', form=form)


@app.route("/changePassword", methods=['GET', 'POST'])
def changePassword():
    form = changePassForm()
    # should be logged in already
    # user enters current password
    if 'logged_in' in session:
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
    session.clear()
    flash('You have logged out', 'success')
    return redirect(url_for('home'))

# handles follow requests from user1 to user2
# if user2 is a public account, the request is fuliflled right away
# if user2 is a private account, user2 will recieve a follow request which can either be accepted or decline
# if the follow request is accepted, user1 will get notified once logged in
# if the follow is declined, the request will be removed from the database and user1 will not get notified


@app.route("/settings")
def settings():
    if 'logged_in' in session:
        render_template('settings.html', title='Settings')
    else:
        return redirect(url_for('home'))


@app.route("/follow", methods=['GET', 'POST'])
def follow():
    form = FollowRequestForm()
    if 'logged_in' in session:
        if form.validate_on_submit():
            username = session['username']
            userFollow = form.userFollow.data
            # search for the user
            cursor = conn.cursor()
            query = 'SELECT * From Person WHERE username=%s'
            cursor.execute(query, (userFollow))
            data = cursor.fetchone()
            if (data['isPrivate']):  # create a follow request
                ins = 'INSERT INTO Follow(followerUsername,followeeUsername,acceptedFollow)VALUES(%s, %s, 0)'
                cursor.execute(ins, (username, userFollow))
                conn.commit()
                cursor.close()

                # notify user follow request has been sent
                flash(f'{userFollow} has recieved your follow request! You will be notified if it is accepted', 'success')
                return redirect(url_for('follow'))
            # the userFollow is public
            ins = 'INSERT INTO Follow(followerUsername,followeeUsername,acceptedFollow) VALUES(%s, %s, 1)'
            cursor.execute(ins, (username, userFollow))
            conn.commit()
            cursor.close()
            flash(f'You Now Follow {userFollow}!', 'success')
            return redirect(url_for('follow'))
        return render_template('follow.html', title='Follow', form=form, isLoggedin=True)


@app.route("/followRequests", methods=['GET', 'POST'])
def followRequests():
    form = ManageFollowRequestForm()
    if 'logged_in' in session:
        current_user = getUser()
        requests = getFollowRequests()
        if request.method == 'GET':
            form.select.choices = requests

        elif request.method == 'POST':
            # form.select.data returns a list of strings corresponding to the position of a username in requests
            # iterate through the data and update the acceptedFollow
            # make this better
            result = form.select.data
            cursor = conn.cursor()
            for i in range(len(form.select.data)):
                accepted = requests[int(result[i])][1]
                update = 'UPDATE Follow SET acceptedFollow = 1 WHERE followerUsername=%s AND followeeUsername=%s'
                cursor.execute(update, (accepted, session['username']))
                conn.commit()
            cursor.close()
            if len(result) > 1:
                flash('You have new followers! Requests have been updated!', 'success')
                return redirect(url_for('followRequests'))
            else:
                flash('You have a new follower! Requests have been updated!', 'success')
                return redirect(url_for('followRequests'))
        # if form.validate_on_submit():

        return render_template('followRequests.html', title='Follow Requests', form=form, isLoggedin=True, current_user=current_user)
    else:
        return redirect(url_for('home'))


@app.route("/groups", methods=['GET', 'POST'])
def groups():
    if 'logged_in' in session:
        return render_template('groups.html', title='Groups', isLoggedin=True)
    else:
        return redirect(url_for('home'))


@app.route("/groups/create", methods=['GET', 'POST'])
def createGroup():
    if 'logged_in' in session:
        # handles creating groups
        form = CreateGroupForm()
        current_user = getUser()
        username = current_user.username

        if form.validate_on_submit():
            # handle CreateGroupForm
            name = form.name.data
            cursor = conn.cursor()
            ins = 'INSERT INTO CloseFriendGroup(groupName, groupOwner) VALUES (%s,%s)'
            cursor.execute(ins, (name, username))
            # add ourselves to the group (in belongs)
            ins = 'INSERT INTO Belong(groupName, groupOwner, username) VALUES (%s,%s,%s)'
            cursor.execute(ins, (name, username, username))
            conn.commit()
            cursor.close()

            flash('You Successfuly Created A Close Friend Group! You Can Now Add Your Friends!', 'success')
            return redirect(url_for('createGroup'))

        return render_template('createGroup.html', title='Create Group', form=form, isLoggedin=True, current_user=current_user)
    else:
        return redirect(url_for('home'))


@app.route("/groups/manage", methods=['GET', 'POST'])
def manageGroups():
    form = ManageGroupForm()
    if 'logged_in' in session:
        current_user = getUser()
        username = current_user.username
        groupNames = getGroups(username)  # returns a tupple list of the grouNames owned by 'username'
        form.group.choices = groupNames

        if form.validate_on_submit():  # and form.newUserForm.validate(form):
            groupName = groupNames[int(form.group.data)][1]
            # handle 'add user' event, the user inputed should be added to the group
            addMember = form.newUser.data
            cursor = conn.cursor()
            ins = 'INSERT INTO Belong(groupName, groupOwner, username) VALUES (%s,%s,%s)'

            cursor.execute(ins, (groupName, username, addMember))
            conn.commit()
            cursor.close()
            flash(f'{addMember} is now in your {groupName} group!', 'success')
            return redirect(url_for('manageGroups'))

            # elif form.removeMember.data:  # and form.currentMemberForm.validate(form):
            #     print('oh no')
            #     # handle 'remove user' event, the current member in the group should be removed from the group
            #     removeUser = form.members.data  # a list of members
            #     pass
        # elif request.method == 'GET':
        #     print('In here!')
        #     form.group.choices = groupNames
            # populate the group form and the current user form
            # form.members.choices = []
        return render_template('manageGroups.html', title='Groups', form=form, isLoggedin=True, current_user=current_user)
    else:
        return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
def account():
    if 'logged_in' in session:
        current_user = getUser()
        current_user.getFollowers()
        current_user.getFollowing()
        return render_template('account.html', title='Account', isLoggedin=True, current_user=current_user)
    else:
        return redirect(url_for('home'))


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
    form = UpdateUserForm()
    current_user = getUser()
    if 'logged_in' in session:
        if form.validate_on_submit():
            # won't update the avatar if no data is given
            currentUsername = session['username']
            firstName = form.first_name.data
            lastName = form.last_name.data
            username = form.username.data
            bio = form.bio.data
            isPrivate = form.isPrivate.data
            setPriv = 1 if isPrivate == 'T' else 0
            cursor = conn.cursor()
            if form.avatar.data:
                picture_file = save_picture(form.avatar.data)
                update = 'UPDATE Person SET fName=%s, lName=%s, username=%s, bio=%s, avatar=%s,isPrivate=%s WHERE username=%s'
                cursor.execute(update, (firstName, lastName, username, bio, picture_file, setPriv, currentUsername))
            else:
                update = 'UPDATE Person SET fName=%s, lName=%s, username=%s, bio=%s,isPrivate=%s WHERE username=%s'
                cursor.execute(update, (firstName, lastName, username, bio, setPriv, currentUsername))
            # update the session username
            session['username'] = username
            # save changes to database
            conn.commit()
            cursor.close()
            # notify the user of successful creation of account
            flash('Your account has been updated!', 'success')  # the second argument taken by the flash function indicates the type of result our message is
            return redirect(url_for('update'))
        if request.method == 'GET':  # fill in form with information given
            form.first_name.data = current_user.firstName
            form.last_name.data = current_user.lastName
            form.username.data = current_user.username
            form.bio.data = current_user.bio
            form.isPrivate.data = 'T' if current_user.isPrivate else 'F'

        return render_template('edit.html', title='Edit Account', form=form, current_user=current_user, isLoggedin=True)
    else:
        return redirect(url_for('home'))


@app.route("/post", methods=['GET', 'POST'])
def post():
    form = CreatePostForm()
    if 'logged_in' in session:
        # need to populate the groups
        username = session['username']
        groupNames = getGroups(username)
        form.groups.choices = groupNames
        if form.validate_on_submit():
            # print(form.image.data)
            picture_file = save_picture2(form.image.data)
            caption = form.caption.data
            allFollowers = form.allFollowers.data
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            if allFollowers == 'T':
                # insert the new photo to database
                # no need to check groups
                cursor = conn.cursor()
                ins = 'INSERT INTO Photo(photoOwner, timestamp, filePath, caption, allFollowers) VALUES(%s,%s,%s,%s,1)'
                cursor.execute(ins, (username, timestamp, picture_file, caption))
                conn.commit()
                cursor.close()
            elif allFollowers == 'F':
                # insert new photo to database
                cursor = conn.cursor()
                ins = 'INSERT INTO Photo(photoOwner, timestamp, filePath, caption, allFollowers) VALUES(%s,%s,%s,%s,0)'
                cursor.execute(ins, (username, timestamp, picture_file, caption))
                conn.commit()
                cursor.close()
                # get the group names
                results = form.groups.data
                for i in range(len(form.groups.data)):
                    name = groupNames[int(results[i])][1]
                    cursor = conn.cursor()
                    # share photo with all groups indicated in groups.data
                    ins = 'INSERT INTO Share(groupName, groupOwner, photoID) VALUES(%s,%s,LAST_INSERT_ID())'
                    cursor.execute(ins, (name, username))
                    conn.commit()
                    cursor.close()
            flash('Your Photo Has Been Posted!', 'success')
            return redirect(url_for('post'))
        return render_template('post.html', title='Post', form=form, isLoggedin=True)
    else:
        return redirect(url_for('home'))


@app.route("/tag", methods=['GET', 'POST'])
def tag():
    form = TagUserForm()
    var = request.args.get('id', None)
    if 'logged_in' in session:
        if request.method == 'GET':
            form.photoID.data = var

        if form.validate_on_submit():
            userTag = form.userTag.data
            photoID = form.photoID.data
            # create a tag request
            cursor = conn.cursor()
            ins = 'INSERT INTO Tag(username, photoID, acceptedTag) VALUES(%s,%s,0)'
            cursor.execute(ins, (userTag, photoID))
            conn.commit()
            cursor.close()
            flash(f'A Tag request was sent to {userTag} for photo ID: {photoID}', 'success')
            return redirect(url_for('dashboard'))
        return render_template('tag.html', title='Tag', isLoggedin=True, form=form)

    else:
        return redirect(url_for('home'))


@app.route("/tagRequests", methods=['GET', 'POST'])
def tagRequests():
    form = ManageTagRequestForm()
    if 'logged_in' in session:
        current_user = getUser()
        requests = getTagRequests()
        if request.method == 'GET':
            form.select.choices = requests

        elif request.method == 'POST':
            # form.select.data returns a list of strings corresponding to the position of a username in requests
            # iterate through the data and update the acceptedTag
            result = form.select.data
            cursor = conn.cursor()
            for i in range(len(form.select.data)):
                accepted = requests[int(result[i])][1]  # get the photoID
                update = 'UPDATE Tag SET acceptedTag = 1 WHERE photoID=%s AND username=%s'
                cursor.execute(update, (accepted, session['username']))
                conn.commit()
            cursor.close()
            if len(result) > 1:
                flash('You have been tagged in new photos! Requests have been updated!', 'success')
                return redirect(url_for('followRequests'))
            else:
                flash('You have been tagged in a new photo! Requests have been updated!', 'success')
                return redirect(url_for('tagRequests'))
        # if form.validate_on_submit():

        return render_template('tagRequests.html', title='Tag Requests', form=form, isLoggedin=True, current_user=current_user)
    else:
        return redirect(url_for('home'))

# #==================================================================================


if __name__ == "__main__":
    app.run(debug=True)
