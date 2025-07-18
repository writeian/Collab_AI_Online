from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User
from access_control import get_current_user, require_login
import datetime
import secrets

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Required fields
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        full_name = request.form["full_name"].strip()
        display_name = request.form["display_name"].strip()
        password = request.form["password"]
        
        # Optional fields
        institution = request.form.get("institution", "").strip()
        department = request.form.get("department", "").strip()
        research_area = request.form.get("research_area", "").strip()
        role = request.form.get("role", "").strip()
        primary_use_case = request.form.get("primary_use_case", "").strip()
        team_size = request.form.get("team_size", "").strip()
        heard_from = request.form.get("heard_from", "").strip()
        receive_updates = request.form.get("receive_updates") == "1"
        contact_for_research = request.form.get("contact_for_research") == "1"
        
        # Debug logging
        # print(f"Registration attempt for username: {username}, email: {email}")
        
        # Validate required input
        if not all([username, email, full_name, display_name, password]):
            flash("All required fields are needed.", "error")
            return render_template("register.html", 
                                username=username, 
                                email=email,
                                full_name=full_name,
                                display_name=display_name,
                                institution=institution,
                                department=department,
                                research_area=research_area,
                                role=role,
                                primary_use_case=primary_use_case,
                                team_size=team_size,
                                heard_from=heard_from,
                                receive_updates=receive_updates,
                                contact_for_research=contact_for_research)
        
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
            user = User()
            user.username = username
            user.email = email
            user.full_name = full_name
            user.display_name = display_name
            user.institution = institution
            user.department = department
            user.research_area = research_area
            user.role = role
            user.primary_use_case = primary_use_case
            user.team_size = team_size
            user.heard_from = heard_from
            user.receive_updates = receive_updates
            user.contact_for_research = contact_for_research
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
            print(f"Registration error: {e}")
            flash(f"An error occurred during registration: {str(e)}", "error")
            return render_template("register.html", 
                                username=username, 
                                email=email,
                                full_name=full_name,
                                display_name=display_name,
                                institution=institution,
                                department=department,
                                research_area=research_area,
                                role=role,
                                primary_use_case=primary_use_case,
                                team_size=team_size,
                                heard_from=heard_from,
                                receive_updates=receive_updates,
                                contact_for_research=contact_for_research)
    
    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        
        # Debug logging
        # print(f"Login attempt for username: {username}")
        
        # Validate input
        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html", username=username)
        
        # Check if user exists and password is correct
        try:
            user = User.query.filter_by(username=username).first()
            # print(f"User found: {user is not None}")
            
            if user and user.check_password(password):
                if not user.is_active:
                    flash("Your account has been deactivated. Please contact support.", "error")
                    return render_template("login.html", username=username)
                
                # Set session
                session['user_id'] = user.id
                session['username'] = user.username  # For easier access
                
                # print(f"Login successful for user: {user.username}")
                flash(f"Welcome back, {user.display_name}!", "success")
                return redirect(url_for("room.index"))
            else:
                # Don't reveal whether username or password was wrong for security
                flash("Invalid username or password.", "error")
                return render_template("login.html", username=username)
        except Exception as e:
            # print(f"Database error during login: {e}")
            flash("An error occurred during login. Please try again.", "error")
            return render_template("login.html", username=username)
    
    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for("room.index"))

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"].strip()
        
        if not email:
            flash("Please enter your email address.", "error")
            return render_template("forgot_password.html", email=email)
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            db.session.commit()
            
            # In a real app, you would send an email here
            # For now, we'll just show the reset link
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash(f"Password reset link: {reset_url}", "success")
        else:
            flash("If an account with that email exists, a reset link has been sent.", "info")
        
        return redirect(url_for("auth.login"))
    
    return render_template("forgot_password.html")

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Find user by reset token
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or user.reset_token_expiry < datetime.datetime.utcnow():
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("reset_password.html")
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("reset_password.html")
        
        # Update password and clear reset token
        user.set_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash("Password has been reset successfully. You can now login.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("reset_password.html")

@auth.route("/profile")
@require_login
def profile():
    user = get_current_user()
    return render_template("profile.html", user=user) 