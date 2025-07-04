import random
import string  # ✅ Required for string.ascii_lowercase, string.digits, etc.

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
