import streamlit as st

# --- CẤU HÌNH APP (v12.0 - TAM LỘ SOI CẦU) ---
st.set_page_config(
    page_title="VTSC AI v12.0 - Soi Cầu Phụ",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS CAO CẤP (Giao diện Chuyên Nghiệp) ---
st.markdown("""
<style>
    .stApp { background-color: #0e0e0e; color: #dcdcdc; }
    
    /* Nút bấm */
    div.stButton > button {
        width: 100%; height: 80px; font-weight: 900; font-size: 24px !important;
        border-radius: 12px; color: white !important;
        border: 1px solid #333; box-shadow: 0 4px 0 #000;
        transition: transform 0.1s;
    }
    div.stButton > button:active { transform: translateY(3px); box-shadow: none; }

    /* Màu chuẩn */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { background: #0984e3 !important; border-bottom: 4px solid #06528f !important; }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { background: #d63031 !important; border-bottom: 4px solid #911d1d !important; }
    div[data-testid="column"]:nth-of-type(3) div.stButton > button { background: #00b894 !important; border-bottom: 4px solid #007961 !important; }

    .card { background: #1e1e1e; border: 1px solid #444; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(255,255,255,0.05); }
    .ask-box { display: flex; justify-content: space-around; margin-top: 10px; }
    .road-dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin: 2px; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'wins' not in st.session_state: st.session_state.wins = 0
if 'losses' not in st.session_state: st.session_state.losses = 0

# --- THUẬT TOÁN XÂY DỰNG BIG ROAD (CẦU CHÍNH) ---
def build_big_road(history):
    clean = [x for x in history if x != 'T']
    if not clean: return []
    
    big_road = []
    current_col = [clean[0]]
    
    for i in range(1, len(clean)):
        if clean[i] == clean[i-1]:
            current_col.append(clean[i])
        else:
            big_road.append(current_col)
            current_col = [clean[i]]
    big_road.append(current_col)
    return big_road

# --- THUẬT TOÁN CẦU PHỤ (DERIVED ROADS) ---
# Quy tắc: So sánh độ dài cột hoặc màu bead để xác định Đỏ/Xanh cho cầu phụ
def get_derived_signal(big_road, simulate_result):
    # Giả lập thêm kết quả mới vào Big Road
    temp_road = [col[:] for col in big_road] # Copy deep
    if not temp_road:
        temp_road = [[simulate_result]]
    else:
        last_col = temp_road[-1]
        if last_col[-1] == simulate_result:
            last_col.append(simulate_result)
        else:
            temp_road.append([simulate_result])
            
    # Tính toán tín hiệu cho Đại Lộ (Offset=1), Tiểu Lộ (Offset=2), Gián Lộ (Offset=3)
    # Ở đây dùng thuật toán đơn giản hóa: "Tính ổn định" (Symmetry)
    # Nếu cột mới tạo ra có độ dài BẰNG cột trước nó -> Tốt (Đỏ)
    # Nếu cột mới tạo ra phá vỡ thế bệt -> Xấu (Xanh)
    
    score = 0
    
    # 1. Soi Đại Lộ (Big Eye) - So cột hiện tại với cột trước
    if len(temp_road) >= 2:
        curr_len = len(temp_road[-1])
        prev_len = len(temp_road[-2])
        if curr_len == prev_len: score += 1 # Cầu đối xứng (Đẹp)
        if curr_len == 1 and prev_len > 2: score -= 0.5 # Gãy đột ngột (Xấu)
        
    # 2. Soi Tiểu Lộ (Small Road) - So cột hiện tại với cột cách 2
    if len(temp_road) >= 3:
        curr_len = len(temp_road[-1])
        prev2_len = len(temp_road[-3])
        if curr_len == prev2_len: score += 1
        
    return score

# --- PHÂN TÍCH TỔNG HỢP (v12.0) ---
def analyze_v12(history):
    clean = [x for x in history if x != 'T']
    if len(clean) < 4:
        return "⏳ Đang nạp dữ liệu...", "WAIT", 0, "#444"

    # 1. Logic Cầu Chính (v10 - Nền tảng)
    h1 = clean[-1]
    h2 = clean[-2]
    h3 = clean[-3] if len(clean) >= 3 else None
    h4 = clean[-4] if len(clean) >= 4 else None
    
    main_pred = None
    if h4 and h1 == h2 and h2 == h3 and h3 == h4: main_pred = h1 # Bệt
    elif h3 and h1 == h2 and h2 == h3: main_pred = 'P' if h1 == 'B' else 'B' # Bẻ 3
    elif h4 and h1 == h2 and h3 == h4 and h2 != h3: main_pred = 'P' if h1 == 'B' else 'B' # Bẻ 2-2
    elif h1 != h2: main_pred = 'P' if h1 == 'B' else 'B' # Cầu 1-1
    
    # 2. Logic Cầu Phụ (Giả lập B/P Ask)
    big_road = build_big_road(clean)
    
    score_if_P = get_derived_signal(big_road, 'P')
    score_if_B = get_derived_signal(big_road, 'B')
    
    # 3. Tổng hợp (Consensus)
    final_pick = None
    reason = ""
    conf = 0
    
    # Nếu Cầu Phụ ủng hộ bên nào rõ rệt -> Theo bên đó
    if score_if_B > score_if_P:
        final_pick = 'B'; reason = "🔮 CẦU PHỤ BÁO ĐỎ (Banker đẹp)"; conf = 85
    elif score_if_P > score_if_B:
        final_pick = 'P'; reason = "🔮 CẦU PHỤ BÁO ĐỎ (Player đẹp)"; conf = 85
    else:
        # Nếu Cầu Phụ cân bằng -> Dùng Cầu Chính
        if main_pred:
            final_pick = main_pred
            reason = "🛡️ THEO CẦU CHÍNH (Cầu phụ hòa)"; conf = 75
        else:
            return "⚠️ Cầu Loạn - Tạm Dừng", "SKIP", 0, "#555"

    # Màu sắc
    col = "#d63031" if final_pick == 'B' else "#0984e3"
    
    return f"{reason}: {guess_full(final_pick)}", final_pick, conf, col

def guess_full(code): return "BANKER" if code == 'B' else "PLAYER"

# --- XỬ LÝ ---
def process(result):
    _, pred, _, _ = analyze_v12(st.session_state.history)
    if pred not in ["SKIP", "WAIT"] and result != 'T':
        if pred == result:
            st.session_state.wins += 1
            st.toast("HÚP! Cầu Phụ Quá Chuẩn!", icon="✅")
        else:
            st.session_state.losses += 1
            st.toast("Gãy! Đợi nhịp sau...", icon="🛑")
    st.session_state.history.append(result)

# --- GIAO DIỆN ---
st.title("🔮 VTSC v12.0 - SOI CẦU PHỤ")
st.caption("Công nghệ giả lập 'Hỏi Cái / Hỏi Con' (Ask Type)")

msg, pred, conf, col = analyze_v12(st.session_state.history)

# THẺ KẾT QUẢ
if pred in ["SKIP", "WAIT"]:
    st.markdown(f"<div class='card'><h2 style='color:#666'>{msg}</h2></div>", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="card" style="border-color: {col}; box-shadow: 0 0 30px {col}40;">
        <h3 style="color:#aaa; margin:0;">AI CHỐT LỆNH</h3>
        <h1 style="color:{col}; font-size:48px; margin:5px 0;">{msg.split(':')[1]}</h1>
        <p style="color:#ccc;">{msg.split(':')[0]}</p>
        <div style="background:#333; height:8px; width:100%; border-radius:4px; margin-top:10px;">
            <div style="width:{conf}%; background:{col}; height:100%; border-radius:4px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# LỜI KHUYÊN
if conf >= 85: advice = "💰 VÀO TIỀN MẠNH (Đồng thuận)"
elif conf >= 75: advice = "⚖️ VÀO ĐỀU TAY"
else: advice = "⛔ QUAN SÁT"
st.markdown(f"<div style='text-align:center; color:{col if conf>0 else '#666'}; font-weight:bold; margin-bottom:15px; font-size:18px;'>{advice}</div>", unsafe_allow_html=True)

# NÚT NHẬP
c1, c2, c3 = st.columns(3)
with c1: 
    if st.button("🔵 PLAYER"): process('P'); st.rerun()
with c2: 
    if st.button("🔴 BANKER"): process('B'); st.rerun()
with c3: 
    if st.button("🟢 TIE"): process('T'); st.rerun()

st.markdown("---")

# THỐNG KÊ
col_stat, col_road = st.columns([1, 2])
with col_stat:
    w, l = st.session_state.wins, st.session_state.losses
    st.markdown(f"<div style='background:#111; padding:15px; border-radius:10px; text-align:center; border:1px solid #333;'><span style='color:#00b894; font-size:28px;'>{w} WIN</span> | <span style='color:#d63031; font-size:28px;'>{l} LOSS</span></div>", unsafe_allow_html=True)
    if st.button("🗑️ Xóa Bàn"): st.session_state.history = []; st.session_state.wins=0; st.session_state.losses=0; st.rerun()

with col_road:
    if st.session_state.history:
        h_code = '<div style="display:flex; gap:4px; flex-wrap:wrap; background:#111; padding:10px; border-radius:10px;">'
        for item in st.session_state.history:
            if item == 'P': c="#0984e3"; t="P"
            elif item == 'B': c="#d63031"; t="B"
            else: c="#00b894"; t="T"
            h_code += f'<div style="width:28px;height:28px;background:{c};border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:12px;font-weight:bold;">{t}</div>'
        h_code += '</div>'
        st.markdown(h_code, unsafe_allow_html=True)