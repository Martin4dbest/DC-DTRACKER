from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from datetime import datetime, date
from werkzeug.security import generate_password_hash
from sqlalchemy import Text
from sqlalchemy import Column, Boolean, DateTime, DECIMAL
from flask_login import LoginManager, login_required, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
from functools import wraps
import os


from flask_login import LoginManager


from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import boto3
from botocore.exceptions import BotoCoreError, ClientError



# AWS SES Setup
AWS_REGION = 'us-east-1'  # Use your AWS region
SENDER_EMAIL = 'your-ses-verified-email@example.com'  # SES verified email address

# Initialize the SES client
ses_client = boto3.client('ses', region_name=AWS_REGION)


# Initialize AWS clients for SES and SNS
ses_client = boto3.client("ses", region_name="us-west-2")  # Update region if necessary
sns_client = boto3.client("sns", region_name="us-west-2")







# Load environment variables from .env file
load_dotenv()
  # Load environment variables from .env file
#print("dotenv loaded successfully!")

# App and database setup
app = Flask(__name__)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)  # Attach it to the Flask app
login_manager.login_view = 'login'  # Specify the login route name
login_manager.login_message = "Please log in to access this page."  # Optional custom login message
login_manager.login_message_category = "info"  # Optional message category for flash messages


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
    medal = db.Column(db.String(100), nullable=True)  # In your User model
    partner_since = db.Column(db.Integer, nullable=True)  # Year as an integer




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
    payment_type = db.Column(db.String(20), nullable=False, default="full")  # New field for payment type
    
    

    

    user = db.relationship("User", backref="donations")
    medal = db.Column(db.String(50))  # field to store medal type
    #user = db.relationship('User', backref='pledges')
    



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
            flash('', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
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
                    return render_template('register.html', current_year=datetime.now().year)

        # Get the 'Partner Since' year
        partner_since = request.form.get('partner_since')
        if partner_since:
            try:
                partner_since = int(partner_since)
                if partner_since < 1900 or partner_since > datetime.now().year:
                    raise ValueError
            except ValueError:
                flash('Invalid year for Partner Since. Please provide a valid year.', 'error')
                return render_template('register.html', current_year=datetime.now().year)

        # Check if email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered.', 'error')
            return render_template('register.html', current_year=datetime.now().year)

        # Create a new user
        new_user = User(
            name=name,
            phone=phone,
            email=email,
            address=address,
            country=country,
            state=state,
            church_branch=request.form['church_branch'],  # Ensure this field is also included
            birthday=birthday,
            partner_since=partner_since,  # Store the Partner Since year
            is_admin=False,
            is_super_admin=False
        )
        new_user.set_password(password)  # Set hashed password

        # Save user to the database
        db.session.add(new_user)
        db.session.commit()

        # Success message and redirect
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    # Render the registration form
    return render_template('register.html', current_year=datetime.now().year)



@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)  # Assuming `User` is your user table





