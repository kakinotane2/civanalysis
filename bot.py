import discord
from discord.ext import commands
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
import aiohttp

# ================= 自分で設定する部分 =================

# 1. Discord Botのトークン
DISCORD_TOKEN = 'あなたのDiscordトークン'

# 2. Google AI (Gemini) APIキー
GEMINI_API_KEY = 'AIzaSyArpqCFHQgO5-WTrrG4UbAS9fZzWvrLl8I'

# 3. スプレッドシートの名前
SHEET_NAME = 'シヴ編成分析所'

# ===================================================

# Geminiの設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Discordの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# スプレッドシートへの書き込み関数
async def update_sheet(commander1, commander2, result):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # ここは以前作ったJSONファイル名に書き換えてください
        creds = ServiceAccountCredentials.from_json_keyfile_name('service-account.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).get_worksheet(0)
        sheet.append_row([commander1, commander2, result])
        return True
    except Exception as e:
        print(f"シート更新エラー: {e}")
        return False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg']):
                await message.channel.send("画像を解析中...（APIキー方式で実行中！）")
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        image_data = await resp.read()

                # Geminiで画像を解析
                response = model.generate_content([
                    "この画像はゲームの対戦結果画面です。左側の指揮官名、右側の指揮官名、そして勝利か敗北かを以下の形式で答えてください。例：アーサー,ゼノビア,勝利",
                    {"mime_type": "image/jpeg", "data": image_data}
                ])
                
                res_text = response.text.strip()
                await message.channel.send(f"解析結果: {res_text}")
                
                # スプレッドシートへ（カンマ区切りを想定）
                try:
                    c1, c2, res = res_text.split(',')
                    success = await update_sheet(c1, c2, res)
                    if success:
                        await message.channel.send("スプレッドシートに記録しました！")
                except:
                    await message.channel.send("解析に失敗しました。もう一度はっきりした画像を送ってください。")

    await bot.process_commands(message)

bot.run(MTQ4MTI2MzMwNDEwNTI2NzI0MQ.GlW4qi.msHp8VmJXaNR9O-U6cgH4rpsXnVS_IcLUJDRM8)
