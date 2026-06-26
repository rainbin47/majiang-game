import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import base64
import requests

# ====================== 配置区 ======================
GITHUB_REPO = "rainbin47/majiang-game"  
DB_FILE = "麻坛所有比赛数据.xlsx"
GITHUB_TOKEN = "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"

# ====================== 🀄 核心牌型番数字典 ======================
HU_CARDS_DICT = {
    "50 番 顶级天骄牌型": {"大四喜": 50, "大三元": 50, "孔雀东南飞": 50, "西北下大雪": 50, "天胡": 50, "地胡": 50, "四暗刻": 50, "连七对": 50, "十三幺": 50, "清老头": 50, "绿一色": 50, "字一色": 50},
    "30 番 惊世豪强牌型": {"小四喜": 30, "小三元": 30, "孔雀东南飞（小）": 30, "西北下大雪（小）": 30, "大七对": 30,"混老头": 30},
    "20 番 纵横捭阖牌型": {"清一色": 20, "清带幺": 20, "一色四步高": 20, "一色四同顺": 20, "一色四节高": 20, "三杠子": 20, "四连刻": 20, "七小对": 20, "全将碰": 20},
    "10 番 名震四海牌型": {"五门齐": 10, "一色清龙": 10, "一色步步高高": 10, "一色节节高": 10, "两头蛇": 10, "十三不靠": 10, "混一色": 10, "混带幺": 10, "海底捞月": 10, "杠上开花": 10, "杠上炮": 10, "抢杠": 10, "全中": 10, "全大": 10, "全小": 10, "无番胡": 10, "碰碰胡": 10, "三连刻": 10, "三色三同刻": 10, "全求人": 10, "三姊妹": 10},
    "5 番 略展身手牌型": {"门清自摸": 5, "小于五": 5, "大于五": 5, "三色花龙": 5, "三色三同顺": 5, "三色三节高": 5},
    "4 番 新晋高手牌型": {"一摸四": 4},
    "3 番 势如破竹牌型": {"一模三": 3},
    "2 番 积少成多牌型": {"自摸": 2, "断幺九": 2, "幺九刻": 2, "暗杠": 2,"板板": 2, "独听边张（卡窿）": 2},
    "1 番 风起青萍牌型": {"门前清": 1, "缺字": 1, "缺一门": 1, "平胡": 1, "明杠": 1, "姊妹花": 1, "连六": 1, "独听": 1, "独幺": 1,"圈风刻": 1, "门风刻": 1,"三元刻": 1,  "258将": 1}
}

# ====================== 🔄 GitHub 同步底层 ======================
def load_github_db():
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            with open(DB_FILE, "wb") as f: f.write(res.content)
    except: pass
    if not os.path.exists(DB_FILE):
        with pd.ExcelWriter(DB_FILE) as writer:
            pd.DataFrame(columns=["比赛名称", "比赛日期", "第1名", "第1名名次分", "第2名", "第2名名次分", "第3名", "第3名名次分", "第4名", "第4名名次分"]).to_excel(writer, sheet_name="比赛汇总", index=False)
    return pd.read_excel(DB_FILE, sheet_name=None)

def save_github_db():
    if not os.path.exists(DB_FILE): return False
    try:
        with open(DB_FILE, "rb") as f: content = base64.b64encode(f.read()).decode()
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DB_FILE}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        res = requests.get(url, headers=headers, timeout=5)
        sha = res.json()["sha"] if res.status_code == 200 else None
        payload = {"message": f"💻 自动同步 {datetime.now().strftime('%Y-%m-%d %H:%M')}", "content": content}
        if sha: payload["sha"] = sha
        res = requests.put(url, headers=headers, json=payload, timeout=5)
        return res.status_code in [200, 201]
    except: return False

# 强效数字转换安全阀
def safe_int(value):
    try:
        if pd.isna(value) or value is None: return 0
        return int(float(value))
    except: return 0

