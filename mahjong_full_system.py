import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# 页面配置
st.set_page_config(page_title="麻坛比赛管理系统", layout="wide")
st.title("🎲 麻坛风云录 比赛管理系统")

# 全局配置
MAX_ROUNDS = 99  # 单场最多99局
POSITION_ORDER = ["东风", "南风", "西风", "北风"]
PLAYER_LIST = ["奶猫", "农少", "老王", "老野", "老蒋", "老潘", "阿狗", "孙军"]
DEALER_LEVELS = {
    "第一庄（2倍）": 2,
    "第二庄（4倍）": 4,
    "第三庄及以上（8倍）": 8
}
HU_TYPES = ["自摸", "放炮", "流局"]

# 初始化session state
if "current_match" not in st.session_state:
    st.session_state.current_match = []
if "match_name" not in st.session_state:
    st.session_state.match_name = f"比赛_{datetime.now().strftime('%Y%m%d')}"

# ---------------------- 左侧：录入界面 ----------------------
with st.sidebar:
    st.header("📝 对局录入")
    
    # 比赛信息
    st.subheader("比赛信息")
    st.session_state.match_name = st.text_input("比赛名称", value=st.session_state.match_name)
    round_num = len(st.session_state.current_match) + 1
    st.info(f"当前第 {round_num} 局 / 最多{MAX_ROUNDS}局")
    
    if round_num > MAX_ROUNDS:
        st.error("本场已达到99局上限，请新建比赛！")
        st.stop()
    
    # 选手位置绑定
    st.subheader("参赛选手")
    player_east = st.selectbox("东风位", PLAYER_LIST, index=0)
    player_south = st.selectbox("南风位", PLAYER_LIST, index=1)
    player_west = st.selectbox("西风位", PLAYER_LIST, index=2)
    player_north = st.selectbox("北风位", PLAYER_LIST, index=3)
    pos_to_player = {
        "东风": player_east,
        "南风": player_south,
        "西风": player_west,
        "北风": player_north
    }
    player_to_pos = {v:k for k,v in pos_to_player.items()}
    # 固定4个选手
    player_names = list(pos_to_player.values())
    score_cols = [f"{name}({pos})" for pos, name in pos_to_player.items()]
    
    # 对局信息录入
    st.subheader(f"第{round_num}局信息")
    current_dealer_player = st.selectbox("当前庄家", player_names, index=0)
    current_dealer_pos = player_to_pos[current_dealer_player]
    dealer_level = st.selectbox("连庄次数", list(DEALER_LEVELS.keys()), index=0)
    dealer_multi = DEALER_LEVELS[dealer_level]
    
    hu_type = st.selectbox("本局结果", HU_TYPES)
    fan = 0
    hu_pos = ""
    pao_pos = ""
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
    
    # 提交按钮
    if st.button("✅ 提交本局", type="primary", use_container_width=True):
        scores = {"东风": 0, "南风": 0, "西风": 0, "北风": 0}
        
        if hu_type != "流局":
            other_pos = [p for p in POSITION_ORDER if p != hu_pos]
            dealer_hu = (hu_pos == current_dealer_pos)  # 是否是庄家胡牌
            
            if hu_type == "自摸":
                for p in other_pos:
                    base = fan * 2  # 自摸翻倍
                    # 庄家胡牌 → 所有三家都乘庄倍数；闲家胡牌 → 只有庄家乘庄倍数
                    if dealer_hu or (p == current_dealer_pos):
                        base *= dealer_multi
                    scores[p] = -base
                    scores[hu_pos] += base
            
            else: # 放炮
                for p in other_pos:
                    if p == pao_pos: # 放炮者翻倍
                        base = fan * 2
                    else:
                        base = fan
                    # 庄家胡牌 → 所有三家都乘庄倍数；闲家胡牌 → 只有庄家乘庄倍数
                    if dealer_hu or (p == current_dealer_pos):
                        base *= dealer_multi
                    scores[p] = -base
                    scores[hu_pos] += base
        
        # 自摸时放炮选手填斜线
        pao_display = pao_player if hu_type == "放炮" else "/" if hu_type == "自摸" else ""
        
        round_data = {
            "局号": round_num,
            "庄家": current_dealer_player,
            "连庄次数": dealer_level,
            "庄倍数": dealer_multi,
            "本局结果": hu_type,
            "胡牌选手": hu_player,
            "放炮选手": pao_display,
            "番数": fan if hu_type != "流局" else 0,
            score_cols[0]: scores["东风"],
            score_cols[1]: scores["南风"],
            score_cols[2]: scores["西风"],
            score_cols[3]: scores["北风"]
        }
        st.session_state.current_match.append(round_data)
        st.success(f"第{round_num}局提交成功！")
        st.rerun()
    
    # 工具按钮
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 新建比赛", use_container_width=True):
            st.session_state.current_match = []
            st.session_state.match_name = f"比赛_{datetime.now().strftime('%Y%m%d')}"
            st.rerun()
    with col2:
        if st.button("↩️ 撤销上一局", use_container_width=True) and len(st.session_state.current_match) > 0:
            st.session_state.current_match.pop()
            st.success("已撤销上一局")
            st.rerun()

