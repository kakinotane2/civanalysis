import discord
from discord.ext import commands
import pandas as pd
import os

# --- 設定 ---
TOKEN = os.getenv('DISCORD_TOKEN')
CSV_FILE = 'battle_logs.csv'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 画像が送られたら反応
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'heic']):
                # 受付確認のリアクション（恐竜研究所風）
                await message.add_reaction('🔍')
                
                # --- ここで本来は文字を読み取ります ---
                # 今はRenderが落ちないよう、仮のデータを1行足す機能にします
                # 準備ができたら、ここに「最強の読み取り機能」を合体させます！
                
                new_data = pd.DataFrame([{
                    '日時': message.created_at,
                    '味方1': '解析中', '味方2': '未実装', '味方3': '未実装',
                    '敵1': '不明', '敵2': '不明', '敵3': '不明',
                    '結果': '勝利'
                }])
                
                if os.path.exists(CSV_FILE):
                    df = pd.read_csv(CSV_FILE)
                    df = pd.concat([df, new_data], ignore_index=True)
                else:
                    df = new_data
                
                df.to_csv(CSV_FILE, index=False)
                
                # 完了のリアクション
                await message.remove_reaction('🔍', bot.user)
                await message.add_reaction('✅')

    await bot.process_commands(message)

bot.run(TOKEN)
