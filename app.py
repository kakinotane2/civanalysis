import streamlit as st
import pandas as pd
import os

# --- ページ設定（恐竜研究所風） ---
st.set_page_config(page_title="シヴ編成分析所", layout="wide")

# 見た目をカッコよくする設定
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    h1 { color: #ff8c00; border-bottom: 2px solid #ff8c00; padding-bottom: 10px; }
    h2 { color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ シヴ編成分析所")
st.caption("ギルドメンバー全員で使える戦績管理システム")

# --- データの読み込み ---
CSV_FILE = 'battle_logs.csv'
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=['日時', '味方1', '味方2', '味方3', '敵1', '敵2', '敵3', '結果'])

# --- サイドメニュー ---
st.sidebar.title("MENU")
menu = st.sidebar.radio("機能を選択", ["📊 戦績分析", "📝 使い方ガイド"])

if menu == "📊 戦績分析":
    st.header("📈 チーム全体の統計")
    
    # 上段に数字を並べる
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("総試合数", len(df))
    with m2:
        win_count = len(df[df['結果'] == '勝利'])
        win_rate = (win_count / len(df) * 100) if len(df) > 0 else 0
        st.metric("平均勝率", f"{win_rate:.1f}%")
    with m3:
        st.metric("登録武将数", len(df['味方1'].unique()) if not df.empty else 0)

    st.subheader("📋 最新の戦闘履歴")
    st.dataframe(df.sort_values('日時', ascending=False), use_container_width=True)

elif menu == "📝 使い方ガイド":
    st.header("📖 はじめての方へ")
    st.success("STEP 1: Discordで戦績スクショを投稿")
    st.info("STEP 2: Botが自動で読み取ってここに追加されます")
    st.warning("STEP 3: 左のメニューから分析データを確認！")
