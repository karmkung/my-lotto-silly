# ไฟล์: main.py
import sys
from src.data_loader import load_lotto_history
from src.dna_engine import get_dna, check_virgin_status
from src.smart_generator import (
    analyze_position_weights, 
    generate_weighted_number, 
    calculate_winning_chance
)

# ---------------------------------------------------------
# โหลดข้อมูล
# ---------------------------------------------------------
print("⏳ กำลังโหลดฐานข้อมูล...")
history_buckets = load_lotto_history()

if history_buckets is None:
    print("❌ เกิดข้อผิดพลาดในการโหลดข้อมูล โปรดตรวจสอบไฟล์ CSV")
    sys.exit()

# ---------------------------------------------------------
# ฟังก์ชันโหมด [1]: ตรวจสอบเลข
# ---------------------------------------------------------
def mode_check_numbers():
    print("\n" + "="*50)
    print("🔎 โหมดตรวจสอบประวัติเลข (Check Virgin)")
    print("="*50)
    
    while True:
        user_input = input("\n👉 กรอกเลขที่ต้องการเช็ค (หรือพิมพ์ 'exit' เพื่อออก): ").strip()
        if user_input.lower() == 'exit': break
        if not user_input.isdigit(): continue

        dna = get_dna(user_input)
        print(f"🧬 DNA Code: {dna}")
        
        found_in = []
        if not check_virgin_status(dna, history_buckets.get('prize_1', set())): found_in.append("รางวัลที่ 1")
        if not check_virgin_status(dna, history_buckets.get('prize_2', set())): found_in.append("รางวัลที่ 2")
        if not check_virgin_status(dna, history_buckets.get('prize_3', set())): found_in.append("รางวัลที่ 3")
        if not check_virgin_status(dna, history_buckets.get('prize_4', set())): found_in.append("รางวัลที่ 4")
        if not check_virgin_status(dna, history_buckets.get('prize_5', set())): found_in.append("รางวัลที่ 5")
        if not check_virgin_status(dna, history_buckets.get('prize_tails', set())): found_in.append("เลขท้าย")

        print("-" * 30)
        if not found_in:
            print(f"✅ VIRGIN! เลข {user_input} ไม่เคยออกรางวัลใดๆ มาก่อน")
        else:
            print(f"❌ USED! เลข {user_input} เคยออกรางวัลแล้วในกลุ่ม: {', '.join(found_in)}")
        print("-" * 30)

