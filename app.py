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
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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



# Define SCOPES (Google Sheets API Scope)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Route for exporting to Google Sheets
@app.route('/export_to_google_sheets', methods=['POST'])
def export_to_google_sheets():
    # Authenticate using credentials (with the actual path to your JSON file)
    creds = Credentials.from_service_account_file(
        'C:/Users/DELL/Desktop/DCDTRACKER GLOBAL/dominion-city-dtracker-238ba4b6c99a.json', scopes=SCOPES)  # Corrected file path
   

    # Create a Sheets API service
    service = build('sheets', 'v4', credentials=creds)

    # ID of your Google Sheet (use the ID from the provided URL)
    SPREADSHEET_ID = '1EHceFWYA9P8uZXnkkDUFmulrcafXwBjwhVaEbOZh0mc'  # Your actual Spreadsheet ID

    # Fetch data from the database (assuming you have a User model and you're querying users from your database)
    users = User.query.all()

    # Prepare data for Google Sheets
    values = [
        ['Partner Name', 'Role', 'Phone Number', 'Email', 'Country', 'State', 'Local Church', 'Address', 'Birthday', 'Pledged Amount', 'Pledged Currency']  # Column headers
    ]

    # Add actual user data to the values list
    for user in users:
        values.append([
            user.name,          # Partner Name
            'Admin' if user.is_admin else 'Partner',  # Convert True/False to 'admin' or 'partner'
            user.phone,         # Phone
            user.email,         # Email
            user.country,       # Country
            user.state,         # State
            user.church_branch, # Local Church (assuming it's called 'church_branch')
            user.address,       # Address
            user.birthday.strftime('%m/%d/%Y') if user.birthday else 'N/A' , # Birthday (formatted as needed)
            user.pledged_amount,
            user.pledge_currency,

        ])

    # Prepare the data for the API request
    body = {
        'values': values  # The actual data to be written to the sheet
    }

    # Call the Sheets API to write data to the sheet
    sheet = service.spreadsheets()
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID, 
        range='Sheet1!A1', 
        valueInputOption='RAW', 
        body=body
    ).execute()

    # After successful export, redirect back to the view page
    return redirect(url_for('view_partners_pledges'))





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
    medal = db.Column(db.String(100), nullable=True)  


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




@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)  # Assuming `User` is your user table


#Partner can update their details after admin registered them but admin cannot update them here@app.route('/update-details', methods=['GET', 'POST'])
@login_required
def update_user_details():
    user = current_user  # Get the logged-in user

    if request.method == 'POST':
        # Get new values from the form
        user.phone = request.form['phone']
        user.email = request.form['email']
        user.address = request.form['address']
        user.country = request.form['country']
        user.state = request.form['state']
        user.church_branch = request.form['church_branch']
        user.birthday = datetime.strptime(request.form['birthday'], "%Y-%m-%d") if request.form['birthday'] else None

        db.session.commit()  # Commit changes to the database
        flash("Your details have been updated!", "success")
        return redirect(url_for('profile'))  # Redirect to user's profile or dashboard

    return render_template('update_user.html', user=user)


# Home route
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/home2')
def home2():
    return render_template('home2.html')



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



#Partner Donation
@app.route("/donate", methods=["GET", "POST"])
@login_required
def donate():
    user = get_current_user()  # Retrieve the current logged-in user
    app.logger.debug(f"User object: {user}")  # Log the user object to see its attributes

    # Ensure the user object has the latest pledge data, including the medal
    db.session.refresh(user)  # Refresh the user to make sure we have the latest data from the database

    if request.method == "POST":
        user_id = session.get("user_id")

        if request.form.get("offline_donation"):
            # User is entering an offline donation amount
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
                    # Ensure the entered date is parsed correctly into a date object
                    donation_date = datetime.strptime(donation_date, '%Y-%m-%d').date()
                except ValueError:
                    flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                    return redirect(url_for("donate"))
            else:
                donation_date = date.today()  # Default to today's date if not provided

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

    # Retrieve all pledges made by users from the database by joining User and Pledge
    pledges = db.session.query(Pledge, User).join(User, Pledge.user_id == User.id).all()

    # Render the form again, passing back the donation_date so it can be displayed in the input
    return render_template("donate.html", user=user, pledges=pledges, donation_date=date.today())




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



#Add Pledges to new Partners and also already onboarded partners
# Route to add Pledge to Partners
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



#Route to Update Partners' Pledgee
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




#Send notifications
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Construct the email body
        email_body = f"Name: {name}\nEmail: {email}\n\nMessage: {message}"

        # The recipient email is taken from the form (can be dynamic based on the form as well)
        recipient_email = 'admin@example.com'  # Replace with your desired recipient email

        try:
            # Send email using SES
            response = ses_client.send_email(
                Source=SENDER_EMAIL,
                Destination={
                    'ToAddresses': [recipient_email],
                },
                Message={
                    'Subject': {
                        'Data': subject,
                    },
                    'Body': {
                        'Text': {
                            'Data': email_body,
                        },
                    },
                },
            )

            # Print the response for debugging (optional)
            print(f"Email sent! Message ID: {response['MessageId']}")

            # Redirect to thank you page
            return redirect(url_for('thank_you'))

        except NoCredentialsError:
            print("Credentials not found!")
            # Handle the error or redirect to an error page if needed
            return "Error: No credentials found to send email."

    return render_template('contact.html')


    
@app.route("/select_payment_options", methods=["GET"])
@login_required
def select_payment_options():
    return render_template("select_payment_options.html")



@app.route('/update_user_details', methods=['GET', 'POST'])
def update_user_details():
    user_id = request.args.get('user_id')  # Retrieve the user_id from the query parameter
    if user_id:
        user = User.query.get(user_id)  # Fetch user from the database by ID
        if user:
            if request.method == 'POST':
                # Handling the form data to update the user's details
                name = request.form.get('name')
                email = request.form.get('email')
                phone = request.form.get('phone')
                address = request.form.get('address')
                country = request.form.get('country')
                state = request.form.get('state')
                church_branch = request.form.get('church_branch')
                birthday = request.form.get('birthday')

                # Update user details
                user.name = name
                user.email = email
                user.phone = phone
                user.address = address
                user.country = country
                user.state = state
                user.church_branch = church_branch
                user.birthday = birthday

                # Commit the changes to the database
                db.session.commit()
                flash('Your details have been updated successfully!', 'success')
                return redirect(url_for('login'))  # Redirect after successful update

            return render_template('update_user_details.html', user=user)  # Render the form pre-filled with user details
        else:
            flash('User not found', 'error')
            return redirect(url_for('index'))  # Redirect if user not found
    else:
        flash('User ID is missing', 'error')
        return redirect(url_for('index'))  # Redirect if user_id is not provided
    
    #http://127.0.0.1:5000/update_user_details?user_id=47
    


# Route for 'paystack.html'
@app.route('/paystack')
def paystack():
    return render_template('paystack.html')


# Route for thank you page
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')




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


application = app

if __name__ == "__main__":
    application.run(debug=True)


















