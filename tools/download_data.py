import os
import requests

# 1. ตั้งค่าเป้าหมาย (API ของ GitHub สำหรับโฟลเดอร์นั้น)
GITHUB_API_URL = "https://api.github.com/repos/vicha-w/thai-lotto-archive/contents/lottonumbers"
SAVE_FOLDER = "raw_files"  # โฟลเดอร์ที่จะเก็บไฟล์ (เพื่อเอาไปใช้กับ batch_converter ต่อ)

def download_from_github():
    print(f"🚀 กำลังเชื่อมต่อ GitHub...")
    
    # สร้างโฟลเดอร์ถ้ายังไม่มี
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    try:
        # เรียกข้อมูลรายชื่อไฟล์จาก GitHub API
        response = requests.get(GITHUB_API_URL)
        
        if response.status_code == 200:
            files = response.json()
            print(f"📦 พบไฟล์ทั้งหมด {len(files)} ไฟล์ กำลังดาวน์โหลด...")
            
            for file_info in files:
                file_name = file_info['name']
                download_url = file_info['download_url']
                
                # เราจะโหลดเฉพาะไฟล์ .txt
                if file_name.endswith('.txt'):
                    print(f"   ⬇️ กำลังโหลด: {file_name} ...")
                    
                    # โหลดเนื้อหาไฟล์
                    r = requests.get(download_url)
                    
                    # บันทึกลงเครื่อง
                    save_path = os.path.join(SAVE_FOLDER, file_name)
                    with open(save_path, 'wb') as f:
                        f.write(r.content)
            
            print("\n✅ ดาวน์โหลดครบทุกไฟล์แล้ว!")
            print(f"👉 ไฟล์ทั้งหมดอยู่ที่โฟลเดอร์: {SAVE_FOLDER}")
            print("💡 ขั้นตอนต่อไป: รัน 'python batch_converter.py' เพื่อรวมไฟล์ได้เลย")
            
        else:
            print(f"❌ เข้าถึงข้อมูลไม่ได้ (Status Code: {response.status_code})")
            print("อาจเป็นเพราะ GitHub จำกัดการเรียกใช้งานชั่วคราว ลองใหม่ภายหลัง")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    # เช็คว่ามี library requests หรือยัง
    try:
        import requests
        download_from_github()
    except ImportError:
        print("❌ คุณยังไม่ได้ลง requests")
        print("👉 กรุณาพิมพ์: pip install requests ใน Terminal ก่อน")