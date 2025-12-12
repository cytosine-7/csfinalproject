import pandas as pd
from deep_translator import GoogleTranslator
import json
import time
import requests
import io
import os

# 1. 下載最新數據
csv_url = "https://data.fda.gov.tw/opendata/exportDataLinked.do?method=ExportData&InfoId=178&logType=2"
print("正在下載最新數據...")

try:
    response = requests.get(csv_url, verify=False)
    # 嘗試解決編碼問題 (Big5 或 utf-8-sig)
    response.encoding = 'utf-8-sig' 
    df = pd.read_csv(io.StringIO(response.text))
    
# === 設定存檔路徑 (修改這裡：存入資料夾內) ===
    target_folder = 'Sedentary_Lifestyle_Management'
    
    # ⚠️ 新增這一行：如果資料夾不存在，就創建它
    if not os.path.exists(target_folder):
        os.makedirs(target_folder, exist_ok=True)
        
    filename = os.path.join(target_folder, 'food_database.json')
    backup_filename = os.path.join(target_folder, 'food_database.backup.json')
    # ==========================================

    # 2. 讀取「舊的」JSON 資料 (如果存在)
    old_data_map = {} 
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            old_list = json.load(f)
            for item in old_list:
                old_data_map[item['zh']] = item
    
    print(f"舊資料庫共有 {len(old_data_map)} 筆資料")

    def get_english_name(text):
        try:
            if not text or str(text).isascii(): return text
            return GoogleTranslator(source='zh-TW', target='en').translate(text)
        except:
            return text

    new_database_list = []
    updated_count = 0
    new_count = 0
    skipped_count = 0

    # 3. 比對邏輯
    for index, row in df.iterrows():
        zh_name = row.get('樣品名稱', '').strip()
        if pd.isna(zh_name) or zh_name == '': continue
        
        # 確保數值是字串或數字，處理 NaN
        new_cal = str(row.get('熱量', '0')).strip()
        if new_cal == 'nan': new_cal = '0'

        # 檢查是否已存在
        if zh_name in old_data_map:
            old_entry = old_data_map[zh_name]
            old_cal = str(old_entry.get('cal', '0')).strip()

            # A. 名稱相同，數值也相同 -> 直接沿用舊翻譯
            if old_cal == new_cal:
                new_database_list.append(old_entry)
                skipped_count += 1
            
            # B. 名稱相同，但數值變了 -> 更新數值
            else:
                old_entry['cal'] = new_cal
                new_database_list.append(old_entry)
                updated_count += 1
        
        # C. 完全的新品項 -> 呼叫翻譯 API
        else:
            en_name = get_english_name(zh_name)
            new_database_list.append({
                "zh": zh_name,
                "en": en_name,
                "cal": new_cal
            })
            new_count += 1
            print(f"新增品項: {zh_name}")
            time.sleep(0.5) # 避免封鎖

    # 4. 存檔與備份機制
    if os.path.exists(filename):
        if os.path.exists(backup_filename):
            os.remove(backup_filename)
        os.rename(filename, backup_filename)
        print(f"已備份舊資料為 {backup_filename}")

    # 寫入最新的資料
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_database_list, f, ensure_ascii=False, indent=4)

    print(f"處理完成！資料已寫入: {filename}")
    print(f"- 無變動: {skipped_count}")
    print(f"- 數值更新: {updated_count}")
    print(f"- 新增翻譯: {new_count}")

except Exception as e:
    print(f"發生錯誤: {e}")