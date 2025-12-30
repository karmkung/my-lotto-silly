# ไฟล์: src/dna_engine.py

def get_dna(number_str):
    """
    แปลงตัวเลข (String) ให้เป็น DNA (เรียงจากน้อยไปมาก)
    เช่น '981234' -> '123489'
    """
    # ลบช่องว่าง (เผื่อไฟล์ CSV ไม่สะอาด)
    clean_num = number_str.strip()
    # เรียงตัวเลข
    sorted_chars = sorted(clean_num)
    # รวมกลับเป็นข้อความ
    return "".join(sorted_chars)

def check_virgin_status(number_dna, history_bucket):
    """
    ตรวจสอบว่า DNA นี้เคยอยู่ในถังประวัติศาสตร์หรือไม่
    Return: True (ถ้าเป็น Virgin/ไม่เคยออก), False (ถ้าเคยออกแล้ว)
    """
    if number_dna in history_bucket:
        return False # ❌ ไม่รอด (เคยออกแล้ว)
    return True      # ✅ รอด (เป็นเลขใหม่)