from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
# IMPORTANT: Change 'your_secret_key' to a strong, random string for production
app.secret_key = 'your_secret_key' 

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Bau#80021'
# yaha per apna password lgao
# apna pass yaha likh de 
# ha likh do
app.config['MYSQL_DB']='campus' 
# sahi hai wait check krte h

mysql=MySQL(app)

@app.route('/')
def index():
    return render_template("index.html")


# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger') # 'danger' for error messages
            return render_template('signup.html') # Re-render the form with the error message

        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        
        # Optional: Check if username or email already exists to prevent duplicates
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username or Email already exists!', 'warning') # 'warning' for a cautionary message
            cursor.close()
            return render_template('signup.html') # Re-render the form with the warning

        cursor.execute("INSERT INTO users (username, email, password, agreed_terms) VALUES (%s, %s, %s, %s)",
                       (username, email, hashed_password, True))
        mysql.connection.commit()
        cursor.close()

        flash('Signup successful! Please log in.', 'success') # 'success' for positive feedback
        return redirect(url_for('login'))
    
    # This is the crucial part: it handles GET requests (when the user first visits /signup)
    # and also returns to the signup page if a POST request fails validation and needs to show the form again.
    return render_template('signup.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username= request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        # Assuming 'username' is the second column (index 1) and 'password' hash is the fourth (index 3)
        # based on your `check_password_hash(user[3], password)`
        cursor.execute("SELECT id, username, email, password, agreed_terms FROM users WHERE username = %s", (username,))
        user = cursor.fetchone() # user is a tuple: (id, username, email, password_hash, agreed_terms)
        cursor.close()

        # user[3] refers to the hashed password in the database
        if user and check_password_hash(user[3], password): 
            session['user_id'] = user[0] # Store user_id in session if you need it
            session['username'] = user[1] # Store username in session
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home2'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route("/home2")
def home2():
    if 'username' in session:
        return render_template('home2.html', user=session['username'])
    else:
        return redirect(url_for('login'))

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/book")
def book():
    return render_template('book.html')

@app.route("/clothes")
def clothes():
    return render_template('clothes.html')

@app.route("/hostel")
def hostel():
    return render_template('hostel.html')

@app.route("/sell")
def sell():
    return render_template('sell.html')

@app.route("/electronic")
def electronic():
    return render_template('electronic.html')

@app.route("/event")
def event():
    return render_template('event.html')

@app.route("/account")
def account():
    return render_template('account.html')

@app.route("/stationery")
def stationery():
    return render_template('stationery.html')

@app.route("/note")
def note():
    return render_template('note.html')
@app.route('/chatp/<int:seller_id>', methods=['GET', 'POST'])
def chatp(seller_id):
    cur = mysql.connection.cursor()

    # Fetch messages for the seller
    cur.execute("SELECT * FROM messages WHERE receiver_id = %s ORDER BY timestamp ASC", (seller_id,))
    messages = cur.fetchall()

    if request.method == 'POST':
        sender_id = 1  # Replace with actual sender from session
        msg = request.form['message']
        cur.execute("INSERT INTO messages (sender_id, receiver_id, message_content) VALUES (%s, %s, %s)",
                    (sender_id, seller_id, msg))
        mysql.connection.commit()

    return render_template('chatp.html', messages=messages,seller_id=seller_id)
# sender
@app.route('/contact_seller/<int:seller_id>', methods=['GET', 'POST'])
def contact_seller(seller_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # if user not logged in

    sender_id = session['user_id']
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        message = request.form['message']
        cur.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                    (sender_id, seller_id, message))
        mysql.connection.commit()

    # Fetch chat history
    cur.execute("""
    SELECT sender_id, receiver_id, message_content, timestamp FROM messages
    WHERE (sender_id = %s AND receiver_id = %s)
       OR (sender_id = %s AND receiver_id = %s)
    ORDER BY timestamp ASC
""", (session['user_id'], seller_id, seller_id, session['user_id']))


    return render_template('contact_seller.html', messages=message, sender_id=sender_id)

# Logout
@app.route('/logout')
def logout():
    session.clear() # Clears all session data
    flash('Logged out successfully!', 'info') # 'info' for informational messages
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)