import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login_page'

# Import models and routes
from src.models.user import User
from src.models.account import Account
from src.routes.api import api_bp

app.register_blueprint(api_bp, url_prefix='/api')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "بيانات تسجيل الدخول غير صحيحة"})
    return send_from_directory(app.static_folder, 'login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))

@app.route("/accounts.html")
@login_required
def accounts_page():
    return send_from_directory(app.static_folder, 'accounts.html')

@app.route("/dashboard.html")
@login_required
def dashboard_page():
    if current_user.role != "editor":
        return redirect(url_for("serve"))
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route("/statistics.html")
@login_required
def statistics_page():
    if current_user.role != "editor":
        return redirect(url_for("serve"))
    return send_from_directory(app.static_folder, 'statistics.html')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))
    
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Create database tables and initial users
with app.app_context():
    db.create_all()
    
    # Add initial users if they don't exist
    if not User.query.filter_by(email="sagedmedhat1@gmail.com").first():
        editor_user = User(email="sagedmedhat1@gmail.com", password="sagma+100", role="editor")
        db.session.add(editor_user)
    if not User.query.filter_by(email="omsaged2014@gmail.com").first():
        user1 = User(email="omsaged2014@gmail.com", password="example", role="user")
        db.session.add(user1)
    if not User.query.filter_by(email="medhatmoh070@gmail.com").first():
        user2 = User(email="medhatmoh070@gmail.com", password="example", role="user")
        db.session.add(user2)
    db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

