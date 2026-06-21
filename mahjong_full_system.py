import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import os
import base64
import requests

# ====================== 配置区（改成你自己的） ======================
GITHUB_REPO = "rainbin47/majiang-game"  # 比如：zhangsan/majiang-game
GITHUB_TOKEN = st.secrets["github_token"]
DB_FILE = "麻坛所有比赛数据.xlsx"

# ====================== 修复后的GitHub读写函数 ======================
def load_github_db():
    """从GitHub下载最新的Excel"""
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{DB_FILE}"
    res = requests.get(url)
    with open(DB_FILE, "wb") as f:
        f.write(res.content)
    # 读取所有sheet
    return pd.read_excel(DB_FILE, sheet_name=None)

def save_github_db():
    """保存到GitHub，加错误提示"""
    # 1. 读取本地文件
    with open(DB_FILE, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    
    # 2. 获取文件最新sha
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        st.error(f"获取文件失败：{res.json()['message']}")
        return False
    sha = res.json()["sha"]
    
    # 3. 提交到GitHub
    res = requests.put(url, headers=headers, json={
        "message": f"更新比赛数据 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": content,
        "sha": sha
    })
    if res.status_code in [200, 201]:
        return True
    else:
        st.error(f"提交失败：{res.json()['message']}")
        return False

# ====================== 页面配置和美化 ======================
st.set_page_config(
    page_title="麻坛风云录（云端版）",
    page_icon="🀄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    font-family: "微软雅黑", sans-serif;
}
h1 {
    color: #b91c1c;
    text-align: center;
    font-weight: 800;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 30px;
}
h2, h3 {
    color: #92400e;
    border-left: 4px solid #b91c1c;
    padding-left: 12px;
    margin-top: 30px;
    margin-bottom: 20px;
}
div[data-testid="metric-container"] {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 20px 10px;
    border: 1px solid #fecaca;
    transition: all 0.3s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}
.stButton>button {
    background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 600;
    box-shadow: 0 4px 10px rgba(185,28,28,0.3);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #991b1b 0%, #b91c1c 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(185,28,28,0.4);
}
.css-1d391kg {
    background: linear-gradient(180deg, #fef2f2 0%, #fee2e2 100%);
    border-right: 2px solid #fecaca;
}
.stDataFrame {
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    overflow: hidden;
}
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #fecaca, transparent);
    margin: 30px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🀄 麻坛风云录 云端版")

# 业务配置
MAX_ROUNDS = 99
POSITION_ORDER = ["东风", "南风", "西风", "北风"]
PLAYER_LIST = ["奶猫", "农少", "老王", "老野", "老蒋", "老潘", "阿狗", "孙军"]
DEALER_LEVELS = {
    "第一庄（2倍）": 2,
    "第二庄（4倍）": 4,
    "第三庄及以上（8倍）": 8
}
HU_TYPES = ["自摸", "放炮", "流局"]
RANK_SCORE = {1:5, 2:3, 3:2, 4:1}

if "current_match" not in st.session_state:
    st.session_state.current_match = []
if "match_name" not in st.session_state:
    st.session_state.match_name = f"比赛_{datetime.now().strftime('%Y%m%d')}"

# ---------------------- 侧边栏 ----------------------
with st.sidebar:
    mode = st.radio("功能模式", ["🎯 新比赛录入", "📜 历史比赛查询"])

# ---------------------- 新比赛录入 ----------------------
if mode == "🎯 新比赛录入":
    with st.sidebar:
        st.header("📝 对局录入")
        st.session_state.match_name = st.text_input("比赛名称", value=st.session_state.match_name)
        match_date = st.date_input("比赛日期", value=datetime.now())
        date_str = match_date.strftime("%Y%m%d")
        round_num = len(st.session_state.current_match) + 1
        st.info(f"🎯 当前第 {round_num} 局 / 最多{MAX_ROUNDS}局")
        
        if round_num > MAX_ROUNDS:
            st.error("本场已达到99局上限，请保存比赛！")
            st.stop()
        
        player_east = st.selectbox("东风位", PLAYER_LIST, index=0)
        player_south = st.selectbox("南风位", PLAYER_LIST, index=1)
        player_west = st.selectbox("西风位", PLAYER_LIST, index=2)
        player_north = st.selectbox("北风位", PLAYER_LIST, index=3)
        pos_to_player = {"东风": player_east, "南风": player_south, "西风": player_west, "北风": player_north}
        player_to_pos = {v:k for k,v in pos_to_player.items()}
        player_names = list(pos_to_player.values())
        score_cols = [f"{name}({pos})" for pos, name in pos_to_player.items()]
        
        current_dealer_player = st.selectbox("当前庄家", player_names, index=0)
        current_dealer_pos = player_to_pos[current_dealer_player]
        dealer_level = st.selectbox("连庄次数", list(DEALER_LEVELS.keys()), index=0)
        dealer_multi = DEALER_LEVELS[dealer_level]
        
        hu_type = st.selectbox("本局结果", HU_TYPES)
        fan = 0
        hu_player = ""
        pao_player = ""
        if hu_type != "流局":
            fan = st.number_input("胡牌番数", min_value=1, value=1)
            hu_player = st.selectbox("胡牌选手", player_names, index=0)
            hu_pos = player_to_pos[hu_player]
            if hu_type == "放炮":
                pao_candidates = [p for p in player_names if p != hu_player]
                pao_player = st.selectbox("放炮选手", pao_candidates, index=0)
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
                            if dealer_hu or (p == current_dealer_pos):
                                base *= dealer_multi
                            scores[p] = -base
                            scores[hu_pos] += base
                    else:
                        for p in other_pos:
                            base = fan * 2 if p == pao_pos else fan
                            if dealer_hu or (p == current_dealer_pos):
                                base *= dealer_multi
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
                st.success(f"🎉 第{round_num}局提交成功！")
                st.rerun()
        
        with col2:
            if st.button("↩️ 撤销上一局", use_container_width=True) and len(st.session_state.current_match) > 0:
                st.session_state.current_match.pop()
                st.success("已撤销上一局")
                st.rerun()
        
        st.divider()
        # 修复后的保存到云端按钮
        if st.button("☁️ 保存到云端", type="secondary", use_container_width=True):
            if len(st.session_state.current_match) == 0:
                st.error("还没有录入对局！")
            else:
                with st.spinner("正在同步到云端..."):
                    # 1. 读取云端所有数据
                    db = load_github_db()
                    # 2. 处理汇总表
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
                    
                    # 3. 保存所有sheet到本地Excel
                    with pd.ExcelWriter(DB_FILE) as writer:
                        new_summary.to_excel(writer, sheet_name="比赛汇总", index=False)
                        # 保存本场明细
                        df.to_excel(writer, sheet_name=f"对局明细_{date_str}", index=False)
                        # 保留所有历史sheet
                        for sheet_name, sheet_df in db.items():
                            if sheet_name not in ["比赛汇总", f"对局明细_{date_str}"]:
                                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # 4. 同步到GitHub
                    success = save_github_db()
                    if success:
                        st.cache_data.clear()
                        st.success("✅ 比赛已成功同步到GitHub！")
                        st.session_state.current_match = []
                        st.rerun()
        
        if st.button("🔄 新建比赛", use_container_width=True):
            st.session_state.current_match = []
            st.session_state.match_name = f"比赛_{datetime.now().strftime('%Y%m%d')}"
            st.rerun()

    # 右侧展示
    df = pd.DataFrame(st.session_state.current_match)
    st.subheader("📊 本场实时总得分")
    total_scores = [df[col].sum() for col in score_cols] if len(df) > 0 else [0,0,0,0]
    cols = st.columns(4)
    for i, (name, score) in enumerate(zip(player_names, total_scores)):
        cols[i].metric(label=name, value=f"{score}分")
    
    st.divider()
    st.subheader("📋 本场对局明细")
    if len(df) > 0:
        def color_score(val):
            if isinstance(val, (int, float)):
                color = "#16a34a" if val > 0 else "#dc2626" if val < 0 else "black"
                return f"color: {color}; font-weight: bold;"
            return ""
        styled_df = df.style.map(color_score, subset=score_cols)
        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("✨ 暂无对局数据")
    
    st.divider()
    if len(df) > 0:
        st.subheader("📈 积分趋势曲线")
        trend_df = df[score_cols].cumsum().reset_index().rename(columns={"index": "局号"})
        trend_df["局号"] += 1
        trend_df = trend_df.melt(id_vars=["局号"], var_name="选手", value_name="累计积分")
        fig = px.line(trend_df, x="局号", y="累计积分", color="选手", markers=True, line_shape="spline", height=450)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader("📌 选手统计")
        stats_df = pd.DataFrame({
            "选手": player_names,
            "胡牌次数": [len(df[(df["本局结果"].isin(["自摸","放炮"])) & (df["胡牌选手"] == name)]) for name in player_names],
            "放炮次数": [len(df[(df["本局结果"]=="放炮") & (df["放炮选手"] == name)]) for name in player_names]
        }).sort_values("胡牌次数", ascending=False)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

# ---------------------- 历史比赛查询 ----------------------
else:
    st.header("📜 云端历史比赛查询")
    with st.spinner("正在加载云端数据..."):
        db = load_github_db()
    summary_df = db["比赛汇总"]
    if len(summary_df) == 0:
        st.info("云端暂无历史比赛")
    else:
        match_options = [f"{row['比赛日期']} - {row['比赛名称']}" for _, row in summary_df.iterrows()]
        selected_match = st.selectbox("选择要查看的比赛", match_options)
        selected_idx = match_options.index(selected_match)
        selected_date = summary_df.iloc[selected_idx]["比赛日期"].replace("-", "")
        match_detail = db[f"对局明细_{selected_date}"]
        
        score_cols = [col for col in match_detail.columns if "(" in col]
        player_names = [col.split("(")[0] for col in score_cols]
        total_scores = [match_detail[col].sum() for col in score_cols]
        
        st.subheader(f"📊 {selected_match} 总得分")
        cols = st.columns(4)
        for i, (name, score) in enumerate(zip(player_names, total_scores)):
            cols[i].metric(label=name, value=f"{score}分")
        
        st.divider()
        st.subheader("📋 对局明细")
        def color_score(val):
            if isinstance(val, (int, float)):
                color = "#16a34a" if val > 0 else "#dc2626" if val < 0 else "black"
                return f"color: {color}; font-weight: bold;"
            return ""
        styled_df = match_detail.style.map(color_score, subset=score_cols)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("📈 积分趋势曲线")
        trend_df = match_detail[score_cols].cumsum().reset_index().rename(columns={"index": "局号"})
        trend_df["局号"] += 1
        trend_df = trend_df.melt(id_vars=["局号"], var_name="选手", value_name="累计积分")
        fig = px.line(trend_df, x="局号", y="累计积分", color="选手", markers=True, line_shape="spline", height=450)
        st.plotly_chart(fig, use_container_width=True)
