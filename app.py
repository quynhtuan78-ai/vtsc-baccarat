import streamlit as st

# --- CẤU HÌNH APP ---
st.set_page_config(
    page_title="VTSC Master AI v6.1",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS SỬA LỖI HIỂN THỊ ---
st.markdown("""
<style>
    .stApp { background-color: #0b0c10; color: #c5c6c7; }
    
    /* SỬA LỖI NÚT BẤM: Ép màu nền cứng bằng !important */
    div.stButton > button {
        width: 100%; height: 80px; font-weight: 900; font-size: 24px !important;
        border-radius: 12px; color: white !important;
        border: 2px solid rgba(255,255,255,0.2);
        text-shadow: 0 1px 2px black;
    }
    div.stButton > button:hover { transform: scale(1.02); }

    /* Định danh màu cụ thể cho từng cột */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { 
        background: linear-gradient(180deg, #3498db, #2980b9) !important; 
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { 
        background: linear-gradient(180deg, #e74c3c, #c0392b) !important; 
    }
    div[data-testid="column"]:nth-of-type(3) div.stButton > button { 
        background: linear-gradient(180deg, #27ae60, #2ecc71) !important; 
    }

    /* Khung dự đoán */
    .prediction-card {
        background: #1f2833; border: 2px solid #45a29e; border-radius: 15px;
        padding: 20px; text-align: center; margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(69, 162, 158, 0.3);
    }
    
    /* Bảng thống kê */
    .stat-box {
        background: #111; border: 1px solid #333; border-radius: 10px;
        padding: 10px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU ---
if 'history' not in st.session_state: st.session_state.history = []
if 'wins' not in st.session_state: st.session_state.wins = 0
if 'losses' not in st.session_state: st.session_state.losses = 0

# --- LOGIC PHÂN TÍCH (GIỮ NGUYÊN v6.0) ---
def analyze_v6(history):
    clean_hist = [x for x in history if x != 'T']
    
    if len(clean_hist) < 3:
        return "⏳ Đang quét nhịp sàn...", "WAIT", 0, "#666"

    h1 = clean_hist[-1]
    h2 = clean_hist[-2]
    h3 = clean_hist[-3]
    
    # 1. CẦU 2-2 (Cặp)
    if len(clean_hist) >= 4:
        h4 = clean_hist[-4]
        if h1 == h2 and h3 == h4 and h1 != h3:
            guess = 'P' if h1 == 'B' else 'B'
            return f"💎 CẦU 2-2: {guess_full(guess)}", guess, 85, get_color(guess)

    # 2. CẦU BỆT
    if h1 == h2 == h3:
        return f"🐉 CẦU BỆT: {guess_full(h1)}", h1, 90, get_color(h1)

    # 3. CẦU 1-1
    if h1 != h2 and h2 != h3:
        guess = 'P' if h1 == 'B' else 'B'
        return f"🏓 CẦU 1-1: {guess_full(guess)}", guess, 80, get_color(guess)

    # 4. CẦU 1-2
    if h1 == h2 and h2 != h3:
        guess = h3
        return f"🔄 CẦU 1-2: {guess_full(guess)}", guess, 70, get_color(guess)

    # 5. XU HƯỚNG
    if len(clean_hist) >= 6:
        b_count = clean_hist[-6:].count('B')
        if b_count >= 4: return "📊 XU HƯỚNG: BANKER", 'B', 60, "#C0392B"
        if b_count <= 2: return "📊 XU HƯỚNG: PLAYER", 'P', 60, "#2980B9"

    return "👀 Cầu Loạn - Tạm Ngưng", "SKIP", 0, "#444"

def guess_full(code): return "BANKER" if code == 'B' else "PLAYER"
def get_color(code): return "#C0392B" if code == 'B' else "#2980B9"

# --- XỬ LÝ ---
def process(result):
    _, pred_code, _, _ = analyze_v6(st.session_state.history)
    if pred_code not in ["SKIP", "WAIT"] and result != 'T':
        if pred_code == result:
            st.session_state.wins += 1
            st.toast("WIN! +1", icon="💰")
        else:
            st.session_state.losses += 1
            st.toast("Loss!", icon="🔥")
    st.session_state.history.append(result)

# --- GIAO DIỆN ---
st.title("💎 VTSC MASTER AI v6.1")

# KHUNG DỰ ĐOÁN (Đã sửa lỗi HTML)
msg, pred, conf, col = analyze_v6(st.session_state.history)

# Viết HTML sát lề trái để tránh lỗi hiển thị code
st.markdown(f"""
<div class="prediction-card" style="border-color: {col}; box-shadow: 0 0 30px {col}40;">
<h3 style="color:#aaa; margin:0">AI PHÂN TÍCH</h3>
<h1 style="color:{col}; font-size:40px; margin:10px 0;">{msg.split(':')[0]}</h1>
<h2 style="color:white; font-size:45px; margin:0;">{msg.split(':')[-1] if ':' in msg else ''}</h2>
<div style="margin-top:15px; background:#111; height:8px; border-radius:4px; width:100%;">
<div style="width:{conf}%; background:{col}; height:100%; border-radius:4px;"></div>
</div>
<p style="color:#888; margin-top:5px;">Độ tin cậy: {conf}%</p>
</div>
""", unsafe_allow_html=True)

# GỢI Ý TIỀN
if conf >= 85: advice, adv_col = "💰 CƯỢC MẠNH (Big Bet)", "#2ecc71"
elif conf >= 70: advice, adv_col = "⚖️ Cược Đều Tay", "#f1c40f"
elif conf > 0: advice, adv_col = "🛡️ Cược Nhỏ", "#95a5a6"
else: advice, adv_col = "⛔ KHÔNG VÀO TIỀN", "#e74c3c"

st.markdown(f"<h3 style='text-align:center; color:{adv_col}'>{advice}</h3>", unsafe_allow_html=True)

# BÀN PHÍM
c1, c2, c3 = st.columns(3)
with c1: 
    if st.button("🔵 PLAYER"): process('P'); st.rerun()
with c2: 
    if st.button("🔴 BANKER"): process('B'); st.rerun()
with c3: 
    if st.button("🟢 TIE"): process('T'); st.rerun()

# THỐNG KÊ & ROADMAP
st.markdown("---")
col_s, col_r = st.columns([1, 2])

with col_s:
    win, loss = st.session_state.wins, st.session_state.losses
    total = win + loss
    rate = int(win/total*100) if total > 0 else 0
    st.markdown(f"""
    <div class="stat-box">
        <div style="color:#66fcf1; font-size:32px;">{win} <span style="font-size:16px; color:#888">WIN</span></div>
        <div style="color:#e74c3c; font-size:24px;">{loss} <span style="font-size:16px; color:#888">LOSS</span></div>
        <div style="color:#aaa; margin-top:5px;">Win Rate: <b style="color:white">{rate}%</b></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🗑️ Xóa Bàn"):
        st.session_state.history = []; st.session_state.wins = 0; st.session_state.losses = 0; st.rerun()

with col_r:
    if st.session_state.history:
        # Viết HTML trên 1 dòng để tránh lỗi
        h_code = '<div style="display:flex; gap:5px; flex-wrap:wrap; background:#111; padding:10px; border-radius:10px;">'
        for item in st.session_state.history:
            if item == 'P': bg, t = "#3498db", "P"
            elif item == 'B': bg, t = "#e74c3c", "B"
            else: bg, t = "#2ecc71", "T"
            h_code += f'<div style="width:30px; height:30px; background:{bg}; border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold;">{t}</div>'
        h_code += '</div>'
        st.markdown(h_code, unsafe_allow_html=True)
    else:
        st.info("👈 Nhập 3 ván đầu tiên...")