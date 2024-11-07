from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from datetime import datetime, date
from werkzeug.security import generate_password_hash
from sqlalchemy import Text
from sqlalchemy import Column, Boolean, DateTime, DECIMAL


from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
from functools import wraps
import os
from dotenv import load_dotenv



# Load environment variables from .env file
load_dotenv()
  # Load environment variables from .env file
#print("dotenv loaded successfully!")

# App and database setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]  # Use only the environment variable for PostgreSQL URI
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]  # Use only the environment variable for security
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.mailtrap.io")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT", 2525)
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "your_mailtrap_username")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "your_mailtrap_password")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

# Initialize extensions
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
scheduler = BackgroundScheduler()

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'your_account_sid')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'your_auth_token')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', 'your_twilio_phone_number')


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)



''''
#Verify the Database Connection: 
with app.app_context():
    try:
        db.create_all()  # Create all tables
        print("Database connected successfully!")
    except Exception as e:
        print(f"Database connection failed: {e}")

'''
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True)
    address = db.Column(db.String(500), nullable=True)
    country = db.Column(db.String(150))
    state = db.Column(db.String(150), nullable=True)
    church_branch = db.Column(db.String(150))
    birthday = db.Column(db.Date, nullable=True)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pledged_amount = db.Column(db.Float, default=0.0)
    pledge_currency = db.Column(db.String(3), default="USD")
    paid_status = db.Column(db.Boolean, default=False)


    # Relationships
    pledges = db.relationship('Pledge', back_populates='donor', cascade="all, delete-orphan")

    

    def set_password(self, password):
        """Set the user's password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored password hash."""
        return check_password_hash(self.password_hash, password)


# Donation model
class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(50), default='USD')
    donation_date = db.Column(db.Date, nullable=False, default=date.today) 

    user = db.relationship("User", backref="donations")
    #user = db.relationship('User', backref='pledges')
    


'''

class Pledge(db.Model):
    __tablename__ = 'pledge'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date_pledged = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

'''
class Pledge(db.Model):
    __tablename__ = 'pledges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pledged_amount = db.Column(db.Numeric)  # Ensure this attribute is defined
    pledge_currency = db.Column(db.String)  # Example additional attribute
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to User model
    #user = db.relationship('User', backref='pledges')
    donor = db.relationship('User', back_populates='pledges')  # This should reference 'pledges' in User
    
    

# Schedule for sending birthday emails
def send_birthday_emails():
    today = datetime.now().date()
    users_with_birthday = User.query.filter(
        db.extract('month', User.birthday) == today.month,
        db.extract('day', User.birthday) == today.day
    ).all()
    for user in users_with_birthday:
        msg = Message(
            "Happy Birthday!",
            sender="noreply@donationtracker.com",
            recipients=[user.email]
        )
        msg.body = f"Dear {user.name},\n\nHappy Birthday! We wish you a wonderful day!\n\nBest regards,\nDonation Tracker Team"
        mail.send(msg)

scheduler.add_job(send_birthday_emails, 'cron', day='*', hour=0)
scheduler.start()




# Decorators to protect routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        country = request.form['country']  # Country from the dropdown
        state = request.form['state']  # State from the dropdown
        manual_country = request.form.get('manual_country')  # Manual country input
        manual_state = request.form.get('manual_state')  # Manual state input

        # Use manual country/state if provided; otherwise, fall back to dropdown
        if manual_country:
            country = manual_country
        if manual_state:
            state = manual_state

        # Handle birthday input with optional year
        birthday_str = request.form.get('birthday')  # e.g., '10-10' or '2024-10-10'
        # Convert the birthday string to a date object if provided
        birthday = None
        if birthday_str:
            try:
                # Try parsing in 'YYYY-MM-DD' format
                birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
            except ValueError:
                try:
                    # Try parsing in 'DD-MM-YYYY' format
                    birthday = datetime.strptime(birthday_str, "%d-%m-%Y").date()
                except ValueError:
                    flash('Invalid date format for birthday. Please use YYYY-MM-DD or DD-MM-YYYY.', 'error')
                    return render_template('register.html')
                

        # Ensure email is unique
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered.', 'error')
            return render_template('register.html')

        # Create a new user
        new_user = User(
            name=name,
            phone=phone,
            email=email,
            address=address,
            country=country,  # Store the selected or manual country
            state=state,      # Store the selected or manual state
            church_branch=request.form['church_branch'],  # Ensure this field is also included
            birthday=birthday,
            is_admin=False,
            is_super_admin=False
        )
        new_user.set_password(password)  # Set hashed password

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')  # Render the registration form template