# ---------------------- 右侧：统一页面展示 ----------------------
df = pd.DataFrame(st.session_state.current_match)

# 1. 第一行：实时总得分展示
st.subheader("📊 实时总得分")
if len(df) > 0:
    total_scores = [df[col].sum() for col in score_cols]
else:
    total_scores = [0, 0, 0, 0]

cols = st.columns(4)
for i, (name, score) in enumerate(zip(player_names, total_scores)):
    color = "#1f77b4" if score >= 0 else "#d62728"
    cols[i].metric(label=name, value=f"{score}分", delta_color="off")
    cols[i].markdown(f"<h3 style='text-align: center; color: {color};'>{score}</h3>", unsafe_allow_html=True)

st.divider()

# 2. 对局明细表
st.subheader("📋 对局明细")
if len(df) > 0:
    # 自定义样式：正数蓝色，负数红色
    def color_score(val):
        if isinstance(val, (int, float)):
            color = "#1f77b4" if val > 0 else "#d62728" if val < 0 else "black"
            return f"color: {color}; font-weight: bold;"
        return ""
    
    styled_df = df.style.map(color_score, subset=score_cols)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # 导出Excel：第一行加总统计，去掉选手统计sheet
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # 先写总统计行
        total_row = pd.DataFrame([{
            "局号": "总得分",
            "庄家": "",
            "连庄次数": "",
            "庄倍数": "",
            "本局结果": "",
            "胡牌选手": "",
            "放炮选手": "",
            "番数": "",
            **{col: df[col].sum() for col in score_cols}
        }])
        total_row.to_excel(writer, sheet_name="对局明细", index=False, startrow=0)
        # 再写对局明细
        df.to_excel(writer, sheet_name="对局明细", index=False, startrow=2)
    
    st.download_button(
        label="📥 下载本场Excel数据",
        data=buffer.getvalue(),
        file_name=f"{st.session_state.match_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("暂无对局数据，请在左侧录入")

st.divider()

# 3. 实时积分曲线
st.subheader("📈 积分趋势曲线")
if len(df) > 0:
    trend_df = df[score_cols].cumsum().reset_index().rename(columns={"index": "局号"})
    trend_df["局号"] = trend_df["局号"] + 1
    trend_df = trend_df.melt(id_vars=["局号"], var_name="选手", value_name="累计积分")
    
    fig = px.line(
        trend_df, x="局号", y="累计积分", color="选手",
        markers=True, title="选手累计积分变化",
        line_shape="spline", height=400
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("录入对局后自动生成曲线")

st.divider()

# 4. 选手统计
st.subheader("📌 选手统计")
if len(df) > 0:
    stats_df = pd.DataFrame({
        "选手": player_names,
        "总积分": total_scores,
        "胡牌次数": [len(df[(df["本局结果"].isin(["自摸","放炮"])) & (df["胡牌选手"] == name)]) for name in player_names],
        "放炮次数": [len(df[(df["本局结果"]=="放炮") & (df["放炮选手"] == name)]) for name in player_names]
    }).sort_values("总积分", ascending=False)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
else:
    st.info("暂无数据")