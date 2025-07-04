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

def load_email_config():
    if all(k in os.environ for k in ["SMTP_SERVER", "SMTP_PORT", "SENDER_EMAIL", "SENDER_PASSWORD"]):
        return {
            "smtp_server": os.environ["SMTP_SERVER"],
            "smtp_port": int(os.environ["SMTP_PORT"]),
            "sender_email": os.environ["SENDER_EMAIL"],
            "sender_password": os.environ["SENDER_PASSWORD"]
        }

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_config.ini")
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if "Email" in config:
            email_config = {
                "smtp_server": config["Email"]["smtp_server"],
                "smtp_port": int(config["Email"]["smtp_port"]),
                "sender_email": config["Email"]["sender_email"],
                "sender_password": config["Email"]["sender_password"]
            }
            print(email_config)  # Debugging: Check loaded credentials
            return email_config
    return None

def send_email_notification(recipient_email, breach_count):
    config = load_email_config()
    if not config:
        print("❌ Email notification failed: Missing configuration. Run the program with '--setup-email' to configure.")
        return False

    subject = "⚠️ SECURITY ALERT: Your Password Was Found in Data Breaches"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #d9534f;">🚨 Password Security Alert</h2>
            <p>The password you checked was found in <strong>{breach_count} data breaches</strong>!</p>
            <p>This means your password is compromised and should be changed immediately on any accounts where you use it.</p>
            <h3 style="color: #5cb85c;">Recommended Actions:</h3>
            <ol>
                <li>Change this password on <strong>ALL</strong> accounts where you use it</li>
                <li>Use unique passwords for each account</li>
                <li>Consider using a password manager</li>
                <li>Enable two-factor authentication where available</li>
            </ol>
            <p style="font-size: 0.9em; color: #777; margin-top: 30px;">
                This is an automated notification from your Password Breach Checker.
            </p>
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = config["sender_email"]
    message["To"] = recipient_email
    message.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"]) as server:
            server.login(config["sender_email"], config["sender_password"])
            server.send_message(message)
        print(f"✅ Security alert sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def setup_email_config():
    print("\n📧 Email Notification Setup")
    smtp_server = input("SMTP Server (e.g., smtp.gmail.com): ")
    smtp_port = input("SMTP Port (e.g., 465): ")
    sender_email = input("Sender Email: ")
    sender_password = getpass("App Password (hidden): ")

    config = configparser.ConfigParser()
    config["Email"] = {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "sender_email": sender_email,
        "sender_password": sender_password
    }

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_config.ini")
    with open(config_path, "w") as f:
        config.write(f)

    print(f"✅ Email configuration saved to {config_path}")
    print("💡 For Gmail, use an App Password: https://myaccount.google.com/apppasswords")

# ------------------------------------
# Password Generation
# ------------------------------------

def generate_password(length=16, include_symbols=True, include_numbers=True, include_lowercase=True, include_uppercase=True):
    chars = ""
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_numbers:
        chars += string.digits
    if include_symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?/"

    if not chars:
        chars = string.ascii_letters + string.digits

    return ''.join(random.choice(chars) for _ in range(length))

def generate_password_suggestions(count=5):
    suggestions = []

    suggestions.append({
        "password": generate_password(16),
        "description": "Strong random password (16 chars)"
    })

    suggestions.append({
        "password": generate_password(20),
        "description": "Extra strong password (20 chars)"
    })

    words = ["apple", "banana", "orange", "grape", "melon", "cherry", "lemon", 
             "kiwi", "peach", "plum", "wolf", "tiger", "eagle", "shark", "bear"]
    memorable = random.sample(words, 3)
    suggestions.append({
        "password": "-".join(memorable) + str(random.randint(100, 999)),
        "description": "Memorable password (words + number)"
    })

    suggestions.append({
        "password": generate_password(16, include_symbols=False),
        "description": "No special characters (for restricted sites)"
    })

    suggestions.append({
        "password": ''.join(random.choice(string.digits) for _ in range(8)),
        "description": "8-digit PIN (for mobile use)"
    })

    return suggestions

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