# ---------------------------------------------------------
# ฟังก์ชันโหมด [2]: โรงงานผลิตเลข (Best Probability Selection)
# ---------------------------------------------------------
def mode_generate_numbers():
    print("\n" + "="*95)
    print("🤖 โหมด AI คัดตัวท็อป (เลือกเฉพาะเลขที่ค่าสถิติสูงสุด)")
    print("   Concept: เลขใหม่ที่ได้ ต้องมาจากความน่าจะเป็นของสถิติเดิมเท่านั้น!")
    print("="*95)
    
    # 1. เตรียมสถิติ (แม่พิมพ์)
    w_p1 = analyze_position_weights(history_buckets.get('raw_prize_1', []))
    w_p2 = analyze_position_weights(history_buckets.get('raw_prize_2', []))
    w_p3 = analyze_position_weights(history_buckets.get('raw_prize_3', []))
    w_p4 = analyze_position_weights(history_buckets.get('raw_prize_4', []))
    w_p5 = analyze_position_weights(history_buckets.get('raw_prize_5', []))
    w_3tail = analyze_position_weights(history_buckets.get('raw_three', []))
    w_2tail = analyze_position_weights(history_buckets.get('raw_two', []))
    w_main = analyze_position_weights(history_buckets['all_raw_prizes'])
    
    # Emergency Weights (เผื่อข้อมูลพัง)
    w_emergency_6 = [[1]*10 for _ in range(6)]
    w_emergency_3 = [[1]*10 for _ in range(3)]
    w_emergency_2 = [[1]*10 for _ in range(2)]

    production_lines = [
        ("🥇 รางวัลที่ 1", w_p1, 6, 'prize_1'),
        ("🥈 รางวัลที่ 2", w_p2, 6, 'prize_2'),
        ("🥉 รางวัลที่ 3", w_p3, 6, 'prize_3'),
        ("4️⃣  รางวัลที่ 4", w_p4, 6, 'prize_4'),
        ("5️⃣  รางวัลที่ 5", w_p5, 6, 'prize_5'),
        ("🧧 เลขท้าย 3 ตัว", w_3tail, 3, 'prize_tails'),
        ("🧧 เลขท้าย 2 ตัว", w_2tail, 2, 'prize_tails')
    ]

    print("✅ เดินเครื่องจักร... กำลังเฟ้นหา 'หัวกะทิ' จากผู้สมัครนับหมื่นตัวเลข...\n")
    
    for title, weight_template, digit_len, check_bucket_key in production_lines:
        print(f"🏭 กำลังคัดเลือก: {title} ...")
        
        current_w = weight_template
        data_source_mode = "Normal"
        
        # Fallback Logic
        if not current_w or len(current_w) == 0:
            current_w = w_main
            data_source_mode = "Backup"
            if not current_w or len(current_w) == 0:
                if digit_len == 6: current_w = w_emergency_6
                elif digit_len == 3: current_w = w_emergency_3
                elif digit_len == 2: current_w = w_emergency_2
                data_source_mode = "Emergency"

        # บ่อพักข้อมูล (Candidate Pools)
        pool_new = [] # บ่อเลขใหม่
        pool_old = [] # บ่อเลขเก่า
        
        # 🔥 สุ่มสร้างเยอะๆ แล้วค่อยคัดตัวที่คะแนนดีที่สุด (Best of 2000)
        attempts = 0
        BATCH_SIZE = 2000 
        
        while attempts < BATCH_SIZE:
            attempts += 1
            
            # 1. สร้างเลขจากแม่พิมพ์สถิติ (weighted generation)
            candidate = generate_weighted_number(current_w)
            if len(candidate) > digit_len: candidate = candidate[-digit_len:]
            if len(candidate) != digit_len: continue
            
            # 2. วิเคราะห์ประวัติ
            dna = get_dna(candidate)
            is_new = False
            path_comment = ""
            
            if data_source_mode == "Emergency":
                path_comment = "(Random)"
                is_new = True
            elif digit_len == 6:
                past_history = []
                if check_virgin_status(dna, history_buckets.get('prize_1', set())) is False: past_history.append("1")
                if check_virgin_status(dna, history_buckets.get('prize_2', set())) is False: past_history.append("2")
                if check_virgin_status(dna, history_buckets.get('prize_3', set())) is False: past_history.append("3")
                if check_virgin_status(dna, history_buckets.get('prize_4', set())) is False: past_history.append("4")
                if check_virgin_status(dna, history_buckets.get('prize_5', set())) is False: past_history.append("5")
                
                if len(past_history) > 0:
                    is_new = False # เก่า
                    if "1" in past_history: path_comment = "(เคยออกที่ 1)"
                    else: path_comment = f"(เคยออกที่ {','.join(past_history)})"
                else:
                    is_new = True # ใหม่
                    path_comment = "(สถิติสูง แต่ไม่เคยออก)"
            else:
                 # เลขท้าย
                 if not check_virgin_status(dna, history_buckets.get('prize_tails', set())):
                     is_new = False
                     path_comment = "(เคยออก)"
                 else:
                     is_new = True
                     path_comment = "(ใหม่)"

            # 3. Filter กฎเหล็ก
            # ห้ามซ้ำรางวัลตัวเอง (ยกเว้นโหมดฉุกเฉิน)
            if digit_len == 6 and data_source_mode != "Emergency":
                target_bucket = history_buckets.get(check_bucket_key, set())
                if target_bucket and not check_virgin_status(dna, target_bucket):
                    continue # ตัดทิ้งเลยถ้าซ้ำตำแหน่งเดิม

            # 4. ให้คะแนนความน่าจะเป็น (Probability Score)
            # ใช้แม่พิมพ์ปัจจุบันเทียบเลย ว่าตรงสเปคแค่ไหน
            score = calculate_winning_chance(candidate, current_w, w_3tail, w_2tail)
            
            # เก็บลงบ่อพัก
            item = {'num': candidate, 'score': score, 'path': path_comment}
            if is_new:
                pool_new.append(item)
            else:
                pool_old.append(item)

        # --- คัดเลือกตัวท็อป (Selection Phase) ---
        # เรียงคะแนนจากมากไปน้อย
        pool_new.sort(key=lambda x: x['score'], reverse=True)
        pool_old.sort(key=lambda x: x['score'], reverse=True)
        
        # ตัดเอาเฉพาะ Unique (กันเลขซ้ำใน Top list)
        def get_top_unique(pool, limit):
            unique_list = []
            seen = set()
            for x in pool:
                if x['num'] not in seen:
                    unique_list.append(x)
                    seen.add(x['num'])
                if len(unique_list) >= limit: break
            return unique_list

        # เลือกมาอย่างละ 3 ตัวที่ดีที่สุด
        top_new = get_top_unique(pool_new, 3)
        top_old = get_top_unique(pool_old, 3)
        
        final_list = top_new + top_old
        final_list.sort(key=lambda x: x['score'], reverse=True) # เรียงโชว์ตามความเทพ

        # แสดงผล
        note = ""
        if data_source_mode == "Backup": note = " (สถิติรวม)"
        elif data_source_mode == "Emergency": note = " (ฉุกเฉิน)"
        
        print(f"   {title}{note}")
        print(f"   {'-'*85}")
        print(f"   {'NUMBER':<10} | {'PROB %':<8} | {'TYPE':<8} | {'PATH ANALYSIS'}")
        print(f"   {'-'*85}")
        
        if not final_list:
            print(f"   ⚠️ ข้อมูลไม่เพียงพอ")
        else:
            for item in final_list:
                num = item['num']
                sc = item['score']
                path = item['path']
                
                if "ใหม่" in path or "สถิติสูง" in path or "New" in path:
                    prefix = "🆕"
                    type_str = "NEW"
                else:
                    prefix = "🔥"
                    type_str = "OLD"
                
                print(f"   {prefix} {num:<8} | {sc:>5.1f}%   | {type_str:<8} | {path}")
        print(f"   {'-'*85}\n")
        
    print("="*95)
    print("💡 PROB % สูง แปลว่า: เลขชุดนั้นตรงกับสถิติย้อนหลังมากที่สุด")
    print("   🆕 NEW: ไม่เคยออกรางวัลใดๆ มาก่อน (แต่โครงสร้างตัวเลขถูกต้องตามสถิติ)")
    print("   🔥 OLD: เคยออกรางวัลอื่นมาแล้ว (และโครงสร้างตัวเลขก็ยังสวยอยู่)")

# ---------------------------------------------------------
# เมนูหลัก
# ---------------------------------------------------------
def main_menu():
    while True:
        print("\n" + "█"*40)
        print("   🎱 LOTTO AI (Probability Master)")
        print("█"*40)
        print(" [1] 🔎 ตรวจสอบเลข")
        print(" [2] 🤖 โรงงานผลิตเลข (คัดตัวท็อป 3+3)")
        print(" [0] ❌ ออก")
        
        choice = input("👉 เลือก: ").strip()
        if choice == '1': mode_check_numbers()
        elif choice == '2': mode_generate_numbers()
        elif choice == '0': break
        else: print("❌ เลือกผิด")

if __name__ == "__main__":
    main_menu()