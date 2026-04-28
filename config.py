# ==============================================================================
# HW2 Configuration
# ------------------------------------------------------------------------------
# 請在此填入您的 CWA API 授權金鑰 (Authorization Key)
# Please enter your CWA API Authorization Key below.
# 取得金鑰：https://opendata.cwa.gov.tw/userInfo/case
# ==============================================================================

CWA_API_KEY = "YOUR_CWA_API_KEY_HERE"

# ==============================================================================
# Database Configuration
# ==============================================================================
DB_PATH = "data.db"

# ==============================================================================
# CWA API - 7-Day Regional Forecast
# Endpoint: /v1/rest/datastore/F-D0047-091 (全台灣各縣市7天天氣預報)
# API Reference: https://opendata.cwa.gov.tw/dist/opendata-swagger.html
# ==============================================================================
BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"

# Mapping of region names to their geographic area classification
REGION_AREA_MAP = {
    "基隆市": "北部",
    "臺北市": "北部",
    "新北市": "北部",
    "桃園市": "北部",
    "新竹市": "北部",
    "新竹縣": "北部",
    "苗栗縣": "中部",
    "臺中市": "中部",
    "彰化縣": "中部",
    "南投縣": "中部",
    "雲林縣": "中部",
    "嘉義市": "南部",
    "嘉義縣": "南部",
    "臺南市": "南部",
    "高雄市": "南部",
    "屏東縣": "南部",
    "宜蘭縣": "東北部",
    "花蓮縣": "東部",
    "臺東縣": "東南部",
}

# The six display regions and their constituent counties/cities
DISPLAY_REGIONS = {
    "北部": ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣"],
    "中部": ["苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣"],
    "南部": ["嘉義市", "嘉義縣", "臺南市", "高雄市", "屏東縣"],
    "東北部": ["宜蘭縣"],
    "東部": ["花蓮縣"],
    "東南部": ["臺東縣"],
}

# Approximate center coordinates for each display region (for Folium map)
REGION_COORDS = {
    "北部":  (25.05, 121.55),
    "中部":  (24.10, 120.85),
    "南部":  (22.80, 120.40),
    "東北部": (24.70, 121.75),
    "東部":  (23.90, 121.60),
    "東南部": (22.75, 121.15),
}
