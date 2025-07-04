import hashlib
import requests


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
