import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import os
import base64
import requests

# ====================== 配置区（改成你自己的） ======================
GITHUB_REPO = "rainbin47/majiang-game"  
GITHUB_TOKEN = st.secrets["github_token"]
DB_FILE = "麻坛所有比赛数据.xlsx"

# ====================== 修复后的GitHub读写函数 ======================
def load_github_db():
    """从GitHub下载最新的Excel"""
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{DB_FILE}"
    res = requests.get(url)
    with open(DB_FILE, "wb") as f:
        f.write(res.content)
    return pd.read_excel(DB_FILE, sheet_name=None)

def save_github_db():
    """保存到GitHub，加错误提示"""
    with open(DB_FILE, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        st.error(f"获取文件失败：{res.json()['message']}")
        return False
    sha = res.json()["sha"]
    
    res = requests.put(url, headers=headers, json={
        "message": f"更新比赛数据 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": content,
        "sha": sha
    })
    return res.status_code in [200, 201]

# ====================== 👑 奢华重构：全局UI美化与自适应注入 ======================
st.set_page_config(
    page_title="雀神风云录 · 云端奢华版",
    page_icon="🀄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* 全局典雅国风渐变背景 */
.stApp {
    background: linear-gradient(135deg, #f9f8f6 0%, #f1efe9 50%, #e6e3da 100%) !important;
    font-family: "SF Pro Display", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

/* 顶部奢华大标题 */
.big-title {
    background: linear-gradient(135deg, #7c1a1a 0%, #b91c1c 50%, #d97706 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: 2px;
    padding: 20px 0 10px 0;
    margin-bottom: 5px;
    filter: drop-shadow(0px 4px 10px rgba(185,28,28,0.15));
}
.sub-title {
    text-align: center;
    color: #78350f;
    font-size: 1rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 35px;
    opacity: 0.8;
}

/* 侧边栏奢华美化 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b18 0%, #2e2520 100%) !important;
    border-right: 1px solid rgba(217, 119, 6, 0.2);
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span {
    color: #f3f4f6 !important;
}
/* 侧边栏单选框高级感 */
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 10px 15px;
    margin-bottom: 8px;
    transition: all 0.3s;
    border: 1px solid transparent;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(217, 119, 6, 0.15);
    border: 1px solid rgba(217, 119, 6, 0.3);
}

/* 核心毛玻璃卡片（自适应） */
div[data-testid="metric-container"], .custom-card {
    background: rgba(255, 255, 255, 0.75) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 20px !important;
    padding: 24px 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.6) !important;
    box-shadow: 0 10px 30px rgba(46, 37, 32, 0.05) !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba(185, 28, 28, 0.12) !important;
    border: 1px solid rgba(217, 119, 6, 0.4) !important;
}

/* 高级按钮设计（包含流光质感） */
.stButton>button {
    background: linear-gradient(135deg, #991b1b 0%, #7f1d1d 100%) !important;
    color: #fef3c7 !important;
    border-radius: 14px !important;
    border: 1px solid #b45309 !important;
    font-weight: 600 !important;
    letter-spacing: 1px;
    padding: 12px 24px !important;
    box-shadow: 0 4px 15px rgba(153,27,27,0.25) !important;
    transition: all 0.3s ease !important;
    width: 100%;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%) !important;
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 8px 25px rgba(185,28,28,0.4) !important;
}

/* 次要/辅助按钮（如撤销、新建等） */
div[data-testid="stButton"] button[p-bgcolor="secondary"] {
    background: transparent !important;
    color: #7f1d1d !important;
    border: 1px solid #7f1d1d !important;
}

/* 数据表格高级化圆角隐藏溢出 */
.stDataFrame {
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.04) !important;
    background: white;
}

/* H2, H3 华丽缎带标题 */
h2, h3 {
    color: #451a03 !important;
    font-weight: 800 !important;
    border-left: 5px solid #b91c1c !important;
    padding-left: 14px !important;
    margin-top: 35px !important;
    margin-bottom: 22px !important;
    letter-spacing: 1px;
}

/* 针对手机端和PC端的自适应补充媒体查询 */
@media (max-width: 768px) {
    .big-title {
        font-size: 1.9rem !important;
        padding-top: 10px;
    }
    .sub-title {
        font-size: 0.8rem !important;
        letter-spacing: 2px !important;
        margin-bottom: 20px;
    }
    div[data-testid="metric-container"] {
        padding: 16px 12px !important;
        margin-bottom: 12px !important;
    }
    /* 手机端按钮加大防误触 */
    .stButton>button {
        padding: 14px 20px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# 渲染精美头部
st.markdown('<div class="big-title">🀄 雀神风云录</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">— 云端尊享数据大盘 —</div>', unsafe_allow_html=True)

# 业务通用静态变量配置
MAX_ROUNDS = 99
POSITION_ORDER = ["东风", "南风", "西风", "北风"]
PLAYER_LIST = ["奶猫", "农少", "老王", "老野", "老蒋", "老潘", "阿狗", "孙军"]
DEALER_LEVELS = {"第一庄（2倍）": 2, "第二庄（4倍）": 4, "第三庄及以上（8倍）": 8}
HU_TYPES = ["自摸", "放炮", "流局"]

if "current_match" not in st.session_state:
    st.session_state.current_match = []
if "match_name" not in st.session_state:
    st.session_state.match_name = f"比赛_{datetime.now().strftime('%Y%m%d')}"

# ---------------------- 侧边栏 ----------------------
with st.sidebar:
    st.markdown("<h2 style='color:#fef3c7!important;border-left:5px solid #d97706!important;'>🧭 控制中心</h2>", unsafe_allow_html=True)
    mode = st.radio("请选择视窗模式", ["🎯 新比赛录入", "📜 历史比赛查询", "📈 选手数据看板"])

# ---------------------- 🎯 新比赛录入 ----------------------
if mode == "🎯 新比赛录入":
    with st.sidebar:
        st.markdown("<hr style='border-color:rgba(255,255,255,0.1)'/>", unsafe_allow_html=True)
        st.subheader("📝 实时对局登记")
        st.session_state.match_name = st.text_input("比赛名称名称", value=st.session_state.match_name)
        match_date = st.date_input("选择比赛日期", value=datetime.now())
        date_str = match_date.strftime("%Y%m%d")
        round_num = len(st.session_state.current_match) + 1
        st.info(f"🎯 当前局数：第 {round_num} 局 / 上限 {MAX_ROUNDS} 局")
        
        if round_num > MAX_ROUNDS:
            st.error("已达上限，请先点击保存到云端！")
            st.stop()
        
        player_east = st.selectbox("东风位选手", PLAYER_LIST, index=0)
        player_south = st.selectbox("南风位选手", PLAYER_LIST, index=1)
        player_west = st.selectbox("西风位选手", PLAYER_LIST, index=2)
        player_north = st.selectbox("北风位选手", PLAYER_LIST, index=3)
        pos_to_player = {"东风": player_east, "南风": player_south, "西风": player_west, "北风": player_north}
        player_to_pos = {v:k for k,v in pos_to_player.items()}
        player_names = list(pos_to_player.values())
        score_cols = [f"{name}({pos})" for pos, name in pos_to_player.items()]
        
        current_dealer_player = st.selectbox("当前局庄家", player_names, index=0)
        current_dealer_pos = player_to_pos[current_dealer_player]
        dealer_level = st.selectbox("庄家连庄状态", list(DEALER_LEVELS.keys()), index=0)
        dealer_multi = DEALER_LEVELS[dealer_level]
        
        hu_type = st.selectbox("本局结果判定", HU_TYPES)
        fan = 0; hu_player = ""; pao_player = ""
        if hu_type != "流局":
            fan = st.number_input("胡牌番数", min_value=1, value=1)
            hu_player = st.selectbox("胡牌获胜选手", player_names, index=0)
            hu_pos = player_to_pos[hu_player]
            if hu_type == "放炮":
                pao_candidates = [p for p in player_names if p != hu_player]
                pao_player = st.selectbox("点炮选手", pao_candidates, index=0)
                pao_pos = player_to_pos[pao_player]
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 提交本局", type="primary", use_container_width=True):
                scores = {"东风": 0, "南风": 0, "西风": 0, "北风": 0}
                if hu_type != "流局":
                    other_pos = [p for p in POSITION_ORDER if p != hu_pos]
                    dealer_hu = (hu_pos == current_dealer_pos)
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
                    "局号": round_num, "庄家": current_dealer_player, "连庄次数": dealer_level,
                    "庄倍数": dealer_multi, "本局结果": hu_type, "胡牌选手": hu_player,
                    "放炮选手": pao_display, "番数": fan if hu_type != "流局" else 0,
                    score_cols[0]: scores["东风"], score_cols[1]: scores["南风"],
                    score_cols[2]: scores["西风"], score_cols[3]: scores["北风"]
                }
                st.session_state.current_match.append(round_data)
                st.rerun()
        
        with col2:
            if st.button("↩️ 撤销上局", use_container_width=True) and len(st.session_state.current_match) > 0:
                st.session_state.current_match.pop()
                st.rerun()
        
        st.divider()
        if st.button("☁️ 将整场封盘保存至云端", use_container_width=True):
            if len(st.session_state.current_match) == 0:
                st.error("当前场次尚未录入任何对局信息！")
            else:
                with st.spinner("正在安全同步加密通道至云端..."):
                    db = load_github_db()
                    old_summary = db["比赛汇总"]
                    df = pd.DataFrame(st.session_state.current_match)
                    total_scores = [df[col].sum() for col in score_cols]
                    rank_result = sorted(zip(player_names, total_scores), key=lambda x: x[1], reverse=True)
                    summary_row = pd.DataFrame([{
                        "比赛名称": st.session_state.match_name,
                        "比赛日期": match_date.strftime("%Y-%m-%d"),
                        "第1名": rank_result[0][0], "第1名名次分": 5,
                        "第2名": rank_result[1][0], "第2名名次分": 3,
                        "第3名": rank_result[2][0], "第3名名次分": 2,
                        "第4名": rank_result[3][0], "第4名名次分": 1
                    }])
                    new_summary = pd.concat([old_summary, summary_row], ignore_index=True)
                    new_sheet_name = f"明细_{date_str}_{st.session_state.match_name}"[:30]
                    
                    with pd.ExcelWriter(DB_FILE) as writer:
                        new_summary.to_excel(writer, sheet_name="比赛汇总", index=False)
                        df.to_excel(writer, sheet_name=new_sheet_name, index=False)
                        for sheet_name, sheet_df in db.items():
                            if sheet_name not in ["比赛汇总", new_sheet_name]:
                                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    if save_github_db():
                        st.cache_data.clear()
                        st.toast("🎉 数据云端存盘成功！", icon="✅")
                        st.session_state.current_match = []
                        st.rerun()
        
        if st.button("🔄 开辟全新比赛", use_container_width=True):
            st.session_state.current_match = []
            st.session_state.match_name = f"比赛_{datetime.now().strftime('%Y%m%d')}"
            st.rerun()

    # 右侧展示区
    df = pd.DataFrame(st.session_state.current_match)
    st.subheader("📊 本场时时计分榜")
    total_scores = [df[col].sum() for col in score_cols] if len(df) > 0 else [0,0,0,0]
    
    # 自动适应：PC端1行4列，手机端横向排不下时自动换行
    cols = st.columns(4)
    for i, (name, score) in enumerate(zip(player_names, total_scores)):
        cols[i].metric(label=f"👑 {name}", value=f"{score} Pts")
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # 左右双栏：PC端并排，手机端上下排列
    layout_col1, layout_col2 = st.columns([3, 2])
    with layout_col1:
        st.subheader("📋 实时流水单细则")
        if len(df) > 0:
            def color_score(val):
                if isinstance(val, (int, float)):
                    color = "#16a34a" if val > 0 else "#dc2626" if val < 0 else "#6b7280"
                    return f"color: {color}; font-weight: bold; font-size:14px;"
                return ""
            styled_df = df.style.map(color_score, subset=score_cols)
            st.dataframe(styled_df, use_container_width=True, hide_index=True, height=450)
        else:
            st.info("💡 虚位以待，请在左侧侧边栏录入第一局对局数据。")
            
    with layout_col2:
        st.subheader("📈 本场积分演变动向")
        if len(df) > 0:
            trend_df = df[score_cols].cumsum().reset_index().rename(columns={"index": "局号"})
            trend_df["局号"] += 1
            trend_df = trend_df.melt(id_vars=["局号"], var_name="选手", value_name="累计积分")
            fig = px.line(trend_df, x="局号", y="累计积分", color="选手", markers=True, line_shape="spline")
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10), font=dict(color="#451a03")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 录入数据后将自动绘制波段走势图。")

# ---------------------- 📜 历史比赛查询 ----------------------
elif mode == "📜 历史比赛查询":
    st.header("📜 历史对局封存卷轴")
    with st.spinner("正在开启云端古籍..."):
        db = load_github_db()
    summary_df = db["比赛汇总"]
    if len(summary_df) == 0:
        st.info("云端未发现历史封存记录")
    else:
        match_options = [f"📅 {row['比赛日期']} — 🏆 {row['比赛名称']}" for _, row in summary_df.iterrows()]
        selected_match = st.selectbox("请挑选您需要复盘的比赛场次", match_options)
        selected_idx = match_options.index(selected_match)
        
        selected_row = summary_df.iloc[selected_idx]
        selected_date = selected_row["比赛日期"].replace("-", "")
        selected_name = selected_row["比赛名称"]
        target_sheet = f"明细_{selected_date}_{selected_name}"[:30]
        
        if target_sheet in db:
            match_detail = db[target_sheet]
            score_cols = [col for col in match_detail.columns if "(" in col]
            player_names = [col.split("(")[0] for col in score_cols]
            total_scores = [match_detail[col].sum() for col in score_cols]
            
            cols = st.columns(4)
            for i, (name, score) in enumerate(zip(player_names, total_scores)):
                cols[i].metric(label=name, value=f"{score} 分")
            
            st.markdown("<br/>", unsafe_allow_html=True)
            q_col1, q_col2 = st.columns([3, 2])
            with q_col1:
                st.subheader("📋 历史输赢逐局明细")
                st.dataframe(match_detail, use_container_width=True, hide_index=True)
            with q_col2:
                st.subheader("📈 历史复盘走势重现")
                trend_df = match_detail[score_cols].cumsum().reset_index().rename(columns={"index": "局号"})
                trend_df["局号"] += 1
                trend_df = trend_df.melt(id_vars=["局号"], var_name="选手", value_name="累计积分")
                fig = px.line(trend_df, x="局号", y="累计积分", color="选手", markers=True, line_shape="spline")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("未找到对应的复盘明细。")

# ---------------------- 📈 选手数据看板 ----------------------
else:
    with st.spinner("数据精算中..."):
        db = load_github_db()
    summary_df = db["比赛汇总"].copy()
    
    if len(summary_df) == 0:
        st.info("暂无历史大盘数据。")
    else:
        summary_df["比赛日期"] = pd.to_datetime(summary_df["比赛日期"])
        summary_df["年度"] = summary_df["比赛日期"].dt.year
        summary_df["季度"] = summary_df["比赛日期"].dt.to_period("Q").astype(str)
        summary_df["月度"] = summary_df["比赛日期"].dt.to_period("M").astype(str)
        
        rows = []
        for _, row in summary_df.iterrows():
            for r in range(1, 5):
                p_name = row[f"第{r}名"]
                p_score = row[f"第{r}名名次分"]
                if pd.notna(p_name):
                    rows.append({
                        "比赛日期": row["比赛日期"], "年度": row["年度"], 
                        "季度": row["季度"], "月度": row["月度"],
                        "选手": p_name, "名次分": p_score
                    })
        all_scores_df = pd.DataFrame(rows)
        
        st.subheader("🎛️ 周期时间维度筛选")
        time_dim = st.radio("时间轴选择", ["全部历史", "按年度统计", "按季度统计", "按月度统计"], horizontal=True)
        
        filtered_df = all_scores_df.copy()
        if time_dim == "按年度统计":
            filtered_df = filtered_df[filtered_df["年度"] == st.selectbox("年份选择", sorted(all_scores_df["年度"].unique(), reverse=True))]
        elif time_dim == "按季度统计":
            filtered_df = filtered_df[filtered_df["季度"] == st.selectbox("季度选择", sorted(all_scores_df["季度"].unique(), reverse=True))]
        elif time_dim == "按月度统计":
            filtered_df = filtered_df[filtered_df["月度"] == st.selectbox("月份选择", sorted(all_scores_df["月度"].unique(), reverse=True))]

        stats_rows = []
        for player in PLAYER_LIST:
            player_df = filtered_df[filtered_df["选手"] == player]
            games = len(player_df)
            avg_s = player_df["名次分"].mean() if games > 0 else 0.0
            total_s = player_df["名次分"].sum() if games > 0 else 0
            stats_rows.append({"选手": player, "总参赛场数": games, "平均名次分": round(avg_s, 2), "累计总名次分": total_s})
        stats_output_df = pd.DataFrame(stats_rows).sort_values(by="累计总名次分", ascending=False)
        
        st.subheader(f"🏆 雀坛英雄绩效大盘单 ({time_dim})")
        st.dataframe(stats_output_df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("📈 全员天梯竞技积分演变动线（纵览全局）")
        all_scores_df = all_scores_df.sort_values(by="比赛日期").reset_index(drop=True)
        all_scores_df["场次序号"] = all_scores_df.groupby("选手").cumcount() + 1
        
        chart_type = st.segmented_control("曲线显示切换", ["累计总分大盘走势", "单场天梯分波动"], default="累计总分大盘走势")
        if chart_type == "累计总分大盘走势":
            all_scores_df["展示分数"] = all_scores_df.groupby("选手")["名次分"].cumsum()
            y_label = "天梯累计分"
        else:
            all_scores_df["展示分数"] = all_scores_df["名次分"]
            y_label = "当场名次分"
            
        fig_players = px.line(all_scores_df, x="场次序号", y="展示分数", color="选手", markers=True, line_shape="spline")
        fig_players.update_layout(
            hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=15, r=15, t=15, b=15)
        )
        st.plotly_chart(fig_players, use_container_width=True)
