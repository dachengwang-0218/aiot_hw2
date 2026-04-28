# HW2 — 臺灣天氣預報系統 / Taiwan Weather Forecast System

## 網站展示 / Preview

![網站展示](作業截圖/網站展示.png?v=2)

## 🚀 線上 Demo / Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aiothw2-5gffsgkmijhmiysvjtagui.streamlit.app/)

👉 **[https://aiothw2-5gffsgkmijhmiysvjtagui.streamlit.app/](https://aiothw2-5gffsgkmijhmiysvjtagui.streamlit.app/)**

---


## 專案結構 Project Structure

```
hw2/
├── config.py       # ⭐ API 金鑰設定 & 常數 / API key & constants
├── hw2_fetch.py    # HW2-1&2&3：抓取、解析、儲存資料
├── hw2_app.py      # HW2-4：Streamlit 視覺化應用程式
├── data.db         # SQLite3 資料庫（執行後自動產生）
├── requirements.txt
└── README.md
```

---

## ⭐ 步驟 0：填入 API 金鑰

開啟 `config.py`，找到以下這行並填入您的 CWA Authorization Key：

```python
CWA_API_KEY = "YOUR_CWA_API_KEY_HERE"
```

取得金鑰：https://opendata.cwa.gov.tw/userInfo/case

---

## 步驟 1：安裝相依套件

```bash
pip install -r requirements.txt
```

---

## 步驟 2：抓取資料並存入資料庫 (HW2-1 ~ HW2-3)

```bash
python hw2_fetch.py
```

成功後會顯示：
```
[INFO] API 請求成功，HTTP 狀態碼：200
[INFO] 共解析 XXX 筆預報記錄。
[INFO] 成功儲存 XXX 筆資料至 data.db
[DONE] 資料已成功儲存至 data.db
```

資料庫位置：`data.db`，資料表：`TemperatureForecasts`

| 欄位       | 型態    | 說明             |
|------------|---------|------------------|
| id         | INTEGER | 主鍵 (自動遞增)   |
| regionName | TEXT    | 縣市名稱         |
| area       | TEXT    | 地區分類         |
| dataDate   | TEXT    | 預報日期         |
| mint       | INTEGER | 最低氣溫 (°C)   |
| maxt       | INTEGER | 最高氣溫 (°C)   |

---

## 步驟 3：啟動 Streamlit 視覺化應用 (HW2-4)

```bash
streamlit run hw2_app.py
```

瀏覽器開啟 http://localhost:8501

### 功能說明
- **左側**：下拉選單選擇地區 + Folium 互動地圖（選中地區以大圓圈標示）
- **右側**：氣溫折線圖（藍=最低溫，紅=最高溫）+ 資料表格
- 所有資料均從 `data.db` SQLite3 資料庫讀取

---

## 地區對應表

| 顯示地區 | 包含縣市                                  |
|----------|-------------------------------------------|
| 北部     | 基隆市、臺北市、新北市、桃園市、新竹市、新竹縣 |
| 中部     | 苗栗縣、臺中市、彰化縣、南投縣、雲林縣      |
| 南部     | 嘉義市、嘉義縣、臺南市、高雄市、屏東縣      |
| 東北部   | 宜蘭縣                                    |
| 東部     | 花蓮縣                                    |
| 東南部   | 臺東縣                                    |
