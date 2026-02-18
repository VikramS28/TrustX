from flask import Blueprint, render_template, request, jsonify, session
from .models import User, Transaction, db

views = Blueprint('view', __name__)

@views.route('/')
def home():
    return render_template("index.html")

@views.route('/accounttype')
def accounttype():
    return render_template("accounttype.html")

@views.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return "Please sign in first.", 403
    user = User.query.get(user_id)
    if not user:
        return "User not found.", 404
    balance = user.balance if user.balance is not None else 0.0# Ensure User is imported if used
    return render_template('dashboard.html', user=user, balance=balance)

@views.route('/hire')
def hire():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    return render_template("hire.html", user=user)

@views.route('/projectdetails')
def projectdetails():
    return render_template("my_project_details.html")

@views.route('/hire_freelancer', methods=['POST'])
def hire_freelancer():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please sign in to hire a freelancer.'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    data = request.get_json()
    freelancer_name = data.get('freelancer_name')
    rate = float(data.get('rate'))

    if user.balance < rate:
        return jsonify({'success': False, 'message': 'Insufficient balance to hire this freelancer.'}), 400

    # Deduct the rate from the user's balance
    user.balance -= rate

    # Log the transaction
    transaction = Transaction(
        user_id=user.id,
        amount=rate,
        transaction_type='hire',
        status='completed',
        crypto_amount=None,
        crypto_currency=None
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Successfully hired {freelancer_name}!'})