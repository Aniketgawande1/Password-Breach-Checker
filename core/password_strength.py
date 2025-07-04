import zxcvbn

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
