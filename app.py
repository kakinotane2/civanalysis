import discord
from discord.ext import commands
import google.generativeai as genai
import os
import aiohttp

# 【ここが重要】「秘密のポケット(Render)」から値を受け取る設定（4行）
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot or not message.attachments:
        return
    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg']):
            await message.channel.send("画像を解析中...")
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    image_data = await resp.read()
            
            response = model.generate_content([
                "この画像はゲームの対戦結果画面です。左側の指揮官名、右側の指揮官名、勝利か敗北かを「名前,名前,勝利」の形式で答えて。",
                {"mime_type": "image/jpeg", "data": image_data}
            ])
            await message.channel.send(f"【解析結果】\n{response.text}")

bot.run(DISCORD_TOKEN)

