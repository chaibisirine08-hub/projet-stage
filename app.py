import os
from dotenv import load_dotenv

# Load environment variables from .env file at the very start
load_dotenv()

from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User
from routes import main_bp


app = Flask(__name__)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Flask configuration
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-domain-ai-12345")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Veuillez vous connecter pour utiliser le générateur de domaines."
login_manager.login_message_category = "error"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Register routes blueprint
app.register_blueprint(main_bp)


# Ensure database tables are created
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)