import pandas as pd
import json
import sys

# 1. 定義輸入和輸出檔案名稱
csv_file_path = '食品營養成分資料庫2024UPDATE2.xlsx - 工作表1.csv'
json_file_path = 'food_database_with_english.json' # 為了區分，我將檔名略微更改

# 2. 定義 CSV 欄位與 JSON 鍵的對應關係
column_mapping = {
    '整合編號': 'id',
    '樣品名稱': 'name',
    'English Name': 'english_name', # <-- 新增英文名稱
    '熱量(kcal)': 'calories',
    '粗蛋白(g)': 'protein',
    '粗脂肪(g)': 'fat',
    '總碳水化合物(g)': 'carbs'
}
csv_columns = list(column_mapping.keys())

# 3. 讀取 CSV 檔案
try:
    # 嘗試用 UTF-8 編碼讀取，並僅讀取需要的欄位
    df = pd.read_csv(csv_file_path, encoding='utf-8', usecols=csv_columns)
except Exception:
    # 如果失敗，嘗試 Big5 編碼
    try:
        df = pd.read_csv(csv_file_path, encoding='big5', usecols=csv_columns)
    except Exception as e:
        print(f"錯誤：無法讀取檔案 {csv_file_path}，請檢查編碼或檔案路徑。錯誤訊息: {e}")
        sys.exit(1)

# 4. 重新命名欄位以符合 JSON 結構
df.rename(columns=column_mapping, inplace=True)

# 5. 數據清理與轉換 (處理 NaN 或空白值)
# 確保所有營養素欄位都是數字，並將 NaN 替換為 0.0
numeric_cols = ['calories', 'protein', 'fat', 'carbs']
for col in numeric_cols:
    # pd.to_numeric 嘗試將欄位轉為數字，錯誤值設為 NaN，然後 NaN 設為 0.0
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

# 6. 加入固定的單位資訊欄位 (假設所有營養數據均以「每 100 克」計算)
df['unit_per_serving'] = '100g'
df['base_unit'] = 'g'

# 7. 將 DataFrame 轉換為 JSON 格式 (list of dictionaries)
food_data = df.to_dict('records')

# 8. 寫入 JSON 檔案
try:
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        # ensure_ascii=False 讓中文正常顯示
        # indent=4 讓 JSON 檔案格式化，方便閱讀
        json.dump(food_data, jsonfile, ensure_ascii=False, indent=4)
    print(f"\n🎉 成功！{len(food_data)} 筆資料已從 CSV 轉換並寫入到 {json_file_path}")

except Exception as e:
    print(f"\n寫入 JSON 檔案時發生錯誤: {e}")
    sys.exit(1)