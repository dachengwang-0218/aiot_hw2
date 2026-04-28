"""
hw2_fetch.py  ─  HW2-1 & HW2-2
================================
使用 requests 從 CWA API 取得臺灣各地區 7 天天氣預報，
解析 JSON 並萃取 regionName、dataDate、mint、maxt，
最終儲存至 SQLite3 資料庫 (data.db)。

Usage:
    python hw2_fetch.py
"""

import ssl
import sqlite3
import requests
import urllib3

from config import CWA_API_KEY, BASE_URL, DB_PATH, REGION_AREA_MAP

# ---------------------------------------------------------------------------
# SSL / Certificate handling
# ---------------------------------------------------------------------------
# 部分環境的 SSL 憑證驗證可能失敗，以下停用警告訊息。
# Disable SSL warnings if verification is skipped.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERIFY_SSL = True  # 若環境 SSL 驗證失敗，可改為 False


# ===========================================================================
# HW2-1  ─  Fetch weather forecast JSON from CWA API
# ===========================================================================

def fetch_forecast_json() -> dict:
    """
    向 CWA API 發送 GET 請求並回傳原始 JSON 資料。

    Returns:
        dict: 完整 API JSON 回應。

    Raises:
        requests.HTTPError: 當 HTTP 狀態碼不為 2xx 時。
        Exception: 其他網路或解析錯誤。
    """
    params = {
        "Authorization": CWA_API_KEY,
        "format": "JSON",
    }

    print(f"[INFO] 正在向 CWA API 發送請求...")
    try:
        response = requests.get(
            BASE_URL,
            params=params,
            verify=VERIFY_SSL,
            timeout=30,
        )
    except requests.exceptions.SSLError:
        print("[WARN] SSL 驗證失敗，改以不驗證模式重試...")
        response = requests.get(
            BASE_URL,
            params=params,
            verify=False,
            timeout=30,
        )

    response.raise_for_status()
    print(f"[INFO] API 請求成功，HTTP 狀態碼：{response.status_code}")
    return response.json()


# ===========================================================================
# HW2-2  ─  Parse JSON and extract required fields
# ===========================================================================

def parse_forecast(data: dict) -> list[dict]:
    """
    解析 CWA API 回傳的 JSON，萃取所需欄位。

    CWA F-D0047-091 實際 JSON 路徑（已由 API 回應驗證）：
        records
          └─ Locations  (list, 取 [0])
               └─ Location  (list, 逐筆走訪)
                    ├─ LocationName          → regionName
                    └─ WeatherElement  (list)
                         ├─ ElementName = "最高溫度"
                         │    └─ Time[i]
                         │         ├─ StartTime  → dataDate
                         │         └─ ElementValue[0]["MaxTemperature"] → maxt
                         └─ ElementName = "最低溫度"
                              └─ Time[i]
                                   └─ ElementValue[0]["MinTemperature"] → mint

    Args:
        data (dict): fetch_forecast_json() 的回傳值。

    Returns:
        list[dict]: 每筆記錄包含：
            - regionName (str)  : 原始地區名稱（縣市）
            - area       (str)  : 分類區域（北部/中部/南部…）
            - dataDate   (str)  : 預報日期，格式 YYYY-MM-DD
            - mint       (int)  : 最低氣溫 (°C)
            - maxt       (int)  : 最高氣溫 (°C)
    """
    records = []

    # 取得縣市列表（PascalCase 為 API 實際回傳鍵名）
    locations = (
        data.get("records", {})
            .get("Locations", [{}])[0]
            .get("Location", [])
    )

    if not locations:
        print("[WARN] 無法解析 Location 資料，請檢查 JSON 結構。")
        return records

    for location in locations:
        region_name = location.get("LocationName", "Unknown")
        area = REGION_AREA_MAP.get(region_name, "其他")

        # 建立 {ElementName: Time列表} 的對照字典
        weather_elements = {
            elem["ElementName"]: elem["Time"]
            for elem in location.get("WeatherElement", [])
        }

        # 最高溫度 / 最低溫度（ElementName 為中文）
        maxt_times = weather_elements.get("最高溫度", [])
        mint_times = weather_elements.get("最低溫度", [])

        # 以最高溫度的時間點為基準逐日配對
        for i, maxt_entry in enumerate(maxt_times):
            data_date = maxt_entry.get("StartTime", "")[:10]  # 取 YYYY-MM-DD

            # ElementValue[0] 的 key 分別是 MaxTemperature / MinTemperature
            maxt_val = maxt_entry.get("ElementValue", [{}])[0].get("MaxTemperature", None)

            mint_val = None
            if i < len(mint_times):
                mint_val = mint_times[i].get("ElementValue", [{}])[0].get("MinTemperature", None)

            # 跳過無效資料
            if data_date and mint_val is not None and maxt_val is not None:
                try:
                    records.append({
                        "regionName": region_name,
                        "area":       area,
                        "dataDate":   data_date,
                        "mint":       int(mint_val),
                        "maxt":       int(maxt_val),
                    })
                except (ValueError, TypeError) as e:
                    print(f"[WARN] 資料轉換失敗 ({region_name}, {data_date}): {e}")

    print(f"[INFO] 共解析 {len(records)} 筆預報記錄。")
    return records


