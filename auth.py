from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User
from access_control import get_current_user, require_login

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        display_name = request.form["display_name"].strip()
        password = request.form["password"]
        
        # Debug logging
        print(f"Registration attempt for username: {username}, email: {email}")
        
        # Validate input
        if not all([username, email, display_name, password]):
            flash("All fields are required.", "error")
            return render_template("register.html", 
                                username=username, 
                                email=email, 
                                display_name=display_name)
        
        # Validate username format (alphanumeric and underscores only)
        if not username.replace('_', '').isalnum():
            flash("Username can only contain letters, numbers, and underscores.", "error")
            return render_template("register.html", 
                                username=username, 
                                email=email, 
                                display_name=display_name)
        
        # Validate email format
        if '@' not in email or '.' not in email:
            flash("Please enter a valid email address.", "error")
            return render_template("register.html", 
                                username=username, 
                                email=email, 
                                display_name=display_name)
        
        # Validate password strength
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html", 
                                username=username, 
                                email=email, 
                                display_name=display_name)
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return render_template("register.html", 
                                username=username, 
                                email=email, 
                                display_name=display_name)
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("register.html", 
                                username=username, 
                                email=email, 
                                display_name=display_name)
        
        try:
            # Create new user
            user = User(username=username, email=email, display_name=display_name)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Log in the user
            session['user_id'] = user.id
            session['username'] = user.username
            
            flash("Registration successful! Welcome to AI Collab.", "success")
            return redirect(url_for("room.index"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("register.html", 
                                username=username, 
                                email=email, 
                                display_name=display_name)
    
    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        
        # Debug logging
        print(f"Login attempt for username: {username}")
        
        # Validate input
        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html", username=username)
        
        # Check if user exists and password is correct
        try:
            user = User.query.filter_by(username=username).first()
            print(f"User found: {user is not None}")
            
            if user:
                print(f"Password check result: {user.check_password(password)}")
                print(f"User is_active: {user.is_active}")
            
            if user and user.check_password(password):
                if not user.is_active:
                    flash("Your account has been deactivated. Please contact support.", "error")
                    return render_template("login.html", username=username)
                
                # Set session
                session['user_id'] = user.id
                session['username'] = user.username  # For easier access
                
                print(f"Login successful for user: {user.username}")
                flash(f"Welcome back, {user.display_name}!", "success")
                return redirect(url_for("room.index"))
            else:
                # Don't reveal whether username or password was wrong for security
                flash("Invalid username or password.", "error")
                return render_template("login.html", username=username)
        except Exception as e:
            print(f"Database error during login: {e}")
            flash("An error occurred during login. Please try again.", "error")
            return render_template("login.html", username=username)
    
    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for("room.index"))

@auth.route("/profile")
@require_login
def profile():
    user = get_current_user()
    return render_template("profile.html", user=user) 