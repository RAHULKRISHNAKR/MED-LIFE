from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import db, User, Allergy, SearchHistory, UserMedication, UserDisease
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
            results = api_handler.search_drug_or_disease(query, search_type)
            
            # Save search to history (updated keyword)
            try:
                search_history = SearchHistory(user_id=current_user.id, search_query=query)
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

# User Profile Page
@routes.route("/profile")
@login_required
def profile():
    allergies = Allergy.query.filter_by(user_id=current_user.id).all()
    medications = UserMedication.query.filter_by(user_id=current_user.id).order_by(UserMedication.start_date.desc()).all()
    diseases = UserDisease.query.filter_by(user_id=current_user.id).order_by(UserDisease.diagnosed_date.desc()).all()
    search_history = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.timestamp.desc()).all()
    
    return render_template(
        "profile.html", 
        allergies=allergies, 
        medications=medications, 
        diseases=diseases, 
        search_history=search_history
    )

# Add Allergy
@routes.route("/add_allergy", methods=["POST"])
@login_required
def add_allergy():
    drug_name = request.form.get("drug_name")
    reaction = request.form.get("reaction")
    
    if not drug_name:
        flash("Please enter a drug or substance name", "danger")
        return redirect(url_for("routes.profile"))
    
    new_allergy = Allergy(
        user_id=current_user.id,
        drug_name=drug_name,
        reaction=reaction
    )
    
    try:
        db.session.add(new_allergy)
        db.session.commit()
        flash("Allergy added successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding allergy: {str(e)}", "danger")
    
    return redirect(url_for("routes.profile"))

# Delete Allergy
@routes.route("/delete_allergy/<int:allergy_id>", methods=["POST"])
@login_required
def delete_allergy(allergy_id):
    allergy = Allergy.query.get_or_404(allergy_id)
    
    # Ensure the allergy belongs to the current user
    if allergy.user_id != current_user.id:
        flash("You don't have permission to delete this allergy", "danger")
        return redirect(url_for("routes.profile"))
    
    try:
        db.session.delete(allergy)
        db.session.commit()
        flash("Allergy deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting allergy: {str(e)}", "danger")
    
    return redirect(url_for("routes.profile"))

# Add Medication
@routes.route("/add_medication", methods=["POST"])
@login_required
def add_medication():
    medication_name = request.form.get("medication_name")
    dosage = request.form.get("dosage")
    frequency = request.form.get("frequency")
    notes = request.form.get("notes")
    
    if not medication_name:
        flash("Please enter a medication name", "danger")
        return redirect(url_for("routes.profile"))
    
    new_medication = UserMedication(
        user_id=current_user.id,
        medication_name=medication_name,
        dosage=dosage,
        frequency=frequency,
        notes=notes
    )
    
    try:
        db.session.add(new_medication)
        db.session.commit()
        flash("Medication added successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding medication: {str(e)}", "danger")
    
    return redirect(url_for("routes.profile"))

# Toggle Medication Active Status
@routes.route("/toggle_medication/<int:medication_id>", methods=["POST"])
@login_required
def toggle_medication(medication_id):
    medication = UserMedication.query.get_or_404(medication_id)
    
    # Ensure the medication belongs to the current user
    if medication.user_id != current_user.id:
        flash("You don't have permission to update this medication", "danger")
        return redirect(url_for("routes.profile"))
    
    try:
        medication.active = not medication.active
        db.session.commit()
        status = "active" if medication.active else "inactive"
        flash(f"Medication marked as {status}", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating medication: {str(e)}", "danger")
    
    return redirect(url_for("routes.profile"))

# Delete Medication
@routes.route("/delete_medication/<int:medication_id>", methods=["POST"])
@login_required
def delete_medication(medication_id):
    medication = UserMedication.query.get_or_404(medication_id)
    
    # Ensure the medication belongs to the current user
    if medication.user_id != current_user.id:
        flash("You don't have permission to delete this medication", "danger")
        return redirect(url_for("routes.profile"))
    
    try:
        db.session.delete(medication)
        db.session.commit()
        flash("Medication deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting medication: {str(e)}", "danger")
    
    return redirect(url_for("routes.profile"))

# Add Disease
@routes.route("/add_disease", methods=["POST"])
@login_required
def add_disease():
    disease_name = request.form.get("disease_name")
    status = request.form.get("status")
    notes = request.form.get("notes")
    
    if not disease_name:
        flash("Please enter a condition name", "danger")
        return redirect(url_for("routes.profile"))
    
    new_disease = UserDisease(
        user_id=current_user.id,
        disease_name=disease_name,
        status=status,
        notes=notes
    )
    
    try:
        db.session.add(new_disease)
        db.session.commit()
        flash("Health condition added successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding health condition: {str(e)}", "danger")
    
    return redirect(url_for("routes.profile"))

# Update Disease Status
@routes.route("/update_disease_status/<int:disease_id>", methods=["POST"])
@login_required
def update_disease_status(disease_id):
    disease = UserDisease.query.get_or_404(disease_id)
    
    # Ensure the disease belongs to the current user
    if disease.user_id != current_user.id:
        flash("You don't have permission to update this condition", "danger")
        return redirect(url_for("routes.profile"))
    
    new_status = request.form.get("status")
    if not new_status:
        flash("Status is required", "danger")
        return redirect(url_for("routes.profile"))
    
    try:
        disease.status = new_status
        db.session.commit()
        flash("Condition status updated successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating condition status: {str(e)}", "danger")
    
    return redirect(url_for("routes.profile"))

# Delete Disease
@routes.route("/delete_disease/<int:disease_id>", methods=["POST"])
@login_required
def delete_disease(disease_id):
    disease = UserDisease.query.get_or_404(disease_id)
    
    # Ensure the disease belongs to the current user
    if disease.user_id != current_user.id:
        flash("You don't have permission to delete this condition", "danger")
        return redirect(url_for("routes.profile"))
    
    try:
        db.session.delete(disease)
        db.session.commit()
        flash("Health condition deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting health condition: {str(e)}", "danger")
    
    return redirect(url_for("routes.profile"))

# Clear Search History
@routes.route("/clear_search_history", methods=["POST"])
@login_required
def clear_search_history():  # Renamed function for consistency
    try:
        SearchHistory.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash("Search history cleared successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error clearing search history: {str(e)}", "danger")
    
    return redirect(url_for("routes.profile"))

# User Logout
@routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("routes.login"))