# ====================== 👑 全局 UI 样式注入 ======================
st.set_page_config(page_title="雀神风云录 · 尊享席位版", page_icon="🀄", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
/* 全局大底框背景 */
.stApp { background: linear-gradient(135deg, #f9f8f6 0%, #f1efe9 50%, #e6e3da 100%) !important; }
.big-title { background: linear-gradient(135deg, #7c1a1a 0%, #b91c1c 50%, #d97706 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-size: 2.8rem; font-weight: 900; padding: 15px 0 0px 0; }
.sub-title { text-align: center; color: #78350f; font-size: 1rem; letter-spacing: 4px; margin-bottom: 25px; opacity: 0.8; }

/* 
 🎯 左侧控制中心：右侧同色系（红黄）的【略深/略暗】版本 
*/
[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #3b0712 0%, #1c0207 100%) !important; 
    border-right: 2px solid #a1782f !important; 
}
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4, 
[data-testid="stSidebar"] h5, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio div { 
    color: #cda250 !important; 
    font-weight: 700 !important; 
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #cda250 !important;
}
[data-testid="stSidebar"] .stAlert p { color: #ffffff !important; }

/* ---------------- 右侧：实时数据大盘样式升级 ---------------- */
/* 已移除原来的白色内衬和红色圆角外边框，让背景自然过渡 */
.static-header-row { display: flex; justify-content: space-around; align-items: center; background: linear-gradient(90deg, #7c1a1a 0%, #b91c1c 100%); padding: 15px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.static-header-item { text-align: center; color: #ffffff; min-width: 120px; }
.static-h-name { font-weight: 800; font-size: 1.1rem; color: #fde68a; }

/* 🎯 关键修改点：得分字体调大至 2.8rem，与主标题完全一样大 */
.static-h-score { font-weight: 900; font-size: 2.8rem; font-family: 'Impact', monospace; margin: 2px 0; color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.4); }
.static-h-sub { font-size: 0.85rem; color: #fca5a5; line-height: 1.3; }

.pane-title { font-size: 1.15rem !important; font-weight: 800 !important; color: #7c1a1a !important; margin-top: 20px !important; margin-bottom: 12px !important; border-left: 4px solid #b91c1c; padding-left: 8px; }
.custom-card { background: rgba(255, 255, 255, 0.85) !important; border-radius: 15px !important; padding: 15px !important; border: 1px solid rgba(217, 119, 6, 0.15) !important; }
h2, h3 { color: #451a03 !important; font-weight: 800 !important; border-left: 5px solid #b91c1c !important; padding-left: 12px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🀄 雀神风云录</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">— 亚洲麻协对局大盘实时大数据积分系统 —</div>', unsafe_allow_html=True)

MAX_ROUNDS = 99
POSITION_ORDER = ["东风", "南风", "西风", "北风"]
WIND_CIRCLES = ["东风圈", "南风圈", "西风圈", "北风圈"]
PLAYER_LIST = ["奶猫", "农少", "老王", "老野", "老蒋", "老潘", "阿狗", "孙军"]
DEALER_LEVELS = ["第一庄（2倍）", "第二庄（4倍）", "第三庄及以上（8倍）"]
DEALER_MULTI_DICT = {"第一庄（2倍）": 2, "第二庄（4倍）": 4, "第三庄及以上（8倍）": 8}
HU_TYPES = ["自摸", "放炮", "流局"]

# ====================== 🚀 状态初始化 ======================
if "current_match" not in st.session_state: st.session_state.current_match = []
if "match_name" not in st.session_state: st.session_state.match_name = f"比赛_{datetime.now().strftime('%Y%m%d')}"
if "circle_idx" not in st.session_state: st.session_state.circle_idx = 0       
if "down_dealer_count" not in st.session_state: st.session_state.down_dealer_count = 0  
if "dealer_pos_idx" not in st.session_state: st.session_state.dealer_pos_idx = 0
if "dealer_level_idx" not in st.session_state: st.session_state.dealer_level_idx = 0
if "seating" not in st.session_state: st.session_state.seating = {"东风": PLAYER_LIST[0], "南风": PLAYER_LIST[1], "西风": PLAYER_LIST[2], "北风": PLAYER_LIST[3]}
if "initial_seating" not in st.session_state: st.session_state.initial_seating = {"东风": PLAYER_LIST[0], "南风": PLAYER_LIST[1], "西风": PLAYER_LIST[2], "北风": PLAYER_LIST[3]}
if "show_re_seat_ui" not in st.session_state: st.session_state.show_re_seat_ui = False
if "current_dealer_name" not in st.session_state: st.session_state.current_dealer_name = st.session_state.seating["东风"]

with st.sidebar:
    st.markdown("<h2 style='color:#cda250!important;border-left:5px solid #a1782f!important;'>🧭 控制中心</h2>", unsafe_allow_html=True)
    mode = st.radio("请选择视窗模式", ["🎯 新比赛录入", "📜 历史比赛查询", "📈 选手数据看板"])

# ---------------------- 🎯 新比赛录入 ----------------------
if mode == "🎯 新比赛录入":
    df = pd.DataFrame(st.session_state.current_match)
    round_num = len(st.session_state.current_match) + 1
    auto_round_end = st.session_state.circle_idx >= 4

    with st.sidebar:
        st.markdown("<hr style='border-color:rgba(161,120,47,0.3)'/>", unsafe_allow_html=True)
        st.subheader("📝 实时对局登记")
        st.session_state.match_name = st.text_input("比赛名称", value=st.session_state.match_name)
        match_date = st.date_input("选择比赛日期", value=datetime.now())
        
        current_circle_name = WIND_CIRCLES[min(st.session_state.circle_idx, 3)] if st.session_state.circle_idx < 4 else "本轮已结束"
        rec_dealer_pos = POSITION_ORDER[st.session_state.dealer_pos_idx]
        rec_dealer_name = st.session_state.seating[rec_dealer_pos]
        dealer_lvl_str = DEALER_LEVELS[st.session_state.dealer_level_idx].split("（")[0]
        
        st.info(f"📋 进度：**{current_circle_name}-{rec_dealer_name}坐{dealer_lvl_str}中**。")
        st.info(f"🎯 当前局数：第 {round_num} 局")
        
        if round_num == 1 and len(df) == 0:
            st.markdown("##### 🪑 开局初始席位")
            new_e = st.selectbox("【东风】选手", PLAYER_LIST, index=PLAYER_LIST.index(st.session_state.seating["东风"]))
            new_s = st.selectbox("【南风】选手", PLAYER_LIST, index=PLAYER_LIST.index(st.session_state.seating["南风"]))
            new_w = st.selectbox("【西风】选手", PLAYER_LIST, index=PLAYER_LIST.index(st.session_state.seating["西风"]))
            new_n = st.selectbox("【北风】选手", PLAYER_LIST, index=PLAYER_LIST.index(st.session_state.seating["北风"]))
            if len({new_e, new_s, new_w, new_n}) == 4:
                st.session_state.seating = {"东风": new_e, "南风": new_s, "西风": new_w, "北风": new_n}
                st.session_state.initial_seating = {"东风": new_e, "南风": new_s, "西风": new_w, "北风": new_n}
                st.session_state.current_dealer_name = new_e
        
        pos_to_player = st.session_state.seating
        player_to_pos = {v:k for k,v in pos_to_player.items()}
        player_names = list(pos_to_player.values())
        player_to_init_pos = {v:k for k,v in st.session_state.initial_seating.items()}
        
        current_dealer_player = st.selectbox("当前局庄家", player_names, index=player_names.index(st.session_state.current_dealer_name))
        st.session_state.current_dealer_name = current_dealer_player
        current_dealer_pos = player_to_pos[current_dealer_player]
        
        dealer_level = st.selectbox("庄家连庄状态", DEALER_LEVELS, index=st.session_state.dealer_level_idx)
        dealer_multi = DEALER_MULTI_DICT[dealer_level]
        
        hu_type = st.selectbox("本局结果判定", HU_TYPES, key="input_hu_type")
        fan = 0; hu_player = ""; pao_player = ""; selected_patterns_str = "/"
        
        if hu_type != "流局":
            hu_player = st.selectbox("胡牌获胜选手", player_names, index=0, key="input_hu_player")
            hu_pos = player_to_pos[hu_player]
            if hu_type == "放炮":
                pao_candidates = [p for p in player_names if p != hu_player]
                pao_player = st.selectbox("点炮选手", pao_candidates, index=0, key="input_pao_player")
                pao_pos = player_to_pos[pao_player]

    db = load_github_db()
    
    stats_map = {name: {"score": 0, "hu": 0, "zimo": 0, "fangpao": 0} for name in player_names}
    
    if len(df) > 0:
        for _, row in df.iterrows():
            for col in df.columns:
                for name in player_names:
                    if col.startswith(name) and col in row:
                        stats_map[name]["score"] += safe_int(row[col])
                        
            h_p = row.get("胡牌选手", "")
            f_p = row.get("放炮选手", "")
            res_t = row.get("本局结果", "")
            
            if res_t != "流局":
                if h_p in stats_map:
                    if res_t == "自摸": stats_map[h_p]["zimo"] += 1   
                    elif res_t == "放炮": stats_map[h_p]["hu"] += 1     
                if res_t == "放炮" and f_p in stats_map: 
                    stats_map[f_p]["fangpao"] += 1

    main_layout_left, main_layout_right = st.columns([11, 13])
    
    # -------------------- 右侧：常驻不位移数据大盘 --------------------
    with main_layout_right:
        # 👑 选手实时得分头部大盘 (红框组件已剥离)
        header_html = '<div class="static-header-row">'
        for name in player_names:
            p_data = stats_map[name]
            sign = '+' if p_data['score'] > 0 else ''
            header_html += f'<div class="static-header-item"><div class="static-h-name">👑 {name}</div><div class="static-h-score">{sign}{p_data["score"]}</div><div class="static-h-sub">接炮:{p_data["hu"]}<br/>自摸:{p_data["zimo"]}<br/>点炮:{p_data["fangpao"]}</div></div>'
        header_html += '</div>'
        st.markdown(header_html, unsafe_allow_html=True)
        
        st.markdown('<div class="pane-title">📋 实时对局流水明细</div>', unsafe_allow_html=True)
        if len(df) > 0:
            init_cols = [f"{st.session_state.initial_seating[p]}({p[0]})" for p in POSITION_ORDER]
            display_cols = ["局号", "当前圈", "庄家", "连庄次数", "本局结果", "胡牌牌型", "胡牌选手", "放炮选手", "番数"] + init_cols
            valid_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[valid_cols], width="stretch", hide_index=True, height=290)
        else:
            st.caption("💡 暂无对局流水数据。")
            
        st.markdown('<div class="pane-title">📈 历史积分演变波段</div>', unsafe_allow_html=True)
        if len(df) > 0:
            trend_records = []
            player_cum = {n: 0 for n in player_names}
            for idx, row in df.iterrows():
                for col in df.columns:
                    for name in player_names:
                        if col.startswith(name) and col in row:
                            player_cum[name] += safe_int(row[col])
                for n in player_names:
                    trend_records.append({"局号": idx + 1, "选手": n, "累计积分": player_cum[n]})
            
            if trend_records:
                trend_df = pd.DataFrame(trend_records)
                fig = px.line(trend_df, x="局号", y="累计积分", color="选手", markers=True)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=5, r=5, t=5, b=5), height=260)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        else:
            st.caption("📊 暂无演变走势波动图。")

    # -------------------- 左侧：主体操作表单 --------------------
    with main_layout_left:
        if auto_round_end or st.session_state.show_re_seat_ui:
            st.markdown("<div class='custom-card' style='background: rgba(217, 119, 6, 0.08) !important; border: 2px solid #d97706 !important;'><h4>🔄 🏁 触发【重新摸位】仪式</h4></div>", unsafe_allow_html=True)
            st.session_state.show_re_seat_ui = True
            rc1, rc2, rc3, rc4 = st.columns(4)
            new_east = rc1.selectbox("新【东风】", PLAYER_LIST, index=PLAYER_LIST.index(st.session_state.seating["东风"]), key="new_s_east")
            new_south = rc2.selectbox("新【南风】", PLAYER_LIST, index=PLAYER_LIST.index(st.session_state.seating["南风"]), key="new_s_south")
            new_west = rc3.selectbox("新【西风】", PLAYER_LIST, index=PLAYER_LIST.index(st.session_state.seating["西风"]), key="new_s_west")
            new_north = rc4.selectbox("新【北风】", PLAYER_LIST, index=PLAYER_LIST.index(st.session_state.seating["北风"]), key="new_s_north")
            
            if len({new_east, new_south, new_west, new_north}) == 4:
                if st.button("🔥 注入全新摸位座次", type="secondary"):
                    st.session_state.seating = {"东风": new_east, "南风": new_south, "西风": new_west, "北风": new_north}
                    st.session_state.circle_idx, st.session_state.down_dealer_count, st.session_state.dealer_pos_idx, st.session_state.dealer_level_idx = 0, 0, 0, 0
                    st.session_state.current_dealer_name = new_east
                    st.session_state.show_re_seat_ui = False
                    st.rerun()

        if hu_type != "流局":
            st.markdown("### 🀄 牌型选择矩阵")
            checked_patterns = []
            for title, cards in reversed(list(HU_CARDS_DICT.items())):
                is_expanded = any(k in title for k in ["1 番", "2 番", "3 番"])
                with st.expander(f"✨ {title}", expanded=is_expanded):
                    cols_matrix = st.columns(3)
                    for idx, (name, score) in enumerate(cards.items()):
                        with cols_matrix[idx % 3]:
                            if st.checkbox(f"{name} ({score}番)", key=f"chk_{round_num}_{title}_{name}"):
                                checked_patterns.append((name, score))
            if checked_patterns:
                fan = sum([item[1] for item in checked_patterns])
                selected_patterns_str = " + ".join([item[0] for item in checked_patterns])
                st.markdown(f"<div class='custom-card'>🔮 已选牌型：<b>{selected_patterns_str}</b><br/>💰 总计：<b>{fan} 番</b></div>", unsafe_allow_html=True)
            else:
                fan, selected_patterns_str = 0, "普通胡"

        with st.sidebar:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 提交本局", type="primary", width="stretch"):
                    scores = {"东风": 0, "南风": 0, "西风": 0, "北风": 0}
                    dealer_hu = (hu_type != "流局" and hu_pos == current_dealer_pos)
                    if hu_type != "流局" and fan >= 0:
                        other_pos = [p for p in POSITION_ORDER if p != hu_pos]
                        if hu_type == "自摸":
                            for p in other_pos:
                                base = fan * 2
                                if dealer_hu or (p == current_dealer_pos): base *= dealer_multi
                                scores[p] = -base
                                scores[hu_pos] += base
                        else:
                            for p in other_pos:
                                base = fan * 2 if p == pao_pos else fan
                                if dealer_hu or (p == current_dealer_pos): base *= dealer_multi
                                scores[p] = -base
                                scores[hu_pos] += base
                    
                    pao_display = pao_player if hu_type == "放炮" else "/" if hu_type == "自摸" else ""
                    
                    round_data = {
                        "局号": round_num, 
                        "当前圈": WIND_CIRCLES[min(st.session_state.circle_idx, 3)],
                        "庄家": current_dealer_player, 
                        "连庄次数": dealer_level, 
                        "庄倍数": dealer_multi,
                        "本局结果": hu_type, 
                        "胡牌牌型": selected_patterns_str, 
                        "胡牌选手": hu_player if hu_type != "流局" else "/", 
                        "放炮选手": pao_display, 
                        "番数": fan
                    }
                    
                    for pos in POSITION_ORDER:
                        current_seat_player = pos_to_player[pos]
                        seat_score = scores[pos]
                        initial_pos = player_to_init_pos[current_seat_player]
                        record_col_name = f"{current_seat_player}({initial_pos[0]})"
                        round_data[record_col_name] = seat_score
                        
                    st.session_state.current_match.append(round_data)
                    
                    current_dealer_pos_idx = POSITION_ORDER.index(current_dealer_pos)
                    if hu_type == "流局" or dealer_hu:
                        st.session_state.dealer_level_idx = min(st.session_state.dealer_level_idx + 1, len(DEALER_LEVELS) - 1)
                    else:
                        st.session_state.dealer_level_idx = 0
                        st.session_state.dealer_pos_idx = (current_dealer_pos_idx + 1) % 4
                        st.session_state.down_dealer_count += 1
                        if st.session_state.down_dealer_count >= 4:
                            st.session_state.circle_idx += 1
                            st.session_state.down_dealer_count = 0
                    
                    st.session_state.current_dealer_name = st.session_state.seating[POSITION_ORDER[st.session_state.dealer_pos_idx]]
                    st.rerun()
            
            with col2:
                if st.button("↩️ 撤销上局", width="stretch") and len(st.session_state.current_match) > 0:
                    st.session_state.current_match.pop()
                    st.rerun()
            
            st.divider()
            if st.button("🔄 手动触发重新摸位", width="stretch"):
                st.session_state.show_re_seat_ui = True
                st.rerun()
                
            if st.button("☁️ 将整场封盘保存至云端", width="stretch"):
                if len(st.session_state.current_match) > 0:
                    old_summary = db["比赛汇总"]
                    
                    all_player_scores = {n: 0 for n in player_names}
                    for _, r in df.iterrows():
                        for col in df.columns:
                            for name in player_names:
                                if col.startswith(name) and col in r:
                                    all_player_scores[name] += safe_int(r[col])
                                
                    rank_result = sorted(all_player_scores.items(), key=lambda x: x[1], reverse=True)
                    while len(rank_result) < 4: rank_result.append(("未参赛", 0))
                    
                    summary_row = pd.DataFrame([{"比赛名称": st.session_state.match_name, "比赛日期": match_date.strftime("%Y-%m-%d"), "第1名": rank_result[0][0], "第1名名次分": 5, "第2名": rank_result[1][0], "第2名名次分": 3, "第3名": rank_result[2][0], "第3名名次分": 2, "第4名": rank_result[3][0], "第4名名次分": 1}])
                    new_summary = pd.concat([old_summary, summary_row], ignore_index=True)
                    new_sheet = f"明细_{match_date.strftime('%Y%m%d')}_{st.session_state.match_name}"[:30]
                    
                    with pd.ExcelWriter(DB_FILE) as writer:
                        new_summary.to_excel(writer, sheet_name="比赛汇总", index=False)
                        df.to_excel(writer, sheet_name=new_sheet, index=False)
                        for sn, sdf in db.items():
                            if sn not in ["比赛汇总", new_sheet]: sdf.to_excel(writer, sheet_name=sn, index=False)
                    if save_github_db():
                        st.session_state.current_match = []
                        st.rerun()

# ---------------------- 📜 历史查询 ----------------------
elif mode == "📜 历史比赛查询":
    st.header("📜 历史对局封存卷轴")
    db = load_github_db()
    summary_df = db["比赛汇总"]
    if len(summary_df) > 0:
        match_options = [f"📅 {row['比赛日期']} — 🏆 {row['比赛名称']}" for _, row in summary_df.iterrows()]
        selected_match = st.selectbox("请挑选复盘场次", match_options)
        sel_row = summary_df.iloc[match_options.index(selected_match)]
        target_sheet = f"明细_{sel_row['比赛日期'].replace('-', '')}_{sel_row['比赛名称']}"[:30]
        if target_sheet in db:
            st.dataframe(db[target_sheet], width="stretch")

# ---------------------- 📈 选手数据大看板 (全新重构升级) ----------------------
else:
    st.header("📈 8人选手大数据综合风云榜")
    db = load_github_db()
    summary_df = db["比赛汇总"].copy()
    
    # 确保时间类型正确
    summary_df["比赛日期"] = pd.to_datetime(summary_df["比赛日期"])
    
    # 维度选择器
    period_mode = st.radio("请选择统计与曲线聚合维度", ["所有比赛", "年度", "季度", "月度"], horizontal=True)
    
    # 数据清洗：将宽表打散成单条选手的名次分记录，方便进行聚合与图表绘制
    records = []
    for _, row in summary_df.iterrows():
        date_val = row["比赛日期"]
        # 解析各个时间标签
        year_str = f"{date_val.year}年"
        quarter_str = f"{date_val.year}年Q{(date_val.month-1)//3 + 1}"
        month_str = f"{date_val.strftime('%Y-%m')}月"
        
        # 提取1-4名的数据
        for i in range(1, 5):
            p_name = row[f"第{i}名"]
            p_score = safe_int(row[f"第{i}名名次分"])
            if p_name in PLAYER_LIST:
                records.append({
                    "比赛日期": date_val,
                    "年度": year_str,
                    "季度": quarter_str,
                    "月度": month_str,
                    "选手": p_name,
                    "名次分": p_score
                })
                
    if records:
        analysis_df = pd.DataFrame(records)
        
        # 根据选择的维度决定分组字段
        group_col = "比赛日期" if period_mode == "所有比赛" else period_mode
        
        # 1. 聚合计算各时间段内 8 个选手的总积分
        pivot_table = analysis_df.groupby([group_col, "选手"])["名次分"].sum().reset_index()
        
        # 2. 计算累计积分用于趋势曲线图
        pivot_table = pivot_table.sort_values(by=group_col)
        pivot_table["累计名次分"] = pivot_table.groupby("选手")["名次分"].cumsum()
        
        # 确保全部 8 人即使某阶段没打也有数据，生成完整的矩阵
        all_periods = sorted(pivot_table[group_col].unique())
        full_index = pd.MultiIndex.from_product([all_periods, PLAYER_LIST], names=[group_col, "选手"])
        chart_data = pivot_table.set_index([group_col, "选手"]).reindex(full_index).reset_index()
        
        # 对缺失值进行前向填充（继承上期积分）并补0
        chart_data["累计名次分"] = chart_data.groupby("选手")["累计名次分"].ffill().fillna(0)
        chart_data["名次分"] = chart_data["名次分"].fillna(0)
        
        # 绘制 Plotly 8 人全员风云走势图
        st.markdown(f"### 📊 8大选手 — {period_mode}累计积分演变曲线")
        
        # 如果是“所有比赛”，横轴采用真实时间轴更平滑
        x_axis = group_col
        if period_mode == "所有比赛":
            chart_data = chart_data.sort_values(by="比赛日期")
            
        fig_all = px.line(
            chart_data, 
            x=x_axis, 
            y="累计名次分", 
            color="选手", 
            markers=True,
            category_orders={group_col: all_periods},
            labels={"累计名次分": "总囤积名次分", group_col: period_mode}
        )
        fig_all.update_layout(
            hovermode="x unified",
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=450
        )
        st.plotly_chart(fig_all, use_container_width=True)
        
        # 3. 展现段落总分榜
        st.markdown(f"### 🏆 {period_mode}阶段总分统计表")
        display_pivot = analysis_df.groupby("选手")["名次分"].sum().reset_index()
        # 补齐未上场的选手
        for p in PLAYER_LIST:
            if p not in display_pivot["选手"].values:
                display_pivot = pd.concat([display_pivot, pd.DataFrame([{"选手": p, "名次分": 0}])], ignore_index=True)
        display_pivot = display_pivot.sort_values(by="名次分", ascending=False).reset_index(drop=True)
        st.table(display_pivot)
        
    else:
        st.caption("💡 暂无汇总名次数据，无法生成曲线图。")
        
    st.markdown("### 📋 原始历史保存总卷轴")
    st.dataframe(db["比赛汇总"].sort_values(by="比赛日期", ascending=False), width="stretch", hide_index=True)