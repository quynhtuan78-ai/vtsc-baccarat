import streamlit as st

# --- CẤU HÌNH APP (VTSC v10.0 - ALL IN ONE) ---
st.set_page_config(
    page_title="VTSC AI v10.0 - All In One",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS CAO CẤP ---
st.markdown("""
<style>
    .stApp { background-color: #000; color: #FFF; }
    div.stButton > button {
        width: 100%; height: 85px; font-weight: 900; font-size: 26px !important;
        border-radius: 12px; color: white !important;
        border: 1px solid #444; transition: all 0.1s;
    }
    div.stButton > button:active { transform: scale(0.95); }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { background: #2980B9 !important; border-bottom: 4px solid #154360 !important; }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { background: #C0392B !important; border-bottom: 4px solid #641E16 !important; }
    div[data-testid="column"]:nth-of-type(3) div.stButton > button { background: #27AE60 !important; border-bottom: 4px solid #145A32 !important; }
    .card { background: #111; border: 2px solid #555; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 30px rgba(255,255,255,0.05); }
</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'wins' not in st.session_state: st.session_state.wins = 0
if 'losses' not in st.session_state: st.session_state.losses = 0

# --- SIÊU THUẬT TOÁN v10.0 (Xử lý xung đột logic) ---
def analyze_v10(history):
    clean = [x for x in history if x != 'T']
    
    if len(clean) < 3:
        return "⏳ Chờ thêm dữ liệu...", "WAIT", 0, "#444"

    h1 = clean[-1] # Mới nhất
    h2 = clean[-2]
    h3 = clean[-3]
    h4 = clean[-4] if len(clean) >= 4 else None
    h5 = clean[-5] if len(clean) >= 5 else None

    # --- 1. ƯU TIÊN CAO NHẤT: BỆT DÀI (Dragon) ---
    # Nếu đã ra 4 cây -> Chắc chắn bám theo, không bẻ nữa
    if h4 and h1 == h2 and h2 == h3 and h3 == h4:
        guess = h1
        return f"🐉 BỆT DÀI (Theo {h1}): {guess_full(guess)}", guess, 95, get_color(guess)

    # --- 2. ƯU TIÊN NHÌ: CẦU 2-2 (Song Song) ---
    # Logic: Nếu trước đó có cặp (h3=h4) và giờ lại có cặp (h1=h2) -> Khả năng cao là cầu 2-2
    # Ví dụ: BB PP -> Đánh B
    if h4 and h1 == h2 and h3 == h4 and h2 != h3:
        guess = 'P' if h1 == 'B' else 'B' # Bẻ cầu (Không nuôi 3)
        return f"💎 CẦU 2-2 (Bẻ {h1}): {guess_full(guess)}", guess, 90, get_color(guess)

    # --- 3. ƯU TIÊN BA: CẦU 1-2 (Lệch) ---
    # Logic: B P P -> Đánh B (Về lại 1)
    # Điều kiện: h1=h2 (là 2 cây P) và h3 khác h2 (là cây B)
    if h1 == h2 and h2 != h3:
        # Kiểm tra xem có phải cầu 2-2 không? Nếu h4 cũng khác h3 thì có thể là 2-2.
        # Ở đây ta ưu tiên bắt 1-2 nếu không khớp 2-2 ở trên
        guess = h3
        return f"📉 CẦU 1-2 (Về {guess_full(guess)}): {guess}", guess, 85, get_color(guess)

    # --- 4. ƯU TIÊN BỐN: SĂN CẦU 3-1 (Của anh) ---
    # Nếu thấy 3 cây (mà chưa ra 4) -> Bẻ
    if h3 and h1 == h2 and h2 == h3:
        guess = 'P' if h1 == 'B' else 'B'
        return f"🔪 SĂN 3-1 (Bẻ {h1}): {guess_full(guess)}", guess, 92, get_color(guess)

    # --- 5. ƯU TIÊN NĂM: NUÔI CẦU 3 (Của anh) ---
    # Chỉ nuôi khi KHÔNG PHẢI cầu 2-2 và KHÔNG PHẢI cầu 1-2
    # Ở các bước trên đã lọc rồi, nên nếu lọt xuống đây thì cứ nuôi
    if h1 == h2:
        guess = h1
        return f"🌱 NUÔI CẦU 3 (Theo {h1}): {guess_full(guess)}", guess, 80, get_color(guess)

    # --- 6. CẦU 1-1 ---
    if h1 != h2:
        # Bắt 1-1
        guess = 'P' if h1 == 'B' else 'B'
        return f"🏓 CẦU 1-1: {guess_full(guess)}", guess, 75, get_color(guess)

    return "👀 Đang phân tích...", "SKIP", 0, "#444"

def guess_full(code): return "BANKER" if code == 'B' else "PLAYER"
def get_color(code): return "#C0392B" if code == 'B' else "#2980B9"

# --- XỬ LÝ ---
def process(result):
    _, pred, _, _ = analyze_v10(st.session_state.history)
    if pred not in ["SKIP", "WAIT"] and result != 'T':
        if pred == result:
            st.session_state.wins += 1
            st.toast("WIN! Chuẩn quá!", icon="✅")
        else:
            st.session_state.losses += 1
            st.toast("Gãy! Gấp thếp...", icon="⚠️")
    st.session_state.history.append(result)

# --- GIAO DIỆN ---
st.title("👑 VTSC ALL-IN-ONE v10.0")
st.caption("Tổng hợp: Săn 3-1 | Bắt 2-2 | Bắt 1-2 | Bám Bệt")

msg, pred, conf, col = analyze_v10(st.session_state.history)

st.markdown(f"""
<div class="card" style="border-color: {col}; box-shadow: 0 0 30px {col}40;">
    <h3 style="color:#aaa; margin:0;">AI DỰ ĐOÁN</h3>
    <h1 style="color:{col}; font-size:45px; margin:10px 0;">{msg.split(':')[0]}</h1>
    <h2 style="color:white; font-size:45px; margin:0;">{msg.split(':')[-1] if ':' in msg else ''}</h2>
    <div style="background:#333; height:8px; width:100%; border-radius:4px; margin-top:10px;">
        <div style="width:{conf}%; background:{col}; height:100%; border-radius:4px;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: 
    if st.button("🔵 PLAYER"): process('P'); st.rerun()
with c2: 
    if st.button("🔴 BANKER"): process('B'); st.rerun()
with c3: 
    if st.button("🟢 TIE"): process('T'); st.rerun()

st.markdown("---")
col1, col2 = st.columns([1, 2])
with col1:
    w, l = st.session_state.wins, st.session_state.losses
    st.markdown(f"<div style='background:#222; padding:10px; border-radius:10px; text-align:center;'><span style='color:#2ecc71; font-size:28px;'>{w} WIN</span> | <span style='color:#e74c3c; font-size:28px;'>{l} LOSS</span></div>", unsafe_allow_html=True)
    if st.button("🗑️ Xóa Bàn"): st.session_state.history = []; st.session_state.wins=0; st.session_state.losses=0; st.rerun()

with col2:
    if st.session_state.history:
        h_code = '<div style="display:flex; gap:5px; flex-wrap:wrap; background:#222; padding:15px; border-radius:10px;">'
        for item in st.session_state.history:
            if item == 'P': c="#2980B9"; t="P"
            elif item == 'B': c="#C0392B"; t="B"
            else: c="#27AE60"; t="T"
            h_code += f'<div style="width:30px;height:30px;background:{c};border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;">{t}</div>'
        h_code += '</div>'
        st.markdown(h_code, unsafe_allow_html=True)