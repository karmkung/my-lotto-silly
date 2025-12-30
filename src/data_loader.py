# ไฟล์: src/data_loader.py
import pandas as pd
from src.dna_engine import get_dna

LOCAL_CSV_PATH = 'data/my_lotto.csv' 

def load_lotto_history(file_path=LOCAL_CSV_PATH):
    print(f"\n📂 กำลังอ่านไฟล์: {file_path}")
    
    # สร้างถังเก็บข้อมูลรอไว้
    buckets = {
        'prize_1': set(), 'prize_2': set(), 'prize_3': set(),
        'prize_4': set(), 'prize_5': set(), 'prize_tails': set(),
        'all_raw_prizes': [], 
        'raw_two': [], 'raw_three': [],
        # ถังเก็บเลขดิบแยกรางวัล
        'raw_prize_1': [], 'raw_prize_2': [], 'raw_prize_3': [],
        'raw_prize_4': [], 'raw_prize_5': []
    }

    try:
        # อ่านไฟล์ CSV (บังคับอ่านเป็น String เพื่อกันเลขเพี้ยน)
        df = pd.read_csv(file_path, dtype=str)
        
        print(f"   พบหัวข้อใน CSV: {list(df.columns)}")
        
        # วนลูปอ่านทีละคอลัมน์ โดยไม่สนชื่อเป๊ะๆ (ใช้การเดาใจ)
        for col_name in df.columns:
            # แปลงชื่อหัวข้อให้เป็นตัวใหญ่และตัดช่องว่างทิ้ง เพื่อให้เช็คง่าย
            clean_col = col_name.strip().upper()
            
            # ดึงตัวเลขในคอลัมน์นั้น (ตัดช่องว่างและค่าว่างทิ้ง)
            numbers = df[col_name].dropna().astype(str)
            
            # -----------------------------------------------------
            # 🕵️‍♀️ ส่วนนักสืบ: เดาว่าคอลัมน์นี้คือรางวัลอะไร?
            # -----------------------------------------------------
            target_bucket = None
            is_tail = False
            
            # เช็ครางวัลที่ 1
            if 'FIRST' in clean_col or 'PRIZE_1' in clean_col or clean_col == '1':
                if 'NEAR' not in clean_col: # กันสับสนกับรางวัลใกล้เคียง
                    target_bucket = 'prize_1'
                    raw_target = 'raw_prize_1'

            # เช็ครางวัลที่ 2
            elif 'SECOND' in clean_col or 'PRIZE_2' in clean_col or clean_col == '2':
                target_bucket = 'prize_2'
                raw_target = 'raw_prize_2'

            # เช็ครางวัลที่ 3
            elif 'THIRD' in clean_col or 'PRIZE_3' in clean_col or clean_col == '3':
                target_bucket = 'prize_3'
                raw_target = 'raw_prize_3'

            # เช็ครางวัลที่ 4
            elif 'FOURTH' in clean_col or 'PRIZE_4' in clean_col or clean_col == '4':
                target_bucket = 'prize_4'
                raw_target = 'raw_prize_4'

            # เช็ครางวัลที่ 5
            elif 'FIFTH' in clean_col or 'PRIZE_5' in clean_col or clean_col == '5':
                target_bucket = 'prize_5'
                raw_target = 'raw_prize_5'
            
            # เช็คเลขท้าย (2 ตัว / 3 ตัว)
            elif 'TWO' in clean_col or 'TAIL' in clean_col or 'THREE' in clean_col:
                is_tail = True
            
            # -----------------------------------------------------
            # 📥 ส่วนบันทึกข้อมูลลงถัง
            # -----------------------------------------------------
            count_loaded = 0
            for num in numbers:
                num = str(num).replace('.0', '').replace(',', '').strip()
                if not num or num.lower() == 'nan': continue
                
                dna = get_dna(num)

                # บันทึกรางวัลใหญ่ (1-5)
                if target_bucket:
                    buckets[target_bucket].add(dna)
                    buckets[raw_target].append(num)
                    if len(num) == 6: buckets['all_raw_prizes'].append(num)
                    count_loaded += 1
                
                # บันทึกเลขท้าย
                if is_tail:
                    buckets['prize_tails'].add(dna)
                    if len(num) == 2: buckets['raw_two'].append(num)
                    if len(num) == 3: buckets['raw_three'].append(num)
                    count_loaded += 1
            
            # รายงานผลการโหลดของคอลัมน์นี้
            if count_loaded > 0:
                print(f"   ✅ อ่าน '{col_name}' -> เข้าถัง {target_bucket or 'เลขท้าย'} ({count_loaded} ตัว)")

        # สรุปยอดรวม
        print("\n📊 สรุปยอดข้อมูลที่โหลดได้จริง:")
        print(f"   - รางวัลที่ 1: {len(buckets['raw_prize_1'])} ตัว")
        print(f"   - รางวัลที่ 2: {len(buckets['raw_prize_2'])} ตัว")
        print(f"   - รางวัลที่ 3: {len(buckets['raw_prize_3'])} ตัว")
        print(f"   - รางวัลที่ 4: {len(buckets['raw_prize_4'])} ตัว")
        print(f"   - รางวัลที่ 5: {len(buckets['raw_prize_5'])} ตัว")
        print("-" * 40)
        
        return buckets

    except Exception as e:
        print(f"❌ อ่านไฟล์ CSV ล้มเหลว: {e}")
        return None