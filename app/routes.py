from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import db, User, Allergy, SearchHistory  # Add SearchHistory import
from app.api_handler import APIHandler
from app.model import predict_new_drug

routes = Blueprint("routes", __name__)
api_handler = APIHandler()  # Initialize API handler

# Home Page
@routes.route("/")
def home():
    return render_template("index.html")

# User Login
@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("routes.dashboard"))
        flash("Invalid email or password", "danger")

    return render_template("login.html")

# User Registration
@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for("routes.register"))

        # Check if the email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("routes.login"))

        # Hash the password and save the new user
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("routes.login"))

    return render_template("register.html")

# User Dashboard
@routes.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.name)

# Search Function (Drug/Disease)
@routes.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        query = request.form.get("query")
        search_type = request.form.get("search_type", "drug")  # Get search type from form
        
        if not query:
            return render_template("search_results.html", message="Please enter a valid query.")

        print(f"Searching for {search_type}: {query}")  # Debug log
        
        try:
            # Call API handler to fetch search results, passing search_type
            results = api_handler.search_drug_or_disease(query, search_type)
            
            # Save search to history
            try:
                search_history = SearchHistory(user_id=current_user.id, query=query)
                db.session.add(search_history)
                db.session.commit()
            except Exception as e:
                print(f"Error saving search history: {str(e)}")
                db.session.rollback()

            return render_template("search_results.html", 
                                  results=results, 
                                  query=query, 
                                  search_type=search_type)
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return render_template("search_results.html", 
                                  message=f"An error occurred while processing your search: {str(e)}",
                                  query=query)

    return render_template("search_results.html", message="Enter a drug or disease name.")

# Drug Prediction Search
@routes.route("/search_drug", methods=["POST"])
@login_required
def search_drug():
    drug_name = request.form.get("drug_name")

    if not drug_name:
        return jsonify({"error": "Drug name is required"}), 400

    prediction = predict_new_drug(drug_name)
    
    return render_template("search_results.html", query=drug_name, results=prediction)

# User Logout
@routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("routes.login"))
