# ไฟล์: batch_converter.py (เวอร์ชัน CSV แนวนอนแยกคอลัมน์)
import csv
import os
import glob
from itertools import zip_longest # ตัวช่วยสำหรับตารางที่ยาวไม่เท่ากัน

RAW_FOLDER = 'raw_files'
OUTPUT_FILE = 'data/my_lotto.csv'

def process_all_files():
    print(f"🏭 เริ่มกระบวนการแปลงเป็น CSV แบบแยกคอลัมน์...")
    
    if not os.path.exists(RAW_FOLDER):
        print(f"❌ ไม่เจอโฟลเดอร์ {RAW_FOLDER}")
        return

    all_files = glob.glob(os.path.join(RAW_FOLDER, '*.txt'))
    
    # 1. สร้างถังเก็บข้อมูลแยกตามคอลัมน์
    # เราเตรียมไว้ให้ครบทุกประเภทที่มี
    columns_data = {
        'FIRST': [],
        'SECOND': [],
        'THIRD': [],
        'FOURTH': [],
        'FIFTH': [],
        'NEAR_FIRST': [],
        'TWO': [],
        'THREE': [] # รวมเลขท้าย 3 ตัว และเลขหน้า
    }
    
    # คำศัพท์ที่จะจับคู่กับถังด้านบน
    mapping = {
        'FIRST': 'FIRST', 'SECOND': 'SECOND', 'THIRD': 'THIRD',
        'FOURTH': 'FOURTH', 'FIFTH': 'FIFTH',
        'NEAR_FIRST': 'NEAR_FIRST', 'TWO': 'TWO',
        'THREE': 'THREE', 'TAIL': 'THREE' # TAIL เหมาเป็น THREE ไว้ก่อน
    }

    total_count = 0
    
    # 2. วนอ่านไฟล์ทั้งหมดเก็บเข้าถัง
    for txt_file in all_files:
        current_category = None
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('http'): continue
                
                parts = line.split()
                first_word = parts[0].upper()
                
                # ถ้าเจอหัวข้อใหม่ ให้เปลี่ยนถัง
                if first_word in mapping:
                    current_category = mapping[first_word]
                    numbers = parts[1:]
                else:
                    # ถ้าไม่เจอหัวข้อ ใช้ถังเดิม (กรณีรางวัลที่ 4, 5 ล้นบรรทัด)
                    numbers = parts
                
                if current_category:
                    for item in numbers:
                        clean_num = item.replace(',', '').replace('.', '').replace('"', '')
                        if clean_num.isdigit():
                            columns_data[current_category].append(clean_num)
                            total_count += 1
                            
        except Exception as e:
            print(f"⚠️ อ่านไฟล์ {txt_file} ไม่ได้: {e}")

    # 3. เขียนลง CSV แบบแนวนอน
    print(f"💾 กำลังบันทึกข้อมูล {total_count} ตัวลงไฟล์...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as out_csv:
        writer = csv.writer(out_csv)
        
        # เขียนหัวตาราง (Header)
        headers = list(columns_data.keys())
        writer.writerow(headers)
        
        # จัดเรียงข้อมูลให้ลงตาราง (zip_longest จะเติมช่องว่างให้ถ้าข้อมูลไม่เท่ากัน)
        # ดึงข้อมูลจากทุกถังมาเรียงกัน
        data_lists = [columns_data[k] for k in headers]
        rows = zip_longest(*data_lists, fillvalue='')
        
        writer.writerows(rows)

    print(f"✅ เสร็จเรียบร้อย! ไฟล์ CSV มีหัวข้อ: {', '.join(headers)}")

if __name__ == "__main__":
    process_all_files()