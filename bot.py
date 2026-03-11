import discord
import easyocr
import cv2
import numpy as np
import csv
import os
from datetime import datetime

# --- 設定：英傑リスト（大幅追加！） ---
CHARACTERS = {
    "トミュリス": ["トミュリス"],
    "マリア・テレジア": ["マリア", "テレジア"],
    "アーサー": ["アーサー"],
    "リンカーン": ["リンカーン", "エイブラハム"],
    "風磨小太郎": ["風磨", "小太郎", "磨"],
    "ゼノビア": ["ゼノビア"],
    "ヒュパティア": ["ヒュパティア"],
    "虞美人": ["虞美人"],
    "劉備": ["劉備", "リョウビ"],
    "ソンドク": ["ソンドク", "善徳"],
    "ペリクレス": ["ペリクレス"],
    "マルクス": ["マルクス"],
    "武則天": ["武則天"],
    "孫武": ["孫武"],
    "ジャンヌ・ダルク": ["ジャンヌ", "ダルク"],
    "エドワード": ["エドワード"],
    "織田信長": ["織田", "信長"],
    "曹操": ["曹操"]
}

reader = easyocr.Reader(['ja', 'en'])
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

CSV_FILE = 'battle_logs.csv'

# ファイルがない場合はヘッダー作成
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', encoding='utf_8_sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["日時", "味方1", "味方2", "味方3", "敵1", "敵2", "敵3", "結果"])

def get_chars(text):
    found = []
    for name, keywords in CHARACTERS.items():
        if any(k in text for k in keywords):
            found.append(name)
    # 重複を消して、パーティ名がズレないように名前順でソート
    found = sorted(list(dict.fromkeys(found)))
    return (found + ["不明"] * 3)[:3]

@client.event
async def on_ready():
    print(f'パーティ相性分析システム 起動！！')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # 📊 パーティ別 相性集計
    if message.content == "!集計":
        if not os.path.exists(CSV_FILE):
            await message.channel.send("データがありません。")
            return
        with open(CSV_FILE, 'r', encoding='utf_8_sig') as f:
            data = list(csv.reader(f))[1:]
        if not data:
            await message.channel.send("データが0件です。")
            return

        matchups = {} 

        for r in data:
            my_pt = "・".join([c for c in r[1:4] if c != "不明"])
            en_pt = "・".join([c for c in r[4:7] if c != "不明"])
            result = r[7]
            
            # 「味方PT vs 敵PT」を1つのキーにする
            key = f"🟦 {my_pt}\n 🆚 \n🟥 {en_pt}"
            if key not in matchups: matchups[key] = [0, 0]
            
            matchups[key][1] += 1
            if result == "勝利": matchups[key][0] += 1

        msg = "⚔️ **【パーティ別 相性データ】**\n"
        # 対戦数が多い順にランキング表示
        for card, s in sorted(matchups.items(), key=lambda x: x[1][1], reverse=True)[:10]:
            rate = (s[0]/s[1])*100
            msg += f"{card}\n🔥 **勝率: {rate:.1f}%** ({s[0]}勝/{s[1]}戦)\n"
            msg += "--------------------------\n"
        
        await message.channel.send(msg)
        return

    # 🖼 画像解析
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'heic']):
                await message.channel.send("📊 戦報を高度解析中...")
                image_data = await attachment.read()
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                h, w, _ = img.shape
                
                # 上半分（自軍）と下半分（敵軍）を解析
                my_text = " ".join([res[1] for res in reader.readtext(img[0:h//2, 0:w])])
                en_text = " ".join([res[1] for res in reader.readtext(img[h//2:h, 0:w])])
                
                # 勝敗判定（「失敗」という文字も考慮）
                res_status = "勝利" if "勝利" in (my_text + en_text) else "敗北" if "失敗" in (my_text + en_text) or "敗北" in (my_text + en_text) else "分戦"
                
                my_team = get_chars(my_text)
                en_team = get_chars(en_text)
                
                # CSVに保存
                with open(CSV_FILE, 'a', encoding='utf_8_sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), *my_team, *en_team, res_status])
                
                # 結果をDiscordにリッチに表示
                embed = discord.Embed(title="⚔️ 戦報解析完了", color=0x00ff00 if res_status == "勝利" else 0xff0000)
                embed.add_field(name="🟦 自軍編成", value=" / ".join(my_team), inline=False)
                embed.add_field(name="🟥 敵軍編成", value=" / ".join(en_team), inline=False)
                embed.add_field(name="🚩 結果", value=f"**{res_status}**", inline=True)
                await message.channel.send(embed=embed)

# --- あなたのトークンに書き換え済み ---
import os
# 直接トークンを書かずに「環境変数」から読み込むように変更
token = os.getenv('DISCORD_TOKEN')
client.run(token)