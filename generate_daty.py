# ไฟล์: generate_mock_data.py
import pandas as pd
import random
import os

# ตรวจสอบว่ามีโฟลเดอร์ data หรือยัง
if not os.path.exists('data'):
    os.makedirs('data')

# สร้างข้อมูลจำลอง 100 งวด (สมมติ)
data = []
for i in range(100):
    # จำลองเลขรางวัล (สุ่มมามั่วๆ เพื่อเทสระบบ)
    row = {
        'date': f'2024-01-{i+1}',
        'prize_1': f'{random.randint(0, 999999):06d}',
        # รางวัลที่ 2 มี 5 รางวัล (คั่นด้วยคอมม่า)
        'prize_2': ",".join([f'{random.randint(0, 999999):06d}' for _ in range(5)]),
        # รางวัลที่ 5 มี 10 รางวัล (สมมติเอาแค่นี้ก่อนเพื่อเทส)
        'prize_5': ",".join([f'{random.randint(0, 999999):06d}' for _ in range(10)]) 
    }
    data.append(row)

df = pd.DataFrame(data)
df.to_csv('data/lotto_mock_data.csv', index=False)
print("✅ สร้างไฟล์ข้อมูลจำลอง data/lotto_mock_data.csv เรียบร้อยครับ!")