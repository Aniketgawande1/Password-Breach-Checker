# import sys
# from getpass import getpass
# from core.breach_checker import is_password_breached
# from core.password_strength import analyze_password_strength
# from core.email_alert import send_email_notification, setup_email_config
# from core.password_generator import generate_password_suggestions
# from core.utils import is_valid_email
# # ------------------------------------
# # Main Program
# # ------------------------------------

# def main():
#     print("🔒 Password Breach & Security Checker 🔒")
#     print("----------------------------------------")

#     if len(sys.argv) > 1 and sys.argv[1] == "--setup-email":
#         setup_email_config()
#         return

#     if len(sys.argv) > 1 and sys.argv[1] == "--test-email":
#         send_test_email()
#         return

#     password = getpass("Enter your password (hidden): ")

#     print("\n📊 Password Strength Analysis:")
#     strength = analyze_password_strength(password)
#     print(f"Strength: {strength['label']} ({strength['score']}/4)")
#     print(f"Estimated crack time: {strength['crack_time']}")
#     if strength['warning']:
#         print(f"Warning: {strength['warning']}")
#     if strength['suggestions']:
#         print("Suggestions:")
#         for s in strength['suggestions']:
#             print(f"- {s}")

#     print("\n🔍 Checking for breaches...")
#     is_breached, breach_count = is_password_breached(password)

#     if is_breached:
#         print("❌ Your password was found in data breaches!")
#         send_email = input("\n📧 Receive an email alert? (y/n): ").strip().lower() == 'y'
#         if send_email:
#             email = input("Enter your email: ").strip()
#             if not is_valid_email(email):
#                 print("❌ Invalid email address.")
#                 return
#             send_email_notification(email, breach_count)

#         print("\n🔐 Recommended Passwords:")
#         for i, suggestion in enumerate(generate_password_suggestions(), 1):
#             print(f"{i}. {suggestion['password']} — {suggestion['description']}")
#     else:
#         print("✅ Your password was NOT found in any breach.")

# if __name__ == "__main__":
#     main()



import sys

from getpass import getpass
from core.breach_checker import is_password_breached
from core.password_strength import analyze_password_strength
from core.email_alert import send_email_notification, setup_email_config
from core.password_generator import generate_password_suggestions
from core.utils import is_valid_email

def main():
    print("🔐 Password Breach & Strength Checker 🔐")

    if len(sys.argv) > 1:
        if sys.argv[1] == "--setup-email":
            setup_email_config()
            return

    password = getpass("Enter your password: ")

    print("\n📊 Password Strength:")
    strength = analyze_password_strength(password)
    print(f"Strength: {strength['label']} ({strength['score']}/4)")
    print(f"Crack time: {strength['crack_time']}")
    if strength["warning"]:
        print(f"Warning: {strength['warning']}")
    for s in strength["suggestions"]:
        print(f"- {s}")

    print("\n🔍 Checking for breach...")
    breached, count = is_password_breached(password)
    if breached:
        print(f"❌ Found in {count} breaches!")
        choice = input("Send email alert? (y/n): ").lower()
        if choice == 'y':
            email = input("Enter your email: ")
            if is_valid_email(email):
                send_email_notification(email, count)
            else:
                print("❌ Invalid email.")
        print("\n🔑 Recommended Passwords:")
        for i, pwd in enumerate(generate_password_suggestions(), 1):
            print(f"{i}. {pwd['password']} — {pwd['description']}")
    else:
        print("✅ Password not found in breaches.")

if __name__ == "__main__":
    main()
