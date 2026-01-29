import streamlit as st

# --- CẤU HÌNH APP (v13.0 - HYBRID DRAGON) ---
st.set_page_config(
    page_title="VTSC AI v13.0 - Hybrid Dragon",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS CAO CẤP ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ecf0f1; }
    
    div.stButton > button {
        width: 100%; height: 85px; font-weight: 900; font-size: 26px !important;
        border-radius: 10px; color: white !important;
        border: 1px solid #333; box-shadow: 0 4px 0 #111;
        transition: all 0.1s;
    }
    div.stButton > button:active { transform: translateY(3px); box-shadow: none; }

    div[data-testid="column"]:nth-of-type(1) div.stButton > button { background: #2980b9 !important; border-bottom: 4px solid #1c5980 !important; }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { background: #c0392b !important; border-bottom: 4px solid #7e241b !important; }
    div[data-testid="column"]:nth-of-type(3) div.stButton > button { background: #27ae60 !important; border-bottom: 4px solid #196f3d !important; }

    .card { background: #1a1a1a; border: 2px solid #333; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 30px rgba(255,255,255,0.05); }
    .dragon-mode { border-color: #f1c40f !important; box-shadow: 0 0 40px #f1c40f50 !important; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'wins' not in st.session_state: st.session_state.wins = 0
if 'losses' not in st.session_state: st.session_state.losses = 0

# --- CÔNG CỤ CẦU PHỤ (Giữ lại từ v12) ---
def build_big_road(history):
    clean = [x for x in history if x != 'T']
    if not clean: return []
    big_road = []
    current_col = [clean[0]]
    for i in range(1, len(clean)):
        if clean[i] == clean[i-1]: current_col.append(clean[i])
        else: big_road.append(current_col); current_col = [clean[i]]
    big_road.append(current_col)
    return big_road

def get_derived_signal(big_road, simulate_result):
    temp_road = [col[:] for col in big_road]
    if not temp_road: temp_road = [[simulate_result]]
    else:
        if temp_road[-1][-1] == simulate_result: temp_road[-1].append(simulate_result)
        else: temp_road.append([simulate_result])
    score = 0
    if len(temp_road) >= 2: # Big Eye
        if len(temp_road[-1]) == len(temp_road[-2]): score += 1
    if len(temp_road) >= 3: # Small Road
        if len(temp_road[-1]) == len(temp_road[-3]): score += 1
    return score

# --- LOGIC TRUNG TÂM v13.0 (XỬ LÝ BỆT + CẦU PHỤ) ---
def analyze_v13(history):
    clean = [x for x in history if x != 'T']
    if len(clean) < 4: return "⏳ Chờ thêm cầu...", "WAIT", 0, "#444"

    h1 = clean[-1]
    h2 = clean[-2]
    h3 = clean[-3]
    h4 = clean[-4] if len(clean) >= 4 else None

    # --- ƯU TIÊN SỐ 1: BẮT BUỘC BÁM BỆT (DRAGON MODE) ---
    # Nếu thấy 4 cây giống nhau -> BỎ QUA mọi chỉ số cầu phụ -> BÁM THEO
    if h4 and h1 == h2 and h2 == h3 and h3 == h4:
        guess = h1
        return f"🔥 RỒNG XUẤT HIỆN (Bám {h1})", guess, 99, get_color(guess)

    # --- ƯU TIÊN SỐ 2: SOI CẦU PHỤ (ASK TYPE) - Chỉ chạy khi KHÔNG CÓ BỆT ---
    big_road = build_big_road(clean)
    score_P = get_derived_signal(big_road, 'P')
    score_B = get_derived_signal(big_road, 'B')

    final_pick = None
    reason = ""
    conf = 0

    # Logic Soi Cầu Phụ
    if score_B > score_P:
        final_pick = 'B'; reason = "🔮 CẦU PHỤ BÁO: BANKER"; conf = 85
    elif score_P > score_B:
        final_pick = 'P'; reason = "🔮 CẦU PHỤ BÁO: PLAYER"; conf = 85
    else:
        # Nếu cầu phụ hòa, dùng cầu chính cơ bản
        if h3 and h1 == h2 and h2 == h3: # Săn 3-1 (Bẻ)
             final_pick = 'P' if h1 == 'B' else 'B'; reason = "🔪 SĂN 3-1 (Bẻ Cầu)"; conf = 80
        elif h4 and h1 == h2 and h3 == h4 and h2 != h3: # Bắt 2-2
             final_pick = 'P' if h1 == 'B' else 'B'; reason = "💎 CẦU 2-2"; conf = 75
        elif h1 != h2: # Cầu 1-1
             final_pick = 'P' if h1 == 'B' else 'B'; reason = "🏓 CẦU 1-1"; conf = 70
        else:
             return "⚠️ Cầu Loạn - Tạm Dừng", "SKIP", 0, "#555"

    col = get_color(final_pick)
    return f"{reason}: {guess_full(final_pick)}", final_pick, conf, col

def guess_full(code): return "BANKER" if code == 'B' else "PLAYER"
def get_color(code): return "#c0392b" if code == 'B' else "#2980b9"

# --- XỬ LÝ ---
def process(result):
    _, pred, _, _ = analyze_v13(st.session_state.history)
    if pred not in ["SKIP", "WAIT"] and result != 'T':
        if pred == result:
            st.session_state.wins += 1
            st.toast("WIN! Tuyệt vời!", icon="💰")
        else:
            st.session_state.losses += 1
            st.toast("Thua! Gấp thếp...", icon="⚠️")
    st.session_state.history.append(result)

# --- GIAO DIỆN ---
st.title("🐉 VTSC v13.0 - HYBRID DRAGON")
st.caption("Chế độ: Gặp Rồng thì Bám - Gặp Loạn thì Soi")

msg, pred, conf, col = analyze_v13(st.session_state.history)

# CSS class đặc biệt nếu gặp Rồng
card_class = "card dragon-mode" if conf >= 95 else "card"

if pred in ["SKIP", "WAIT"]:
    st.markdown(f"<div class='{card_class}'><h2 style='color:#666'>{msg}</h2></div>", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="{card_class}" style="border-color: {col};">
        <h3 style="color:#aaa; margin:0;">AI CHỐT:</h3>
        <h1 style="color:{col}; font-size:50px; margin:5px 0;">{msg.split(':')[1] if ':' in msg else msg.split('(')[0]}</h1>
        <p style="color:#ddd;">{msg.split(':')[0] if ':' in msg else msg}</p>
        <div style="background:#333; height:10px; width:100%; border-radius:5px; margin-top:10px;">
            <div style="width:{conf}%; background:{col}; height:100%; border-radius:5px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# LỜI KHUYÊN TIỀN
if conf >= 95: advice = "🔥 TẤT TAY / BIG BET (Bám Bệt)"
elif conf >= 85: advice = "💰 ĐÁNH MẠNH (Cầu Đẹp)"
elif conf >= 70: advice = "⚖️ ĐÁNH ĐỀU TAY"
else: advice = "🛡️ QUAN SÁT"

adv_color = "#f1c40f" if conf >= 95 else col
st.markdown(f"<div style='text-align:center; color:{adv_color if conf>0 else '#666'}; font-weight:bold; margin-bottom:15px; font-size:20px; text-transform:uppercase;'>{advice}</div>", unsafe_allow_html=True)

# NÚT
c1, c2, c3 = st.columns(3)
with c1: 
    if st.button("🔵 PLAYER"): process('P'); st.rerun()
with c2: 
    if st.button("🔴 BANKER"): process('B'); st.rerun()
with c3: 
    if st.button("🟢 TIE"): process('T'); st.rerun()

st.markdown("---")
# THỐNG KÊ
col1, col2 = st.columns([1, 2])
with col1:
    w, l = st.session_state.wins, st.session_state.losses
    st.markdown(f"<div style='background:#111; padding:10px; border-radius:10px; text-align:center; border:1px solid #333;'><span style='color:#2ecc71; font-size:26px;'>{w} WIN</span> - <span style='color:#e74c3c; font-size:26px;'>{l} LOSS</span></div>", unsafe_allow_html=True)
    if st.button("🗑️ Xóa Bàn"): st.session_state.history = []; st.session_state.wins=0; st.session_state.losses=0; st.rerun()

with col2:
    if st.session_state.history:
        h_code = '<div style="display:flex; gap:4px; flex-wrap:wrap; background:#111; padding:10px; border-radius:10px;">'
        for item in st.session_state.history:
            if item == 'P': c="#2980b9"; t="P"
            elif item == 'B': c="#c0392b"; t="B"
            else: c="#27ae60"; t="T"
            h_code += f'<div style="width:30px;height:30px;background:{c};border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;">{t}</div>'
        h_code += '</div>'
        st.markdown(h_code, unsafe_allow_html=True)