"""
hw2_app.py  ─  HW2-4  (Premium Edition)
=========================================
Streamlit 視覺化應用程式 — 升級版美化設計。

版面配置：左右兩欄
  · 左側：地區選擇按鈕 + Folium 互動式地圖
  · 右側：天氣指標卡片 + 折線圖 + 資料表格

所有資料均從 SQLite3 資料庫 (data.db) 讀取。

Usage:
    python3 -m streamlit run hw2_app.py
"""

import sqlite3
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from config import DB_PATH, DISPLAY_REGIONS, REGION_COORDS

# ===========================================================================
# Page configuration
# ===========================================================================
st.set_page_config(
    page_title="臺灣天氣預報儀表板",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ===========================================================================
# Premium CSS Design System
# ===========================================================================
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', 'Noto Sans TC', sans-serif;
    background: #070b14 !important;
}

/* Animated gradient background */
.stApp {
    background: linear-gradient(135deg, #070b14 0%, #0d1b2a 40%, #0f2438 70%, #070b14 100%) !important;
    background-attachment: fixed !important;
}

/* Hide streamlit branding */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

.block-container {
    padding: 2rem 2.5rem 2rem !important;
    max-width: 1600px !important;
}

/* ══════════════════════════════════════════════
   HERO HEADER
══════════════════════════════════════════════ */
.hero {
    position: relative;
    background: linear-gradient(135deg, #0d1f35 0%, #122d48 50%, #0a1f35 100%);
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 24px;
    padding: 36px 44px;
    margin-bottom: 28px;
    overflow: hidden;
    box-shadow:
        0 0 0 1px rgba(99,179,237,0.08),
        0 20px 60px rgba(0,0,0,0.5),
        inset 0 1px 0 rgba(255,255,255,0.06);
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -80px; left: 20%;
    width: 360px; height: 200px;
    background: radial-gradient(ellipse, rgba(99,102,241,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-inner {
    position: relative;
    display: flex;
    align-items: center;
    gap: 24px;
    z-index: 1;
}
.hero-badge {
    font-size: 4rem;
    filter: drop-shadow(0 0 20px rgba(56,189,248,0.5));
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%,100% { transform: translateY(0px); }
    50%      { transform: translateY(-8px); }
}
.hero-text {}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #e0f2fe 0%, #7dd3fc 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 6px 0;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.hero-sub {
    font-size: 0.9rem;
    color: #64748b;
    margin: 0;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}
.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    color: #7dd3fc;
    font-weight: 500;
}
.hero-right {
    margin-left: auto;
    text-align: right;
}
.hero-date {
    font-size: 0.8rem;
    color: #4a6480;
    line-height: 1.8;
}
.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #34d399;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; box-shadow: 0 0 0 0 rgba(52,211,153,0.4); }
    50%      { opacity: 0.7; box-shadow: 0 0 0 6px rgba(52,211,153,0); }
}

/* ══════════════════════════════════════════════
   GLASS CARDS
══════════════════════════════════════════════ */
.glass-card {
    background: rgba(13, 27, 42, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(99, 179, 237, 0.12);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow:
        0 4px 24px rgba(0,0,0,0.3),
        inset 0 1px 0 rgba(255,255,255,0.04);
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(99,179,237,0.25);
    box-shadow: 0 8px 40px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.06);
}

/* ── Section label ── */
.section-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #4a7fa8;
    margin-bottom: 14px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(74,127,168,0.4), transparent);
}

