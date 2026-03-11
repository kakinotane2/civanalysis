# test
import streamlit as st
import pandas as pd
import os

# サイトの基本設定
st.set_page_config(page_title="シヴ編成分析所", layout="wide")

st.title("🛡️ シヴ編成分析ダッシュボード")
st.caption("Botが収集した戦報データを元にリアルタイム分析します")

CSV_FILE = 'battle_logs.csv'

# データの読み込み
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    
    # --- サイドメニュー（ボタン代わり） ---
    menu = st.sidebar.radio("メニューを選択", ["全体データ", "パーティ相性分析", "日別勝率グラフ"])

    if menu == "全体データ":
        st.subheader("📋 記録された全データ")
        st.dataframe(df)

    elif menu == "パーティ相性分析":
        st.subheader("⚔️ パーティ vs パーティ 相性表")
        # 味方と敵のパーティ文字列を作成
        df['味方PT'] = df[['味方1', '味方2', '味方3']].fillna('').apply(lambda x: '・'.join([i for i in x if i]), axis=1)
        df['敵PT'] = df[['敵1', '敵2', '敵3']].fillna('').apply(lambda x: '・'.join([i for i in x if i]), axis=1)
        
        # 集計
        matchup = df.groupby(['味方PT', '敵PT', '結果']).size().unstack(fill_value=0)
        if '勝利' not in matchup: matchup['勝利'] = 0
        if '敗北' not in matchup: matchup['敗北'] = 0
        
        matchup['試合数'] = matchup.sum(axis=1)
        matchup['勝率'] = (matchup['勝利'] / matchup['試合数'] * 100).round(1)
        
        st.table(matchup[['試合数', '勝利', '勝率']].sort_values('試合数', ascending=False))

    elif menu == "日別勝率グラフ":
        st.subheader("📅 日別の戦績推移")
        df['日付'] = pd.to_datetime(df['日時']).dt.date
        daily = df.groupby(['日付', '結果']).size().unstack(fill_value=0)
        if '勝利' not in daily: daily['勝利'] = 0
        
        st.line_chart(daily['勝利'])
        st.bar_chart(daily)

else:

    st.error("まだデータ（battle_logs.csv）がありません。Botに画像を投げてデータを作ってください！")
