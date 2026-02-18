from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Transaction, db
from .logger import log_login, log_signup
from coinbase_commerce.client import Client
from coinbase_commerce.error import WebhookInvalidPayload, APIError  # Add APIError
from web3 import Web3

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
            if 'isGoogleSignIn' in data:
                email = data.get('email')
                first_name = data.get('firstName')
                last_name = data.get('lastName')

                user = User.query.filter_by(email=email).first()
                if user:
                    return jsonify({'success': False, 'message': 'Email already exists'}), 400

                new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=generate_password_hash('google-auth-placeholder')
                )
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                return jsonify({'success': True, 'message': 'Google Sign-In successful'})

        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')

        if len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(firstname) < 3:
            flash('First name must be greater than 2 characters', category='error')
        elif len(lastname) < 3:
            flash('Last name must be greater than 2 characters', category='error')
        elif len(password) < 4:
            flash('Password must be greater than 3 characters', category='error')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists', category='error')
            else:
                log_signup(email, password)
                new_user = User(
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    password=generate_password_hash(password)
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully', category='success')
                session['user_id'] = new_user.id
                return redirect(url_for('view.accounttype'))

    return render_template("signup.html", user=user)

@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully', category='success')
            log_login(email, "Success")
            session['user_id'] = user.id
            return redirect(url_for('view.accounttype'))
        else:
            flash('Invalid email or password', category='error')
            log_login(email, "Failed")

    return render_template("signin.html", user=user)

@auth.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'user_id' not in session:
        flash('Please sign in to deposit funds.', category='error')
        return redirect(url_for('auth.signin'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', category='error')
        return redirect(url_for('auth.signin'))

    if request.method == 'POST':
        client = Client(api_key=current_app.config['COINBASE_COMMERCE_API_KEY'])
        amount_inr = float(request.form.get('amount'))
        if amount_inr <= 0:
            flash('Amount must be greater than 0.', category='error')
            return redirect(url_for('auth.deposit'))

        try:
            client = Client(api_key=current_app.config['COINBASE_COMMERCE_API_KEY'])
            charge_data = {
                'name': 'TrustX Deposit',
                'description': f'Deposit for {user.email}',
                'local_price': {
                    'amount': str(amount_inr),
                    'currency': 'INR'
                },
                'pricing_type': 'fixed_price',
                'metadata': {
                    'user_id': user.id,
                    'transaction_type': 'deposit'
                }
            }
            charge = client.charge.create(**charge_data)
            transaction = Transaction(
                user_id=user.id,
                amount=amount_inr,
                transaction_type='deposit',
                crypto_amount=None,
                crypto_currency=None
            )
            db.session.add(transaction)
            db.session.commit()
            return redirect(charge.hosted_url)
        except APIError as e:
            flash('Failed to create payment: Invalid API key. Please contact support.', category='error')
            return redirect(url_for('auth.deposit'))
        except Exception as e:
            flash(f'Error creating payment: {str(e)}', category='error')
            return redirect(url_for('auth.deposit'))

    return render_template('deposit.html', user=user)

@auth.route('/webhook', methods=['POST'])
def webhook():
    request_data = request.get_data().decode('utf-8')
    signature_header = request.headers.get('X-CC-Webhook-Signature')
    webhook_secret = current_app.config['COINBASE_COMMERCE_WEBHOOK_SECRET']
    try:
        event = Webhook.construct_event(request_data, signature_header, webhook_secret)
    except (WebhookInvalidPayload, Exception) as e:
        return 'Invalid webhook payload or signature', 400

    if event.type == 'charge:confirmed':
        charge = event.data
        user_id = charge.metadata.get('user_id')
        amount_inr = float(charge.pricing.local.amount)
        crypto_amount = float(charge.pricing.crypto.amount)

        user = User.query.get(user_id)
        if user:
            user.balance += amount_inr
            transaction = Transaction.query.filter_by(user_id=user_id, amount=amount_inr, status='pending').first()
            if transaction:
                transaction.status = 'completed'
                transaction.crypto_amount = crypto_amount
                transaction.crypto_currency = charge.pricing.crypto.currency
                db.session.commit()
            else:
                return 'Transaction not found', 404

    return 'Webhook received', 200

@auth.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'user_id' not in session:
        flash('Please sign in to withdraw funds.', category='error')
        return redirect(url_for('auth.signin'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', category='error')
        return redirect(url_for('auth.signin'))

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        if amount <= 0:
            flash('Amount must be greater than 0.', category='error')
            return redirect(url_for('auth.withdraw'))
        if amount > user.balance:
            flash('Insufficient balance.', category='error')
            return redirect(url_for('auth.withdraw'))

        user.balance -= amount
        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            transaction_type='withdrawal',
            status='completed'
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Withdrawal successful!', category='success')
        return redirect(url_for('view.dashboard'))

    return render_template('withdraw.html', user=user)