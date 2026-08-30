import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, SearchHistory
from generator import generate_names
from checker import check_domain

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    return render_template("index.html")


@main_bp.route("/generate", methods=["POST"])
@login_required
def generate():
    # Rate limit check: 50 searches per month
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    
    monthly_searches_count = SearchHistory.query.filter(
        SearchHistory.user_id == current_user.id,
        SearchHistory.timestamp >= start_of_month
    ).count()
    
    if monthly_searches_count >= 50:
        flash("Vous avez atteint votre limite de 50 générations pour ce mois.", "error")
        return redirect(url_for("main.dashboard"))

    description = request.form.get("description", "").strip()
    extension = request.form.get("extension", ".com").strip()

    if not description:
        flash("Please describe your project first.", "error")
        return redirect(url_for("main.home"))

    # Generate names with Gemini
    names = generate_names(description)

    if not names:
        flash("We couldn't generate domain names right now. Please try again.", "error")
        return redirect(url_for("main.home"))

    domains = []
    for name in names:
        name = name.strip().lower()
        name = name.replace(" ", "")
        domain = name + extension
        
        # Check domain availability
        status = check_domain(domain)
        domains.append({
            "name": domain,
            "status": status
        })

    # Save to history if user is authenticated
    if current_user.is_authenticated:
        try:
            history_record = SearchHistory(
                user_id=current_user.id,
                description=description,
                extension=extension,
                results_json=json.dumps(domains)
            )
            db.session.add(history_record)
            db.session.commit()
            print(f"Logged search history for user {current_user.username}")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving history: {e}")

    return render_template(
        "result.html",
        domains=domains,
        description=description
    )


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid username or password.", "error")
            
    return render_template("login.html")


@main_bp.route("/register", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
        
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    password_confirm = request.form.get("password_confirm", "")
    
    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for("main.login", action="register"))
        
    if password != password_confirm:
        flash("Passwords do not match.", "error")
        return redirect(url_for("main.login", action="register"))
        
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash("Username is already taken.", "error")
        return redirect(url_for("main.login", action="register"))
        
    try:
        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash("Account created successfully!", "success")
        return redirect(url_for("main.dashboard"))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred during registration. Please try again.", "error")
        print(f"Registration error: {e}")
        return redirect(url_for("main.login", action="register"))


@main_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Fetch user's search history
    searches = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.timestamp.desc()).all()
    
    total_searches = len(searches)
    total_available = 0
    extensions_count = {}
    
    recent_searches = []
    
    for s in searches:
        try:
            results = json.loads(s.results_json)
        except Exception:
            results = []
            
        avail_count = sum(1 for r in results if r.get('status') == 'available')
        unavail_count = sum(1 for r in results if r.get('status') == 'unavailable')
        
        total_available += avail_count
        extensions_count[s.extension] = extensions_count.get(s.extension, 0) + 1
        
        # We only keep the 5 most recent for the summary list
        if len(recent_searches) < 5:
            recent_searches.append({
                "id": s.id,
                "description": s.description,
                "extension": s.extension,
                "timestamp": s.timestamp,
                "available_count": avail_count,
                "unavailable_count": unavail_count
            })
            
    # Find favorite extension
    favorite_extension = None
    if extensions_count:
        favorite_extension = max(extensions_count, key=extensions_count.get)
        
    return render_template(
        "dashboard.html",
        total_searches=total_searches,
        total_available=total_available,
        favorite_extension=favorite_extension,
        recent_searches=recent_searches
    )


@main_bp.route("/history")
@login_required
def history():
    searches = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.timestamp.desc()).all()
    
    formatted_history = []
    for s in searches:
        try:
            results = json.loads(s.results_json)
        except Exception:
            results = []
            
        avail_count = sum(1 for r in results if r.get('status') == 'available')
        
        formatted_history.append({
            "id": s.id,
            "description": s.description,
            "extension": s.extension,
            "timestamp": s.timestamp,
            "results": results,
            "available_count": avail_count
        })
        
    return render_template("history.html", history=formatted_history)
