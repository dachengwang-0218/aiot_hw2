"""
hw2_app.py  ─  HW2-4  (Luxury Gold Edition)
Usage: python3 -m streamlit run hw2_app.py
"""

import sqlite3, datetime
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from config import DB_PATH, DISPLAY_REGIONS, REGION_COORDS

st.set_page_config(
    page_title="臺灣天氣預報 · 尊爵版",
    page_icon="♛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
#  LUXURY CSS DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ══ FONTS ══════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600&family=Cormorant+Garamond:ital,wght@0,300;0,500;1,300&display=swap');

/* ══ TOKENS ══════════════════════════════════════════════════ */
:root{
  --black:   #050507;
  --ink:     #0a0a0f;
  --surface: #0f0f17;
  --card:    #13131d;
  --card2:   #16162280;

  --gold-1:  #D4AF37;
  --gold-2:  #C9A84C;
  --gold-3:  #F5E17A;
  --gold-4:  #8B6914;
  --gold-dim: rgba(212,175,55,0.12);
  --gold-glow:rgba(212,175,55,0.20);
  --gold-line:rgba(212,175,55,0.22);

  --txt-1:   #F5EFD8;
  --txt-2:   #9A8E72;
  --txt-3:   #4A4436;

  --cold:    #7EC8E3;
  --hot:     #E8956D;
  --green:   #6EC497;

  --r:       14px;
  --r-lg:    20px;

  --sh: 0 2px 4px rgba(0,0,0,.6), 0 12px 40px rgba(0,0,0,.7), 0 0 0 1px var(--gold-line);
  --sh-lift: 0 4px 8px rgba(0,0,0,.7), 0 24px 64px rgba(0,0,0,.8), 0 0 0 1px rgba(212,175,55,.35);
}

/* ══ RESET ══════════════════════════════════════════════════ */
*,*::before,*::after{box-sizing:border-box;margin:0}

html,body,[class*="css"],.stApp{
  font-family:'Inter',sans-serif;
  background:var(--black) !important;
  color:var(--txt-1);
}

/* Rich background: deep black + radial gold halos + fine grid */
.stApp{
  background-image:
    linear-gradient(rgba(212,175,55,.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(212,175,55,.018) 1px, transparent 1px),
    radial-gradient(ellipse 70% 50% at 80% 5%,  rgba(212,175,55,.07) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 5%  95%,  rgba(212,175,55,.04) 0%, transparent 55%),
    radial-gradient(ellipse 90% 70% at 50% 50%, rgba(5,5,7,0) 40%, #050507 100%) !important;
  background-size:48px 48px, 48px 48px, 100% 100%, 100% 100%, 100% 100% !important;
  background-attachment:fixed !important;
}

#MainMenu,footer,header{visibility:hidden}
.block-container{padding:2.2rem 3rem !important; max-width:1700px !important}

/* ══ KEYFRAMES ═══════════════════════════════════════════════ */
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes shimmer{
  0%  {background-position:200% center}
  100%{background-position:-200% center}
}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes spin-slow{to{transform:rotate(360deg)}}

/* ══ ORNAMENTAL DIVIDER ══════════════════════════════════════ */
.divider{
  display:flex;align-items:center;gap:14px;
  margin:6px 0 20px;
}
.divider-line{flex:1;height:1px;background:linear-gradient(90deg,transparent,var(--gold-line),transparent)}
.divider-gem{
  width:7px;height:7px;
  background:var(--gold-2);
  transform:rotate(45deg);
  flex-shrink:0;
  box-shadow:0 0 8px var(--gold-glow);
}

/* ══ HERO ════════════════════════════════════════════════════ */
.hero{
  position:relative;
  padding:44px 52px;
  margin-bottom:32px;
  background:var(--card);
  border:1px solid var(--gold-line);
  border-radius:var(--r-lg);
  box-shadow:var(--sh);
  overflow:hidden;
  animation:fadeUp .6s cubic-bezier(.23,1,.32,1) both;
}
/* top shimmer stripe */
.hero::before{
  content:'';
  position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent 0%,var(--gold-1) 30%,var(--gold-3) 50%,var(--gold-1) 70%,transparent 100%);
  background-size:200% auto;
  animation:shimmer 4s linear infinite;
}
/* ambient glow */
.hero::after{
  content:'';
  position:absolute;top:-80px;right:-80px;
  width:320px;height:320px;
  background:radial-gradient(circle,var(--gold-dim) 0%,transparent 65%);
  pointer-events:none;border-radius:50%;
}
.hero-inner{
  position:relative;z-index:1;
  display:flex;align-items:center;gap:28px;
}
.crown{
  width:64px;height:64px;
  background:linear-gradient(135deg,var(--gold-4),var(--gold-1),var(--gold-3));
  border-radius:var(--r);
  display:flex;align-items:center;justify-content:center;
  font-size:1.8rem;flex-shrink:0;
  box-shadow:0 0 32px var(--gold-glow), 0 0 64px rgba(212,175,55,.1);
}
.hero-heading{
  font-family:'Playfair Display',serif;
  font-size:2rem;font-weight:700;
  letter-spacing:-0.01em;line-height:1.15;
  background:linear-gradient(105deg,var(--txt-1) 0%,var(--gold-3) 45%,var(--txt-1) 100%);
  background-size:200% auto;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
  animation:shimmer 6s linear infinite;
}
.hero-italic{
  font-family:'Cormorant Garamond',serif;
  font-style:italic;font-size:1rem;
  color:var(--txt-2);margin-top:5px;letter-spacing:.04em;
}
.hero-tags{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.tag{
  display:inline-flex;align-items:center;gap:5px;
  border:1px solid var(--gold-line);
  border-radius:20px;padding:3px 11px;
  font-size:.68rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;
  color:var(--gold-2);
  background:var(--gold-dim);
}
.hero-right{margin-left:auto;text-align:right}
.live-badge{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(110,196,151,.1);
  border:1px solid rgba(110,196,151,.25);
  border-radius:20px;padding:4px 12px;
  font-size:.68rem;font-weight:600;letter-spacing:.08em;
  text-transform:uppercase;color:#6EC497;
}
.live-dot{width:6px;height:6px;border-radius:50%;background:#6EC497;animation:blink 2s ease-in-out infinite}
.hero-time{font-family:'Cormorant Garamond',serif;font-size:1rem;color:var(--txt-3);margin-top:8px}

/* ══ CARDS ═══════════════════════════════════════════════════ */
.card{
  background:var(--card);
  border:1px solid var(--gold-line);
  border-radius:var(--r-lg);
  padding:22px 24px;
  margin-bottom:16px;
  box-shadow:var(--sh);
  transition:border-color .35s ease,box-shadow .35s ease,transform .3s ease;
  animation:fadeUp .55s cubic-bezier(.23,1,.32,1) both;
}
.card:hover{
  border-color:rgba(212,175,55,.45);
  box-shadow:var(--sh-lift);
  transform:translateY(-2px);
}
.card-title{
  font-family:'Playfair Display',serif;
  font-size:.75rem;font-weight:600;
  letter-spacing:.14em;text-transform:uppercase;
  color:var(--gold-2);margin-bottom:6px;
}

/* ══ SELECTBOX ═══════════════════════════════════════════════ */
div[data-baseweb="select"]>div{
  background:rgba(212,175,55,.05) !important;
  border:1px solid var(--gold-line) !important;
  border-radius:var(--r) !important;
  color:var(--txt-1) !important;
  font-family:'Inter',sans-serif !important;
}
div[data-baseweb="select"]>div:focus-within{
  border-color:var(--gold-2) !important;
  box-shadow:0 0 0 3px var(--gold-dim) !important;
}
.counties{font-size:.72rem;color:var(--txt-3);margin-top:8px;line-height:1.8;letter-spacing:.01em}

/* ══ METRICS GRID ════════════════════════════════════════════ */
.mgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px}
.mc{
  background:var(--card);
  border:1px solid var(--gold-line);
  border-radius:var(--r);
  padding:16px 18px 14px;
  position:relative;overflow:hidden;
  transition:transform .28s ease,border-color .28s ease,box-shadow .28s ease;
  animation:fadeUp .6s cubic-bezier(.23,1,.32,1) both;
}
.mc::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1.5px;
  background:linear-gradient(90deg,transparent,var(--accent-c),transparent);
}
.mc.g::before{--accent-c:#D4AF37}
.mc.b::before{--accent-c:var(--cold)}
.mc.r::before{--accent-c:var(--hot)}
.mc.e::before{--accent-c:var(--green)}
.mc:hover{transform:translateY(-3px);border-color:rgba(212,175,55,.35);box-shadow:0 8px 32px rgba(0,0,0,.6)}
.mc-lbl{
  font-size:.6rem;font-weight:600;letter-spacing:.12em;
  text-transform:uppercase;color:var(--txt-3);margin-bottom:8px;
}
.mc-val{
  font-family:'Playfair Display',serif;
  font-size:1.7rem;font-weight:700;letter-spacing:-.02em;line-height:1;
}
.mc-unit{font-size:.78rem;font-weight:400;opacity:.5}
.cv-gold{color:var(--gold-1)}
.cv-cold{color:var(--cold)}
.cv-hot {color:var(--hot) }
.cv-green{color:var(--green)}

/* ══ LEGEND ══════════════════════════════════════════════════ */
.legend{display:flex;gap:20px;margin-bottom:10px}
.leg{display:flex;align-items:center;gap:7px}
.leg-bar{width:22px;height:2px;border-radius:2px}
.leg-txt{font-size:.7rem;color:var(--txt-2)}

/* ══ TABLE ═══════════════════════════════════════════════════ */
.stDataFrame{border-radius:var(--r) !important;overflow:hidden !important}

/* ══ IFRAME ══════════════════════════════════════════════════ */
iframe{
  border-radius:var(--r) !important;
  border:1px solid var(--gold-line) !important;
  box-shadow:0 4px 24px rgba(0,0,0,.6), 0 0 0 1px rgba(212,175,55,.05) !important;
}

/* ══ EXPANDER ════════════════════════════════════════════════ */
details{background:rgba(212,175,55,.03) !important;border:1px solid var(--gold-line) !important;border-radius:var(--r) !important}
details summary{color:var(--txt-2) !important;font-size:.75rem !important;font-weight:500 !important;padding:8px 14px !important;cursor:pointer !important}
details summary:hover{color:var(--gold-2) !important}

/* ══ MISC ════════════════════════════════════════════════════ */
hr{border:none !important;border-top:1px solid var(--gold-line) !important;margin:16px 0 !important}
.stCaption,small{color:var(--txt-3) !important;font-size:.7rem !important}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_all_data(db_path=DB_PATH) -> pd.DataFrame:
    try:
        conn = sqlite3.connect(db_path)
        df   = pd.read_sql_query("SELECT * FROM TemperatureForecasts ORDER BY dataDate ASC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ 資料庫讀取失敗：{e}　→　請先執行 `python3 hw2_fetch.py`")
        return pd.DataFrame()

def get_region_data(df, area):
    sub = df[df["area"]==area].copy()
    if sub.empty: return sub
    agg = (sub.groupby("dataDate",as_index=False)
              .agg(mint=("mint","mean"),maxt=("maxt","mean")).round(1))
    agg["dataDate"] = pd.to_datetime(agg["dataDate"])
    return agg.head(7)  # 只取前 7 天

def wx_label(t):
    if t>=35: return "酷暑 🌡"
    if t>=30: return "炎熱 ☀️"
    if t>=25: return "溫暖 ⛅"
    if t>=18: return "舒適 🌤"
    if t>=10: return "涼爽 🍂"
    return "嚴寒 ❄️"

# ─────────────────────────────────────────────────────────────
#  MAP
# ─────────────────────────────────────────────────────────────
GOLD_PAL = {
    "北部": "#D4AF37","中部": "#C9A84C","南部": "#E8C573",
    "東北部":"#B8960C","東部":"#F0D060","東南部":"#A07830",
}

def build_map(sel):
    m = folium.Map(location=(23.6,121.0), zoom_start=7,
                   tiles="CartoDB dark_matter", scrollWheelZoom=False)
    for area, coords in REGION_COORDS.items():
        is_sel = area==sel
        c = GOLD_PAL.get(area,"#D4AF37")
        if is_sel:
            folium.Circle(location=coords,radius=46000,
                          color=c,fill=True,fill_color=c,
                          fill_opacity=.07,weight=0).add_to(m)
        folium.Circle(
            location=coords,
            radius=21000 if is_sel else 13000,
            color=c,fill=True,fill_color=c,
            fill_opacity=.6 if is_sel else .2,
            weight=1.5 if is_sel else 1,
            tooltip=folium.Tooltip(f"<b style='color:{c};font-size:12px;font-family:serif'>{area}</b>"),
        ).add_to(m)
        pre = "♦ " if is_sel else ""
        folium.Marker(
            location=coords,
            icon=folium.DivIcon(
                html=f"""<div style="
                    font-family:'Playfair Display',serif;
                    font-size:{'13px' if is_sel else '10px'};
                    font-weight:{'700' if is_sel else '400'};
                    color:#fff;letter-spacing:.04em;
                    text-shadow:0 0 12px {c}aa,0 1px 4px rgba(0,0,0,0.95);
                    white-space:nowrap;transform:translate(-50%,-50%);
                    pointer-events:none">{pre}{area}</div>""",
                icon_size=(90,24),icon_anchor=(45,12),
            ),
        ).add_to(m)
    return m

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
def main():
    now = datetime.datetime.now()

    # ── HERO ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero">
      <div class="hero-inner">
        <div class="crown">♛</div>
        <div>
          <div class="hero-heading">臺灣天氣預報儀表板</div>
          <div class="hero-italic">Taiwan 7-Day Weather Forecast · Curated with Excellence</div>
          <div class="hero-tags">
            <span class="tag">♦ 中央氣象署 CWA</span>
            <span class="tag">◈ SQLite3 Database</span>
            <span class="tag">◉ Folium Maps</span>
          </div>
        </div>
        <div class="hero-right">
          <div class="live-badge"><span class="live-dot"></span>即時資料</div>
          <div class="hero-time">{now.strftime("%Y · %m · %d")}<br>{now.strftime("%H : %M")}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── DATA ──────────────────────────────────────────────────
    df_all = load_all_data()
    if df_all.empty:
        st.warning("⚠️ 資料庫為空，請執行 `python3 hw2_fetch.py`")
        st.stop()
    areas = list(DISPLAY_REGIONS.keys())

    L, R = st.columns([1, 1.75], gap="large")

    # ══ LEFT ══════════════════════════════════════════════════
    with L:
        # Selector
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">♦ 選擇地區</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"><div class="divider-line"></div><div class="divider-gem"></div><div class="divider-line"></div></div>', unsafe_allow_html=True)
        sel = st.selectbox("area", areas, label_visibility="collapsed", key="sel")
        counties = "　".join(DISPLAY_REGIONS.get(sel,[]))
        st.markdown(f'<div class="counties">涵蓋區域：{counties}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Map
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">◉ 地區分布圖</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"><div class="divider-line"></div><div class="divider-gem"></div><div class="divider-line"></div></div>', unsafe_allow_html=True)
        st_folium(build_map(sel), width="100%", height=430, returned_objects=[], key="map")
        st.markdown('</div>', unsafe_allow_html=True)

    # ══ RIGHT ═════════════════════════════════════════════════
    with R:
        rdf = get_region_data(df_all, sel)
        if rdf.empty:
            st.warning(f"找不到 {sel} 的資料"); st.stop()

        vmin  = round(rdf["mint"].min(),1)
        vmax  = round(rdf["maxt"].max(),1)
        a_min = round(rdf["mint"].mean(),1)
        a_max = round(rdf["maxt"].mean(),1)

        # ── Metrics
        st.markdown(f"""
        <div class="mgrid">
          <div class="mc e">
            <div class="mc-lbl">預報天數</div>
            <div class="mc-val cv-green">{len(rdf)}<span class="mc-unit"> 天</span></div>
          </div>
          <div class="mc b">
            <div class="mc-lbl">最低氣溫</div>
            <div class="mc-val cv-cold">{vmin}<span class="mc-unit"> °C</span></div>
          </div>
          <div class="mc r">
            <div class="mc-lbl">最高氣溫</div>
            <div class="mc-val cv-hot">{vmax}<span class="mc-unit"> °C</span></div>
          </div>
          <div class="mc g">
            <div class="mc-lbl">平均最低</div>
            <div class="mc-val cv-gold">{a_min}<span class="mc-unit"> °C</span></div>
          </div>
          <div class="mc g">
            <div class="mc-lbl">平均最高</div>
            <div class="mc-val cv-gold">{a_max}<span class="mc-unit"> °C</span></div>
          </div>
          <div class="mc g">
            <div class="mc-lbl">天氣概況</div>
            <div class="mc-val cv-gold" style="font-size:1.05rem;margin-top:4px">{wx_label(a_max)}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Chart
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">◈ 氣溫折線圖</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"><div class="divider-line"></div><div class="divider-gem"></div><div class="divider-line"></div></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-style:italic;
             font-size:.92rem;color:var(--txt-2);margin-bottom:10px">
          {sel} — 七日溫度趨勢
        </div>
        <div class="legend">
          <div class="leg"><div class="leg-bar" style="background:#7EC8E3"></div><span class="leg-txt">最低氣溫 MinT</span></div>
          <div class="leg"><div class="leg-bar" style="background:#E8956D"></div><span class="leg-txt">最高氣溫 MaxT</span></div>
        </div>
        """, unsafe_allow_html=True)
        cdf = rdf.set_index("dataDate")[["mint","maxt"]].copy()
        cdf.index   = cdf.index.strftime("%m/%d")
        cdf.columns = ["最低氣溫 MinT (°C)","最高氣溫 MaxT (°C)"]
        st.line_chart(cdf, color=["#7EC8E3","#E8956D"], height=260, width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Table
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">♦ {sel} 週預報資料表</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"><div class="divider-line"></div><div class="divider-gem"></div><div class="divider-line"></div></div>', unsafe_allow_html=True)
        tdf = rdf.copy()
        tdf["dataDate"] = tdf["dataDate"].dt.strftime("%Y-%m-%d")
        tdf["range"]    = (tdf["maxt"]-tdf["mint"]).round(1)
        tdf.columns     = ["日期","最低氣溫 (°C)","最高氣溫 (°C)","溫差 (°C)"]
        st.dataframe(tdf, width="stretch", hide_index=True, column_config={
            "日期":         st.column_config.TextColumn("📅 日期",          width="medium"),
            "最低氣溫 (°C)": st.column_config.NumberColumn("🥶 最低",        format="%.1f °C", width="small"),
            "最高氣溫 (°C)": st.column_config.NumberColumn("🔥 最高",        format="%.1f °C", width="small"),
            "溫差 (°C)":    st.column_config.ProgressColumn("↕ 溫差", format="%.1f °C",
                              min_value=0, max_value=20, width="medium"),
        })
        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("◈ 原始資料庫記錄（各縣市）"):
            raw = df_all[df_all["area"]==sel].copy()
            st.dataframe(raw, width="stretch", hide_index=True)

if __name__ == "__main__":
    main()