# ===========================================================================
# HW2-3  ─  Save data to SQLite3 database
# ===========================================================================

def save_to_db(records: list[dict], db_path: str = DB_PATH) -> None:
    """
    建立（或更新）SQLite3 資料庫，將預報資料存入 TemperatureForecasts 表格。

    Table schema:
        id         INTEGER PRIMARY KEY AUTOINCREMENT
        regionName TEXT    NOT NULL
        area       TEXT    NOT NULL
        dataDate   TEXT    NOT NULL
        mint       INTEGER NOT NULL
        maxt       INTEGER NOT NULL

    重複匯入時以 (regionName, dataDate) 為唯一鍵進行 UPSERT。

    Args:
        records  (list[dict]): parse_forecast() 的回傳值。
        db_path  (str)       : SQLite3 資料庫路徑。
    """
    if not records:
        print("[WARN] 無資料可儲存。")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 建立資料表（若不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TemperatureForecasts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT    NOT NULL,
            area       TEXT    NOT NULL,
            dataDate   TEXT    NOT NULL,
            mint       INTEGER NOT NULL,
            maxt       INTEGER NOT NULL,
            UNIQUE (regionName, dataDate)
        )
    """)

    # UPSERT：若 (regionName, dataDate) 已存在則更新，否則插入
    upsert_sql = """
        INSERT INTO TemperatureForecasts (regionName, area, dataDate, mint, maxt)
        VALUES (:regionName, :area, :dataDate, :mint, :maxt)
        ON CONFLICT(regionName, dataDate)
        DO UPDATE SET
            area = excluded.area,
            mint = excluded.mint,
            maxt = excluded.maxt
    """
    cursor.executemany(upsert_sql, records)
    conn.commit()

    print(f"[INFO] 成功儲存 {cursor.rowcount if cursor.rowcount >= 0 else len(records)} 筆資料至 {db_path}")
    conn.close()


# ===========================================================================
# Main entry point
# ===========================================================================

def main():
    print("=" * 60)
    print("  CWA 7-Day Weather Forecast Fetcher  (HW2-1 ~ HW2-3)")
    print("=" * 60)

    if CWA_API_KEY == "YOUR_CWA_API_KEY_HERE":
        print("\n[ERROR] 請先在 config.py 中填入您的 CWA API 授權金鑰！")
        return

    # Step 1: Fetch
    raw_json = fetch_forecast_json()

    # Step 2: Parse
    records = parse_forecast(raw_json)

    if not records:
        print("[ERROR] 解析結果為空，程式結束。請確認 API 金鑰與回應格式。")
        return

    # 顯示前 3 筆資料預覽
    print("\n── 資料預覽 (前 3 筆) ──")
    for r in records[:3]:
        print(f"  {r['regionName']} [{r['area']}] | {r['dataDate']} | "
              f"MinT={r['mint']}°C  MaxT={r['maxt']}°C")

    # Step 3: Save to DB
    save_to_db(records)

    print("\n[DONE] 資料已成功儲存至", DB_PATH)
    print("       接下來執行：streamlit run hw2_app.py")


if __name__ == "__main__":
    main()
