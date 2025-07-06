from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from flask_bcrypt import generate_password_hash
from src.models.account import Account
from src.models.user import User
from src.main import db

api_bp = Blueprint("api", __name__)

@api_bp.route("/user-role", methods=["GET"])
@login_required
def get_user_role():
    return jsonify({"role": current_user.role})

@api_bp.route("/accounts", methods=["GET"])
@login_required
def get_accounts():
    accounts = Account.query.all()
    return jsonify([account.to_dict() for account in accounts])

@api_bp.route("/save-accounts", methods=["POST"])
@login_required
def save_accounts():
    if current_user.role != "editor":
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    data = request.get_json()
    accounts_data = data.get("accounts", [])
    
    try:
        # Clear existing accounts and add new ones
        db.session.query(Account).delete()
        for account_data in accounts_data:
            account = Account(
                subject=account_data["subject"],
                price=account_data["price"]
            )
            account.is_paid = account_data.get("paid", False)
            db.session.add(account)
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route("/accounts/<int:account_id>/toggle", methods=["POST"])
@login_required
def toggle_account_payment(account_id):
    account = Account.query.get_or_404(account_id)
    account.is_paid = not account.is_paid
    
    try:
        db.session.commit()
        return jsonify({"success": True, "is_paid": account.is_paid})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route("/statistics", methods=["GET"])
@login_required
def get_statistics():
    if current_user.role != "editor":
        return jsonify({"error": "Unauthorized"}), 403
    
    accounts = Account.query.all()
    
    paid_total = sum(account.price for account in accounts if account.is_paid)
    unpaid_total = sum(account.price for account in accounts if not account.is_paid)
    total_amount = paid_total + unpaid_total
    
    # Group by subjects
    subjects_data = {}
    for account in accounts:
        if account.subject in subjects_data:
            subjects_data[account.subject] += account.price
        else:
            subjects_data[account.subject] = account.price
    
    return jsonify({
        "paid_total": paid_total,
        "unpaid_total": unpaid_total,
        "total_amount": total_amount,
        "subjects_data": subjects_data
    })

@api_bp.route("/users", methods=["GET"])
@login_required
def get_users():
    if current_user.role != "editor":
        return jsonify({"error": "Unauthorized"}), 403
    
    users = User.query.all()
    return jsonify([{
        "id": user.id,
        "email": user.email,
        "role": user.role
    } for user in users])

@api_bp.route("/update-user", methods=["POST"])
@login_required
def update_user():
    if current_user.role != "editor":
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    data = request.get_json()
    old_email = data.get("old_email")
    new_email = data.get("new_email")
    new_password = data.get("new_password")
    
    user = User.query.filter_by(email=old_email).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    try:
        if new_email and new_email != user.email:
            # Check if new email already exists
            if User.query.filter_by(email=new_email).first():
                return jsonify({"success": False, "message": "New email already in use"}), 400
            user.email = new_email
        
        if new_password:
            user.password_hash = generate_password_hash(new_password).decode("utf-8")
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

