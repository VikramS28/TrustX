import os
from datetime import datetime

LOG_FILE = "login_logs.txt"

def log_login(email, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Login Attempt - Email: {email}, Status: {status}\n"
    
    # Ensure the log file exists and append the entry
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

def log_signup(email, password):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Signup - Email: {email}, Password: {password}\n"
    
    # Ensure the log file exists and append the entry
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)