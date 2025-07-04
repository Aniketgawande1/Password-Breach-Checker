import os
import smtplib
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass


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

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None