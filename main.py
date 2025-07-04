import hashlib
import requests
import zxcvbn
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import os
from getpass import getpass
import configparser
import sys
import re

try:
    import zxcvbn
except ImportError:
    print("❌ Missing dependency: zxcvbn. Install it using 'pip install zxcvbn-python'.")
    sys.exit(1)

# ------------------------------------
# Password Utilities
# ------------------------------------

def hash_password(password):
    return hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

def get_hash_prefix(password):
    return hash_password(password)[:5]

def check_breach(prefix):
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 429:
            print("🚫 Rate limit exceeded. Please try again later.")
        else:
            print(f"⚠️ API error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Network error: {e}")
    return None

def is_password_breached(password):
    prefix = get_hash_prefix(password)
    suffixes = check_breach(prefix)

    if suffixes is None:
        return False, 0

    sha1_hash = hash_password(password)
    hash_suffix = sha1_hash[5:]

    lines = suffixes.splitlines()
    for line in lines:
        parts = line.split(":")
        if parts[0] == hash_suffix:
            breach_count = int(parts[1])
            print(f"Found {breach_count} times in breaches.")
            return True, breach_count
    return False, 0

def analyze_password_strength(password):
    result = zxcvbn.zxcvbn(password)
    score = result['score']
    crack_time = result['crack_times_display']['offline_slow_hashing_1e4_per_second']
    feedback = result['feedback']
    strength_labels = {0: "Very Weak", 1: "Weak", 2: "Medium", 3: "Strong", 4: "Very Strong"}
    return {
        'score': score,
        'label': strength_labels[score],
        'crack_time': crack_time,
        'warning': feedback['warning'],
        'suggestions': feedback['suggestions']
    }

# ------------------------------------
# Email Configuration & Notification
# ------------------------------------


# ------------------------------------
# Password Generation
# ------------------------------------


# ------------------------------------
# Email Validation
# ------------------------------------

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# ------------------------------------
# Test Email Sending
# ------------------------------------

def send_test_email():
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    sender_email = "aniketgawande130@gmail.com"
    sender_password = "exgv yskm wwzf fbnm"  # Replace with your App Password
    recipient_email = "anirudhgawande480@gmail.com"

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, "Subject: Test Email\n\nThis is a test email.")
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ------------------------------------
# Main Program
# ------------------------------------

def main():
    print("🔒 Password Breach & Security Checker 🔒")
    print("----------------------------------------")

    if len(sys.argv) > 1 and sys.argv[1] == "--setup-email":
        setup_email_config()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--test-email":
        send_test_email()
        return

    password = getpass("Enter your password (hidden): ")

    print("\n📊 Password Strength Analysis:")
    strength = analyze_password_strength(password)
    print(f"Strength: {strength['label']} ({strength['score']}/4)")
    print(f"Estimated crack time: {strength['crack_time']}")
    if strength['warning']:
        print(f"Warning: {strength['warning']}")
    if strength['suggestions']:
        print("Suggestions:")
        for s in strength['suggestions']:
            print(f"- {s}")

    print("\n🔍 Checking for breaches...")
    is_breached, breach_count = is_password_breached(password)

    if is_breached:
        print("❌ Your password was found in data breaches!")
        send_email = input("\n📧 Receive an email alert? (y/n): ").strip().lower() == 'y'
        if send_email:
            email = input("Enter your email: ").strip()
            if not is_valid_email(email):
                print("❌ Invalid email address.")
                return
            send_email_notification(email, breach_count)

        print("\n🔐 Recommended Passwords:")
        for i, suggestion in enumerate(generate_password_suggestions(), 1):
            print(f"{i}. {suggestion['password']} — {suggestion['description']}")
    else:
        print("✅ Your password was NOT found in any breach.")

if __name__ == "__main__":
    main()