# Home route
@app.route("/")
def index():
    return render_template("index.html")

 # Renders the index page dynamically




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
            
            # Redirect admins to the admin dashboard
            if user.is_admin or user.is_super_admin:
                return redirect(url_for('admin_dashboard'))
            
            # Redirect regular users to home2.html
            return redirect(url_for('home2'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/home2')
def home2():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

    # Retrieve user information
    user = User.query.get(session['user_id'])

    return render_template(
        'home2.html',
        user=user
    )

@app.route("/donate", methods=["GET", "POST"])
def donate():
    user = None
    if "user_id" in session:
        user = get_current_user()  # Retrieve the current logged-in user if available
        app.logger.debug(f"User object: {user}")  # Log the user object to see its attributes
        if user:
            db.session.refresh(user)  # Refresh the user to ensure the latest data from the database

    if request.method == "POST":
        user_id = session.get("user_id")  # Check if a user is logged in
        payment_type = request.form.get("payment_type")  # Get the selected payment type

        # Handle offline donation
        if request.form.get("offline_donation"):
            amount = request.form.get("amount")
            currency = request.form.get("currency")
            donation_date = request.form.get("date_donated")  # Get date from form, if provided

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
            if donation_date:
                try:
                    donation_date = datetime.strptime(donation_date, '%Y-%m-%d').date()
                except ValueError:
                    flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                    return redirect(url_for("donate"))
            else:
                donation_date = date.today()  # Default to today's date if not provided

            # Create a new donation, with or without user association
            donation = Donation(
                user_id=user_id,  # Associate with logged-in user if available
                amount=amount,
                currency=currency,
                donation_date=donation_date,
                payment_type=payment_type  # Save the selected payment type
            )

            try:
                db.session.add(donation)
                db.session.commit()
                flash(f"Thank you for your {payment_type} donation!", "success")
                app.logger.info(f"Donation saved: {donation.amount}, User ID: {user_id}, Type: {payment_type}, Date: {donation_date}")
                return redirect(url_for("donation_success"))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error saving donation: {e}")
                flash("There was an error processing your donation. Please try again.", "danger")
                return redirect(url_for("donate"))


    # Retrieve pledges made by all users
    pledges = db.session.query(Pledge, User).join(User, Pledge.user_id == User.id).all()

    # Render the form again, passing back the donation_date so it can be displayed in the input
    return render_template("donate.html", user=user, pledges=pledges, donation_date=date.today())


@app.route('/recent_donations', methods=['GET', 'POST'])
def recent_donations():
    search_country = request.form.get('search_country', '').strip()  # Get search country from form, with trimming
    search_payment_type = request.form.get('search_payment_type', '').strip()  # Get payment type filter from form

    # Build the query for donations
    query = Donation.query

    # Filter by country if provided
    if search_country:
        query = query.filter(Donation.user.has(country=search_country.lower()))

    # Filter by payment type if provided
    if search_payment_type:
        query = query.filter(Donation.payment_type == search_payment_type.lower())

    # Fetch donations, ordered by donation date
    recent_donations = query.order_by(Donation.donation_date.desc()).all()

    return render_template('recent_donations.html', recent_donations=recent_donations, search_country=search_country, search_payment_type=search_payment_type)



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
    # Initialize search filters as empty
    search_date = None
    search_country = None
    recent_donations = Donation.query.order_by(Donation.donation_date.desc()).all()  # Default query
    
    if request.method == "POST":
        try:
            # Retrieve search parameters
            search_date = request.form.get('search_date')
            search_country = request.form.get('search_country')
            
            # Start with the base query and apply filters
            query = Donation.query.join(User, User.id == Donation.user_id).order_by(Donation.donation_date.desc())
            
            # Apply date filter if provided
            if search_date:
                query = query.filter(Donation.donation_date == datetime.strptime(search_date, '%Y-%m-%d').date())
            
            # Apply country filter if provided
            if search_country:
                query = query.filter(User.country.ilike(f"%{search_country}%"))
            
            # Fetch the filtered donations
            recent_donations = query.all()
        
        except ValueError as e:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
    
    else:
        # Default query for GET request
        recent_donations = Donation.query.order_by(Donation.donation_date.desc()).all()

    # Fetch all users and calculate total donations
    users = User.query.all()
    total_donations = sum(donation.amount for donation in recent_donations)

    return render_template("admin_dashboard.html", 
                           users=users, 
                           recent_donations=recent_donations, 
                           total_donations=total_donations, 
                           search_date=search_date, 
                           search_country=search_country)



#SENDING NOTIFICATIONS(MAIL AND SMS USING AWS)
@app.route("/mail_sms", methods=["GET", "POST"])
def mail_sms():
    if request.method == "POST":
        try:
            # Handle bulk SMS sending
            if "send_bulk_sms" in request.form:
                message = request.form["sms_message"]
                phone_numbers = request.form["phone_numbers"].split(",")  # Split by commas to get a list
                phone_numbers = [num.strip() for num in phone_numbers]  # Remove any extra whitespace
                send_bulk_sms(message, phone_numbers)
                flash("Bulk SMS sent successfully!", "success")

            # Handle bulk email sending
            elif "send_bulk_email" in request.form:
                subject = request.form["email_subject"]
                body = request.form["email_body"]
                recipients = request.form["recipients"].split(",")  # Split by commas to get a list
                recipients = [email.strip() for email in recipients]  # Remove any extra whitespace
                send_bulk_email(subject, body, recipients)
                flash("Bulk email sent successfully!", "success")
                
            return redirect(url_for('admin_dashboard'))
        
        except Exception as e:
            flash("An error occurred: " + str(e), "danger")
    
    return render_template("mail_sms.html")


# Function to send bulk email using AWS SES
def send_bulk_email(subject, body, recipients):
    try:
        response = ses_client.send_email(
            Source='your-email@example.com',  # Replace with your verified SES email
            Destination={'ToAddresses': recipients},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print("Email sent! Message ID:", response['MessageId'])
    except (BotoCoreError, ClientError) as error:
        print(f"An error occurred with SES: {error}")



# Function to send bulk SMS using AWS SNS
def send_bulk_sms(message, phone_numbers):
    try:
        for number in phone_numbers:
            response = sns_client.publish(
                PhoneNumber=number,
                Message=message
            )
            print(f"Message sent to {number} with response: {response}")
    except (BotoCoreError, ClientError) as error:
        print(f"An error occurred with SNS: {error}")



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



#Add Pledges to new Partners and also already-onboarded partners
@app.route('/add_pledge', methods=['GET', 'POST'])
def add_pledge():
    if request.method == 'POST':
        # Handling form submission
        if request.form:
            user_id = request.form['user_id']  # Get the user ID from the form
            pledged_amount = request.form['pledged_amount']
            pledge_currency = request.form['currency']
            medal = request.form.get('medal')  # Get the selected medal from the form

            # Fetch the user from the User table
            user = User.query.get(user_id)

            if user:
                # Update the pledged amount and currency in the User table
                user.pledged_amount = float(pledged_amount)  # Ensure this is a float
                user.pledge_currency = pledge_currency
                user.medal = medal  # Save the selected medal type

                # Commit the changes to the database
                db.session.commit()

                flash('Pledge added successfully! You can login again')
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
            medal = data.get('medal')  # Medal type provided in JSON data


            # Fetch the user from the User table
            user = User.query.get(user_id)

            if user:
                # Update the pledged amount and currency in the User table
                user.pledged_amount = float(pledged_amount)
                user.pledge_currency = pledge_currency
                user.medal = medal  # Save the selected medal type

                # Commit the changes to the database
                db.session.commit()

                return jsonify({'success': True, 'message': 'Pledge added successfully.'})
            else:
                return jsonify({'success': False, 'message': 'User not found.'}), 404

    return render_template('add_pledge.html') 




def get_user_by_id(user_id):
    return User.query.get(user_id)  



#Route to Confirm Partners' Pledges and reset to zero after payment is completed in full
@app.route('/update_pledge/<int:user_id>', methods=['GET', 'POST'])
def update_pledge(user_id):
    if request.method == 'POST':
        # Fetch the user's record from the User table
        user = User.query.filter_by(id=user_id).first()

        if user:
            print(f"Before update - User ID {user_id} - Pledged Amount: {user.pledged_amount}")  # Debugging line

            # Reset pledged amount to zero
            user.pledged_amount = 0

            try:
                db.session.commit()  # Commit the change to the database
                print(f"After update - User ID {user_id} - Pledged Amount: {user.pledged_amount}")  # Debugging line
            except Exception as e:
                print(f"Error committing to database: {e}")
                db.session.rollback()  # Rollback in case of an error

            # Verify if the change was successful
            updated_user = User.query.filter_by(id=user_id).first()
            if updated_user and updated_user.pledged_amount == 0:
                flash(f'Pledge for user {user_id} has been reset to zero!')
            else:
                flash('Error: Unable to reset the pledge amount.', 'error')

        else:
            flash(f'No user found with ID {user_id}.', 'error')
            print(f"No user found with ID {user_id}")  # Debugging line

        # Redirect to the admin dashboard to reflect the updated pledge
        return redirect(url_for('admin_dashboard')) 


    # For GET requests, display the update page with current pledge information
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        print(f"No user found with ID {user_id}.")  # Debugging line
    else:
        print(f"GET request - Current pledge for user {user_id}: {user.pledged_amount}")  # Debugging line
        
    return render_template('update_pledge.html', user=user)




def get_current_pledge(user_id):
    return Pledge.query.filter_by(user_id=user_id).first()




#View Partners Pledges
@app.route('/view_partners_pledges', methods=['GET', 'POST'])
@login_required  
@admin_required 
def view_partners_pledges():
    # Retrieve the search_country from the form if it's a POST request
    search_country = request.form.get('search_country') if request.method == 'POST' else None

    # Filter out admins and apply country filter if search_country is provided
    if search_country:
        users = User.query.filter(User.is_admin == False, User.country.ilike(f"%{search_country}%")).all()
    else:
        users = User.query.filter(User.is_admin == False).all()  # Fetch all non-admin users

    return render_template('view_partners_pledges.html', users=users, search_country=search_country)



#View Partnere Details
@app.route('/view_partners_details', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
@admin_required  # Ensure the user is an admin
def view_partners_details():
    # Retrieve the search_country from the form if it's a POST request
    search_country = request.form.get('search_country') if request.method == 'POST' else None

    # Filter out admins and apply country filter if search_country is provided
    if search_country:
        users = User.query.filter(User.is_admin == False, User.country.ilike(f"%{search_country}%")).all()
    else:
        users = User.query.filter(User.is_admin == False).all()  # Fetch all non-admin users

    return render_template('view_partners_details.html', users=users, search_country=search_country)



#View Admin Details
@app.route('/view_admin_details', methods=['GET', 'POST'])
@login_required  
@admin_required
def view_admin_details():
    # Retrieve the search_country from the form if it's a POST request
    search_country = request.form.get('search_country') if request.method == 'POST' else None

    # Filter out non-admins and apply country filter if search_country is provided
    if search_country:
        admins = User.query.filter(User.is_admin == True, User.country.ilike(f"%{search_country}%")).all()
    else:
        admins = User.query.filter(User.is_admin == True).all()  # Fetch all admin users

    return render_template('view_admin_details.html', admins=admins, search_country=search_country)



# View donations made by the logged-in partner
@app.route('/view_my_donations')
def view_my_donations():
    # Manually check if the user is authenticated (using a session)
    if 'user_id' not in session:
        # If the user is not logged in, redirect them to the login page
        return redirect(url_for('login'))  # Replace 'login' with your actual login route

    # Fetch donations for the logged-in user
    user_id = session['user_id']  # Get user_id from the session
    donations = Donation.query.filter_by(user_id=user_id).all()  # Filter donations based on the logged-in user

    return render_template('view_my_donations.html', donations=donations)




@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403





@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email_or_phone = request.form.get('email_or_phone')
        new_password = request.form.get('new_password')
        
        # Validate email or phone (check if it exists in the database)
        user = User.query.filter((User.email == email_or_phone) | (User.phone == email_or_phone)).first()
        
        if not user:
            flash('Invalid email or phone number', 'error')
            return redirect(url_for('change_password'))
        
        # Hash the new password
        hashed_password = generate_password_hash(new_password)
        
        # Update the password in the database
        try:
            user.password_hash = hashed_password
            db.session.commit()
            flash('Password successfully changed', 'success')
            return redirect(url_for('login'))  # Redirect to login after successful update
        except Exception as e:
            db.session.rollback()
            flash('Error updating password. Please try again.', 'error')
            return redirect(url_for('change_password'))
        
    return render_template('change_password.html')  # Render the password change form





@app.route('/contact')
def contact():
    return render_template('contact.html')  # Renders the contact page



    
@app.route("/select_payment_options", methods=["GET"])
@login_required
def select_payment_options():
    return render_template("select_payment_options.html")


    #http://127.0.0.1:5000/update_user_details?user_id=47


# Load environment variables
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SHEET_API_KEY_PATH')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Define SCOPES (Google Sheets API Scope)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

@app.route('/sync_with_google_sheets', methods=['POST'])
def sync_with_google_sheets():
    # Authenticate using Google service account
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    try:
        # === Step 1: Import Data from Google Sheets ===
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Sheet1!A2:K'  # Assuming data starts at row 2, columns A to K
        ).execute()
        rows = result.get('values', [])

        # Log data from the Google Sheet
        print(f"Synchronizing with Google Sheets: {rows}")  # Log the rows fetched from Google Sheets

        if not rows:
            flash('No data found in the Google Sheet.', 'error')
        else:
            for row in rows:
                # Extract data from the row
                name = row[0] if len(row) > 0 else None
                phone = row[1] if len(row) > 1 else None
                email = row[2] if len(row) > 2 else None
                address = row[3] if len(row) > 3 else None
                country = row[4] if len(row) > 4 else None
                state = row[5] if len(row) > 5 else None
                church_branch = row[6] if len(row) > 6 else None
                birthday_str = row[7] if len(row) > 7 else None
                pledged_amount = row[8] if len(row) > 8 else None
                pledge_currency = row[9] if len(row) > 9 else None

                # Parse birthday if provided
                birthday = None
                if birthday_str:
                    try:
                        birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
                    except ValueError:
                        birthday = None  # Skip invalid dates

                # Use phone number or email as the password
                if phone:
                    password = phone
                elif email:
                    password = email
                else:
                    flash(f"No phone or email available to set as a password for {name}. Skipping user.", "error")
                    continue

                # Check if the user already exists by email
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    flash(f"User with email {email} already exists. Skipping import for {name}.", "warning")
                    continue

                # Create the new user
                new_user = User(
                    name=name,
                    phone=phone,
                    email=email,
                    address=address,
                    country=country,
                    state=state,
                    church_branch=church_branch,
                    birthday=birthday,
                    pledged_amount=pledged_amount,
                    pledge_currency=pledge_currency,
                    is_admin=False,
                    is_super_admin=False
                )
                new_user.set_password(password)  # Hash and set the password

                # Save the user to the database
                db.session.add(new_user)
                db.session.commit()

                # Log user import success
                print(f"User {name} imported successfully.")  # Log each user import

                flash(f"User {name} imported successfully.", "success")

        # === Step 2: Export Data to Google Sheets ===

        # Export partners' pledges data
        users = User.query.filter_by(is_admin=False).all()  # Only select non-admin users
        partners_values = [
            ['Partner Name', 'Role', 'Phone Number', 'Email', 'Country', 'State', 'Local Church', 'Address', 'Birthday', 'Pledged Amount', 'Pledged Currency']
        ]

        for user in users:
            partners_values.append([
                user.name,
                'Admin' if user.is_admin else 'Partner',
                user.phone,
                user.email,
                user.country,
                user.state,
                user.church_branch,
                user.address,
                user.birthday.strftime('%m/%d/%Y') if user.birthday else 'N/A',
                user.pledged_amount,
                user.pledge_currency,
            ])

        partners_body = {'values': partners_values}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Sheet2!A1',
            valueInputOption='RAW',
            body=partners_body
        ).execute()

        # Export donations data
        donations = Donation.query.all()
        donations_values = [
            ['Partner', 'Country', 'State', 'Local Church', 'Amount', 'Currency', 'Payment Type', 'Donation Date']
        ]

        for donation in donations:
            donations_values.append([
                donation.user.name,
                donation.user.country,
                donation.user.state,
                donation.user.church_branch,
                donation.amount,
                donation.currency,
                donation.payment_type,
                donation.donation_date.strftime('%m/%d/%Y') if donation.donation_date else 'N/A',
            ])

        donations_body = {'values': donations_values}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Sheet3!A1',
            valueInputOption='RAW',
            body=donations_body
        ).execute()

        flash('Data synchronization with Google Sheets completed successfully.', 'success')
        return redirect(url_for('view_partners_pledges'))

    except Exception as e:
        flash(f"Error during Google Sheets synchronization: {str(e)}", 'error')
        return redirect(url_for('view_partners_pledges'))




# Route for 'paystack.html'
@app.route('/paystack')
def paystack():
    return render_template('paystack.html')


# Route for thank you page
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/edit-profile-success')
def edit_profile_success():
    return render_template('edit_profile_success.html')





@app.route('/success')
def success():
    return "Pledge added successfully!", 200


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in before accessing the profile edit page
def edit_profile():
    user_id = session.get('user_id')  # Get the user ID from session
    user = db.session.get(User, user_id)  # Use db.session.get() to avoid the deprecated warning

    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        country = request.form.get('country')
        state = request.form.get('state')
        church_branch = request.form.get('church_branch')
        partner_since = request.form.get('partner_since')

        # Update the user profile
        user.email = email
        user.phone = phone
        user.address = address
        user.country = country
        user.state = state
        user.church_branch = church_branch
        user.partner_since = partner_since

        # Commit the changes to the database
        db.session.commit()

        # Flash a success message
        flash('Profile updated successfully!', 'success')

        # Redirect to edit_profile_success.html first
        return redirect(url_for('edit_profile_success'))

    # Render the edit profile page for GET requests
    return render_template('edit_profile.html', user=user)  # Pass user data to the template




# Logout route
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    session.pop('is_super_admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


application = app

if __name__ == "__main__":
    application.run(debug=True)
    