# Home route
@app.route("/")
def index():
    return render_template("index.html")

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Retrieve the user record
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            session['is_super_admin'] = user.is_super_admin

            flash(f'Welcome, {user.name}!', 'success')
            
            if user.is_admin or user.is_super_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('donate'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route("/donate", methods=["GET", "POST"])
@login_required
def donate():
    user = get_current_user()  # Retrieve the current user
    app.logger.debug(f"User object: {user}")  # Log the user object to see its attributes

    if request.method == "POST":
        user_id = session.get("user_id")

        if request.form.get("offline_donation"):
            # User is entering an offline donation amount
            amount = request.form.get("amount")
            currency = request.form.get("currency")
            donation_date = request.form.get("donation_date")  # Get date from form, if provided

            # Validate the amount
            try:
                amount = float(amount)
                if amount <= 0:
                    flash("Donation amount must be greater than zero.", "danger")
                    return redirect(url_for("donate"))
            except (ValueError, TypeError):
                flash("Invalid amount format.", "danger")
                return redirect(url_for("donate"))

            # Validate or set the donation date
            if not donation_date:
                donation_date = date.today()  # Default to today's date if not provided
            else:
                try:
                    donation_date = datetime.strptime(donation_date, '%Y-%m-%d').date()
                except ValueError:
                    flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                    return redirect(url_for("donate"))

            if user_id:
                # Create a new Donation object
                donation = Donation(user_id=user_id, amount=amount, currency=currency, donation_date=donation_date)

                try:
                    db.session.add(donation)
                    db.session.commit()
                    flash("Thank you for confirming your offline donation!", "success")
                    app.logger.info(f"Donation saved: {donation.amount}, User ID: {user_id}, Date: {donation_date}")
                    return redirect(url_for("donation_success"))
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error saving donation: {e}")
                    flash("An error occurred while processing your donation. Please try again.", "danger")
            else:
                flash("You need to be logged in to donate.", "danger")
                return redirect(url_for("login"))

        if request.form.get("show_account"):
            # Logic to show bank account details
            return render_template("donate.html", user=user, show_account_details=True)

    # Retrieve all pledges made by users from the database by joining User and Pledge
    pledges = db.session.query(Pledge, User).join(User, Pledge.user_id == User.id).all()

    return render_template("donate.html", user=user, pledges=pledges, show_account_details=False)



def get_current_user():
    user_id = session.get("user_id")
    return User.query.get(user_id) if user_id else None  # Adjust according to your ORM




# Donation success route
@app.route("/donation_success")
@login_required
def donation_success():
    return render_template("donation_success.html")




#Admin Registration route
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        country = request.form.get('country')
        state = request.form.get('state')  # This is the selected state
        manual_country = request.form.get('manual_country')  # Manual country input
        manual_state = request.form.get('manual_state')  # Manual state input
        church_branch = request.form.get('church_branch')

        # Use manual country/state if provided
        if manual_country:
            country = manual_country
        if manual_state:
            state = manual_state

        # Ensure email is unique
        existing_admin = User.query.filter_by(email=email).first()
        if existing_admin:
            flash('Email address already registered.', 'error')
            return render_template('admin_register.html')

        # Create new admin user
        new_admin = User(
            name=name,
            phone=phone,
            email=email,
            address=address,
            country=country,
            state=state,
            church_branch=church_branch,
            is_admin=True,        # Admin user
            is_super_admin=False  # Not a super admin
        )
        new_admin.set_password(password)

        # Commit to the database
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin registration successful! You can now log in.', 'success')
        return redirect(url_for('admin_login'))  # Adjust the redirect as necessary

    return render_template('admin_register.html')  # Render the registration form template


# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Retrieve the admin record
        admin = User.query.filter_by(email=email, is_admin=True).first()

        if admin and admin.check_password(password):
            session['user_id'] = admin.id
            session['is_admin'] = admin.is_admin
            session['is_super_admin'] = admin.is_super_admin

            flash(f'Welcome, {admin.name}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('admin_login.html')


@app.route("/admin_dashboard", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    # Handle bulk SMS and email
    if request.method == "POST":
        if "send_bulk_sms" in request.form:
            message = request.form["sms_message"]
            send_bulk_sms(message)
            flash("Bulk SMS sent successfully!", "success")
        elif "send_bulk_email" in request.form:
            subject = request.form["email_subject"]
            body = request.form["email_body"]
            send_bulk_email(subject, body)
            flash("Bulk email sent successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    # Fetch all donations and users
    users = User.query.all()
    donations = Donation.query.all()
    total_donations = sum(donation.amount for donation in donations)

    return render_template("admin_dashboard.html", users=users, recent_donations=donations, total_donations=total_donations)





# API endpoint to fetch user details by ID
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Fetch user details using SQLAlchemy
    user = User.query.get(user_id)
    
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    # Fetch donation history for the user
    donations = Donation.query.filter_by(user_id=user_id).all()
    
    # Prepare donations list
    donation_history = [{'amount': donation.amount, 'currency': donation.currency} for donation in donations]
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'address': user.address,
        'country': user.country,
        'state': user.state,
        'church_branch': user.church_branch,
        'birthday': user.birthday,
        'role': 'Admin' if user.is_admin else 'User',
        'phone': user.phone,
        'donation_history': donation_history,  # List of donations for the user
        'is_active': user.is_active,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }), 200



# Route to delete a user
@app.route("/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        # Delete the user; associated pledges will be deleted automatically
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting user: {e}")
        flash("An error occurred while deleting the user.", "danger")
    return redirect(url_for("admin_dashboard"))




# Route to delete a donation
@app.route("/delete_donation/<int:donation_id>", methods=["POST"])
@admin_required
def delete_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    try:
        db.session.delete(donation)
        db.session.commit()
        flash("Donation deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting donation: {e}")
        flash("An error occurred while deleting the donation.", "danger")
    return redirect(url_for("admin_dashboard"))


@app.route('/add_pledge', methods=['GET', 'POST'])
def add_pledge():
    if request.method == 'POST':
        # Handling form submission
        if request.form:
            user_id = request.form['user_id']  # Get the user ID from the form
            pledged_amount = request.form['pledged_amount']
            pledge_currency = request.form['currency']

            # Fetch the user from the User table
            user = User.query.get(user_id)

            if user:
                # Update the pledged amount and currency in the User table
                user.pledged_amount = float(pledged_amount)  # Ensure this is a float
                user.pledge_currency = pledge_currency

                # Commit the changes to the database
                db.session.commit()

                flash('Pledge added successfully!')
                return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard or success page
            else:
                flash('User not found!', 'danger')
                return redirect(url_for('admin_dashboard'))  # Redirect in case user not found
        
        # Handling JSON submission
        else:
            data = request.get_json()
            user_id = data.get('user_id')
            pledged_amount = data.get('pledged_amount')
            pledge_currency = data.get('currency', 'USD')  # Default to 'USD' if currency not provided

            # Fetch the user from the User table
            user = User.query.get(user_id)

            if user:
                # Update the pledged amount and currency in the User table
                user.pledged_amount = float(pledged_amount)
                user.pledge_currency = pledge_currency

                # Commit the changes to the database
                db.session.commit()

                return jsonify({'success': True, 'message': 'Pledge added successfully.'})
            else:
                return jsonify({'success': False, 'message': 'User not found.'}), 404

    return render_template('add_pledge.html')  # Render the form for adding pledges




def get_user_by_id(user_id):
    return User.query.get(user_id)  


@app.route('/update_pledge/<int:user_id>', methods=['GET', 'POST'])
def update_pledge(user_id):
    if request.method == 'POST':
        pledged_amount = request.form['pledged_amount']
        currency = request.form['currency']
        
        # Update the pledge in the database
        update_user_pledge(user_id, pledged_amount, currency)

        flash('Pledge updated successfully!')
        return redirect(url_for('admin_dashboard'))

    # Fetch the user and current pledge details
    user = get_user_by_id(user_id)
    current_pledge = get_current_pledge(user_id)
    return render_template('update_pledge.html', user=user, current_pledge=current_pledge)


def get_current_pledge(user_id):
    return Pledge.query.filter_by(user_id=user_id).first()




def update_user_pledge(user_id, pledged_amount, currency):
    # Logic to find the pledge associated with the user and update it
    pledge = Pledge.query.filter_by(user_id=user_id).first()
    if pledge:
        pledge.pledged_amount = float(pledged_amount)
        pledge.pledge_currency = currency
        db.session.commit()


def get_current_pledge(user_id):
    # Logic to retrieve the current pledge for the user
    return Pledge.query.filter_by(user_id=user_id).first()



@app.route('/track')
def track():
    # Fetch all users with their donations (pledges)
    users_with_pledges = User.query.join(Donation).all()

    # Create a list of dictionaries with user and pledge data
    pledges_data = []
    for user in users_with_pledges:
        for pledge in user.donations:  # `donations` backref on User model
            pledges_data.append({
                'user': user,
                'pledge': pledge
            })
    
    # Print data to check if it's correct
    print(pledges_data)  # Debug line, you can check this in your terminal or console
    
    return render_template('track.html', pledges=pledges_data)




@app.route('/success')
def success():
    return "Pledge added successfully!", 200


    


# Logout route
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    session.pop('is_super_admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