/* ══════════════════════════════════════════════
   REGION SELECTOR PILLS
══════════════════════════════════════════════ */
.region-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 6px;
}
.region-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    border: 1.5px solid;
    transition: all 0.2s ease;
    user-select: none;
}
.pill-active {
    background: linear-gradient(135deg, #1e40af, #1d4ed8);
    border-color: #3b82f6;
    color: #ffffff;
    box-shadow: 0 0 20px rgba(59,130,246,0.4);
}
.pill-inactive {
    background: rgba(255,255,255,0.04);
    border-color: rgba(255,255,255,0.1);
    color: #94a3b8;
}
.pill-inactive:hover {
    border-color: rgba(255,255,255,0.25);
    color: #e2e8f0;
    background: rgba(255,255,255,0.08);
}
.county-tag {
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 6px;
    padding-left: 4px;
    line-height: 1.6;
}

/* ══════════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════════ */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 20px;
}
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 14px 14px 0 0;
}
.metric-card.cold::before  { background: linear-gradient(90deg, #38bdf8, #818cf8); }
.metric-card.hot::before   { background: linear-gradient(90deg, #f97316, #ef4444); }
.metric-card.days::before  { background: linear-gradient(90deg, #34d399, #10b981); }
.metric-card.avg::before   { background: linear-gradient(90deg, #a78bfa, #818cf8); }
.metric-card.range::before { background: linear-gradient(90deg, #fbbf24, #f59e0b); }

.metric-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #4a6480;
    margin-bottom: 6px;
}
.metric-val {
    font-size: 1.6rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.02em;
}
.metric-val.cold  { color: #7dd3fc; }
.metric-val.hot   { color: #fb923c; }
.metric-val.days  { color: #6ee7b7; }
.metric-val.avg   { color: #c4b5fd; }
.metric-val.range { color: #fcd34d; }
.metric-unit {
    font-size: 0.75rem;
    font-weight: 400;
    opacity: 0.6;
    margin-left: 2px;
}

/* ══════════════════════════════════════════════
   CHART WRAPPER
══════════════════════════════════════════════ */
.chart-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.chart-legend {
    display: flex;
    gap: 16px;
    margin-bottom: 14px;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78rem;
    color: #64748b;
}
.legend-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}

/* ══════════════════════════════════════════════
   TABLE STYLES
══════════════════════════════════════════════ */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
}
.stDataFrame thead tr th {
    background: rgba(13,27,42,0.9) !important;
    color: #7dd3fc !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-bottom: 1px solid rgba(99,179,237,0.2) !important;
}
.stDataFrame tbody tr:nth-child(even) {
    background: rgba(255,255,255,0.02) !important;
}

/* ══════════════════════════════════════════════
   SELECTBOX OVERRIDE
══════════════════════════════════════════════ */
div[data-baseweb="select"] > div {
    background: rgba(13,27,42,0.9) !important;
    border: 1.5px solid rgba(99,179,237,0.25) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: rgba(59,130,246,0.7) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}

/* ══════════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════════ */
details {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 4px !important;
}
details summary {
    color: #64748b !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    padding: 8px 12px !important;
}
details summary:hover { color: #94a3b8 !important; }

/* ══════════════════════════════════════════════
   DIVIDER
══════════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 18px 0 !important;
}

/* ══════════════════════════════════════════════
   FOLIUM MAP
══════════════════════════════════════════════ */
iframe {
    border-radius: 14px !important;
    border: 1px solid rgba(99,179,237,0.15) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
}

/* Caption / small text */
.stCaption, small { color: #4a6480 !important; font-size: 0.78rem !important; }

/* Warning / Error boxes */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ===========================================================================
# Database helpers
# ===========================================================================

@st.cache_data(ttl=300)
def load_all_data(db_path: str = DB_PATH) -> pd.DataFrame:
    """從 SQLite3 資料庫讀取全部預報資料。"""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(
            "SELECT * FROM TemperatureForecasts ORDER BY dataDate ASC",
            conn,
        )
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ 無法讀取資料庫：{e}\n\n請先執行 `python3 hw2_fetch.py` 以建立資料庫。")
        return pd.DataFrame()


def get_region_data(df: pd.DataFrame, area: str) -> pd.DataFrame:
    """篩選特定區域，每日最低/最高氣溫取平均。"""
    subset = df[df["area"] == area].copy()
    if subset.empty:
        return subset
    agg = (
        subset.groupby("dataDate", as_index=False)
              .agg(mint=("mint", "mean"), maxt=("maxt", "mean"))
              .round(1)
    )
    agg["dataDate"] = pd.to_datetime(agg["dataDate"])
    return agg


# ===========================================================================
# Map builder — upgraded markers
# ===========================================================================

def build_map(selected_area: str) -> folium.Map:
    """建立深色 Folium 地圖，已選區域有脈衝光環效果。"""
    m = folium.Map(
        location=(23.6, 121.0),
        zoom_start=7,
        tiles="CartoDB dark_matter",
        zoom_control=True,
        scrollWheelZoom=False,
    )

    PALETTE = {
        "北部":  {"fill": "#38bdf8", "glow": "rgba(56,189,248,0.35)"},
        "中部":  {"fill": "#34d399", "glow": "rgba(52,211,153,0.35)"},
        "南部":  {"fill": "#f87171", "glow": "rgba(248,113,113,0.35)"},
        "東北部": {"fill": "#c084fc", "glow": "rgba(192,132,252,0.35)"},
        "東部":  {"fill": "#fbbf24", "glow": "rgba(251,191,36,0.35)"},
        "東南部": {"fill": "#22d3ee", "glow": "rgba(34,211,238,0.35)"},
    }

    for area, coords in REGION_COORDS.items():
        is_sel = (area == selected_area)
        pal    = PALETTE.get(area, {"fill": "#ffffff", "glow": "rgba(255,255,255,0.2)"})
        color  = pal["fill"]
        glow   = pal["glow"]

        # Outer glow ring (selected only)
        if is_sel:
            folium.Circle(
                location=coords,
                radius=38000,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.07,
                weight=0,
            ).add_to(m)

        # Main filled circle
        folium.Circle(
            location=coords,
            radius=22000 if is_sel else 15000,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.5 if is_sel else 0.2,
            weight=2.5 if is_sel else 1.5,
            tooltip=folium.Tooltip(
                f"<b style='color:{color};font-size:13px'>{area}</b>",
                sticky=False,
            ),
        ).add_to(m)

        # Label marker
        pin = "📍 " if is_sel else ""
        folium.Marker(
            location=coords,
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    font-family:'Inter',sans-serif;
                    font-size:{'14px' if is_sel else '11px'};
                    font-weight:{'800' if is_sel else '500'};
                    color:#ffffff;
                    text-shadow:0 0 8px {glow}, 0 1px 4px rgba(0,0,0,0.9);
                    white-space:nowrap;
                    transform:translate(-50%,-50%);
                    pointer-events:none;
                ">{pin}{area}</div>""",
                icon_size=(90, 28),
                icon_anchor=(45, 14),
            ),
        ).add_to(m)

    return m


# ===========================================================================
# Helper: weather description based on temp
# ===========================================================================
def temp_desc(maxt: float) -> str:
    if maxt >= 35: return "🌡️ 酷熱"
    if maxt >= 30: return "☀️ 炎熱"
    if maxt >= 25: return "⛅ 溫暖"
    if maxt >= 18: return "🌤️ 舒適"
    if maxt >= 10: return "🧥 涼冷"
    return "🧣 寒冷"


# ===========================================================================
# Main App
# ===========================================================================

def main():
    import datetime

    # ── Hero Header ─────────────────────────────────────────────────────────
    now_str = datetime.datetime.now().strftime("%Y 年 %m 月 %d 日  %H:%M")
    st.markdown(f"""
    <div class="hero">
      <div class="hero-inner">
        <div class="hero-badge">🌤️</div>
        <div class="hero-text">
          <h1 class="hero-title">臺灣 7 天天氣預報儀表板</h1>
          <div class="hero-sub">
            <span class="hero-tag">📡 中央氣象署 CWA</span>
            <span class="hero-tag">🗄️ SQLite3 資料庫</span>
            <span class="hero-tag">🗺️ 互動式地圖</span>
          </div>
        </div>
        <div class="hero-right">
          <div class="hero-date">
            <span class="live-dot"></span>即時資料<br>
            {now_str}
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Load data ────────────────────────────────────────────────────────────
    df_all = load_all_data()
    if df_all.empty:
        st.warning("⚠️ 資料庫為空或不存在，請先執行 `python3 hw2_fetch.py`。")
        st.stop()

    available_areas = list(DISPLAY_REGIONS.keys())

    # ── Area selection (radio → hidden, we use selectbox for simplicity) ─────
    col_left, col_right = st.columns([1, 1.65], gap="large")

    # ════════════════════════════════════════════════════════════════════════
    # LEFT COLUMN
    # ════════════════════════════════════════════════════════════════════════
    with col_left:
        # Region selector card
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">📍 選擇地區</div>', unsafe_allow_html=True)
        selected_area = st.selectbox(
            label="地區",
            options=available_areas,
            label_visibility="collapsed",
            key="region_select",
        )
        counties = "　".join(DISPLAY_REGIONS.get(selected_area, []))
        st.markdown(f'<div class="county-tag">🏙️ {counties}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Map card
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🗺️ 地區分布圖</div>', unsafe_allow_html=True)
        taiwan_map = build_map(selected_area)
        st_folium(
            taiwan_map,
            width="100%",
            height=440,
            returned_objects=[],
            key="taiwan_map",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN
    # ════════════════════════════════════════════════════════════════════════
    with col_right:
        region_df = get_region_data(df_all, selected_area)
        if region_df.empty:
            st.warning(f"找不到 **{selected_area}** 的資料，請確認資料庫內容。")
            st.stop()

        overall_min = round(region_df["mint"].min(), 1)
        overall_max = round(region_df["maxt"].max(), 1)
        avg_min     = round(region_df["mint"].mean(), 1)
        avg_max     = round(region_df["maxt"].mean(), 1)
        temp_range  = round(overall_max - overall_min, 1)
        desc        = temp_desc(avg_max)

        # ── Metric cards ────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="metrics-grid">
            <div class="metric-card days">
                <div class="metric-label">📅 預報天數</div>
                <div class="metric-val days">{len(region_df)}<span class="metric-unit"> 天</span></div>
            </div>
            <div class="metric-card cold">
                <div class="metric-label">🥶 最低氣溫</div>
                <div class="metric-val cold">{overall_min}<span class="metric-unit"> °C</span></div>
            </div>
            <div class="metric-card hot">
                <div class="metric-label">🔥 最高氣溫</div>
                <div class="metric-val hot">{overall_max}<span class="metric-unit"> °C</span></div>
            </div>
            <div class="metric-card avg">
                <div class="metric-label">📊 平均最低</div>
                <div class="metric-val avg">{avg_min}<span class="metric-unit"> °C</span></div>
            </div>
            <div class="metric-card avg">
                <div class="metric-label">📊 平均最高</div>
                <div class="metric-val avg">{avg_max}<span class="metric-unit"> °C</span></div>
            </div>
            <div class="metric-card range">
                <div class="metric-label">🌡️ 天氣概況</div>
                <div class="metric-val range" style="font-size:1.15rem">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Line chart ──────────────────────────────────────────────────────
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">📈 氣溫折線圖</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="chart-title">{selected_area} ─ 最高 / 最低氣溫趨勢</div>
        <div class="chart-legend">
            <div class="legend-item">
                <div class="legend-dot" style="background:#38bdf8"></div>
                最低氣溫 MinT
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background:#f87171"></div>
                最高氣溫 MaxT
            </div>
        </div>
        """, unsafe_allow_html=True)

        chart_df = region_df.set_index("dataDate")[["mint", "maxt"]].copy()
        chart_df.index = chart_df.index.strftime("%m/%d")
        chart_df.columns = ["最低氣溫 MinT (°C)", "最高氣溫 MaxT (°C)"]

        st.line_chart(
            chart_df,
            color=["#38bdf8", "#f87171"],
            height=280,
            width="stretch",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Data table ──────────────────────────────────────────────────────
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-label">📋 {selected_area} 週預報資料表</div>',
            unsafe_allow_html=True,
        )

        display_df = region_df.copy()
        display_df["dataDate"] = display_df["dataDate"].dt.strftime("%Y-%m-%d")
        # Add temperature range column
        display_df["range"] = (display_df["maxt"] - display_df["mint"]).round(1)
        display_df.columns = ["日期", "最低氣溫 (°C)", "最高氣溫 (°C)", "溫差 (°C)"]

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
            column_config={
                "日期":         st.column_config.TextColumn("📅 日期", width="medium"),
                "最低氣溫 (°C)": st.column_config.NumberColumn(
                    "🥶 最低氣溫",
                    format="%.1f °C",
                    width="medium",
                ),
                "最高氣溫 (°C)": st.column_config.NumberColumn(
                    "🔥 最高氣溫",
                    format="%.1f °C",
                    width="medium",
                ),
                "溫差 (°C)": st.column_config.ProgressColumn(
                    "↕ 溫差",
                    format="%.1f °C",
                    min_value=0,
                    max_value=20,
                    width="medium",
                ),
            },
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Raw records expander ─────────────────────────────────────────────
        with st.expander("🗄️ 查看各縣市原始資料庫記錄"):
            raw = df_all[df_all["area"] == selected_area].copy()
            st.dataframe(raw, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
