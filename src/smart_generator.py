# ไฟล์: src/smart_generator.py (ฉบับสมบูรณ์ + Prize Prediction)
import random
from collections import Counter

# 1. ระบบวิเคราะห์สถิติ
def analyze_position_weights(raw_numbers):
    if not raw_numbers: return []
    digit_len = len(str(raw_numbers[0]))
    position_stats = [ {d: 0 for d in range(10)} for _ in range(digit_len) ]
    
    for num_str in raw_numbers:
        num_str = str(num_str).strip()
        if len(num_str) != digit_len or not num_str.isdigit(): continue
        for i in range(digit_len):
            position_stats[i][int(num_str[i])] += 1
            
    weights_per_position = []
    for i in range(digit_len):
        weights_per_position.append([position_stats[i][d] for d in range(10)])
    return weights_per_position

# 2. ตัวกรองความสวยงาม
def is_beautiful_number(num_str):
    length = len(num_str)
    # กฎ 1: ห้ามซ้ำติดกันเกิน 2 ตัว
    for i in range(length - 2):
        if num_str[i] == num_str[i+1] == num_str[i+2]: return False
    # กฎ 2: ห้ามซ้ำเกิน 3 ครั้งในชุด
    counts = Counter(num_str)
    for count in counts.values():
        if count > 3: return False
    # กฎ 3: ต้องมีความหลากหลาย
    if length == 6 and len(set(num_str)) < 4: return False
    if length == 3 and len(set(num_str)) < 2: return False
    return True

# 3. ตัวสร้างเลข
def generate_weighted_number(weights_per_position):
    while True:
        generated_digits = []
        REPEAT_PENALTY = 0.5 
        for i in range(len(weights_per_position)):
            current_weights = list(weights_per_position[i])
            if i > 0:
                prev = int(generated_digits[i-1])
                current_weights[prev] *= REPEAT_PENALTY
            try:
                digit = random.choices(range(10), weights=current_weights, k=1)[0]
            except ValueError:
                digit = random.randint(0, 9)
            generated_digits.append(str(digit))
            
        candidate = "".join(generated_digits)
        if is_beautiful_number(candidate): return candidate

# 4. ระบบคำนวณคะแนนโอกาสชนะ
def calculate_winning_chance(candidate_num, weights_main, weights_3=None, weights_2=None):
    if not candidate_num: return 0.0
    s_num = str(candidate_num)
    length = len(s_num)
    
    def get_score(segment, w_set):
        if not w_set or len(segment) != len(w_set): return 0.0
        total = 0
        for i, ch in enumerate(segment):
            my_w = w_set[i][int(ch)]
            max_w = max(w_set[i])
            if max_w > 0: total += (my_w / max_w) * 100
        return total / len(segment)

    score_main = get_score(s_num, weights_main)
    score_3 = get_score(s_num[-3:], weights_3) if length >= 3 and weights_3 else 0
    score_2 = get_score(s_num[-2:], weights_2) if length >= 2 and weights_2 else 0

    if length == 6: return round((score_main*0.5) + (score_3*0.3) + (score_2*0.2), 2)
    elif length == 3: return round((score_main*0.7) + (score_2*0.3), 2)
    else: return round(score_main, 2)

# 🔥 5. ระบบทำนายเกรดรางวัล (อันนี้แหละที่คุณขาดไป)
def predict_prize_grade(candidate_num, weights_dict, weights_3=None, weights_2=None):
    """
    ทำนายเกรดรางวัล (รองรับทั้งรางวัลใหญ่ 1-5 และ เลขท้าย 2/3 ตัว)
    """
    if not candidate_num: return "N/A", 0
    candidate_str = str(candidate_num)
    length = len(candidate_str)
    
    best_grade = "Unknown"
    max_score = -1
    
    # ฟังก์ชันคำนวณความเหมือน (Similarity)
    def calc_sim(n_str, w_set):
        if not w_set or len(n_str) != len(w_set): return 0.0
        tot = 0
        for i, ch in enumerate(n_str):
            mx = max(w_set[i])
            if mx > 0: tot += (w_set[i][int(ch)] / mx) * 100
        return tot / len(n_str)

    # 1. เทียบกับรางวัลใหญ่ (Prize 1-5)
    for grade, w_set in weights_dict.items():
        score = calc_sim(candidate_str, w_set)
        if score > max_score:
            max_score = score
            best_grade = grade
            
    # 2. เทียบกับเลขท้าย 3 ตัว (ถ้ามีข้อมูล)
    if weights_3 and length >= 3:
        tail_3 = candidate_str[-3:]
        score_3 = calc_sim(tail_3, weights_3)
        # ถ้าคะแนนเลขท้าย 3 ตัว สูงกว่ารางวัลใหญ่ -> ให้ทำนายว่าเป็นเลขท้าย
        if score_3 > max_score:
            max_score = score_3
            best_grade = "🧧 เลขท้าย 3 ตัว"

    # 3. เทียบกับเลขท้าย 2 ตัว (ถ้ามีข้อมูล)
    if weights_2 and length >= 2:
        tail_2 = candidate_str[-2:]
        score_2 = calc_sim(tail_2, weights_2)
        # ถ้าคะแนนเลขท้าย 2 ตัว สูงปรี๊ด -> ให้ทำนายว่าเป็นเลขท้าย
        if score_2 > max_score:
            max_score = score_2
            best_grade = "🧧 เลขท้าย 2 ตัว"
            
    return best_grade, max_score