import os
import random
import discord
from discord.ext import commands
from google import genai

# APIキーやトークンの設定（環境変数から読み込む想定）
# GEMINI_API_KEY と DISCORD_BOT_TOKEN をあらかじめ設定しておきます
client_genai = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

intents = discord.Intents.default()
intents.message_content = True  # メッセージの内容を読み取る権限
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"ログインしました: {bot.user.name}")


# 1. 映画の候補アンケートを自動で立てるコマンド
@bot.command(name="映画アンケート")
async def start_poll(ctx, movie1: str, movie2: str):
  embed = discord.Embed(
      title="🎬 今週の映画鑑賞会 候補投票！",
      description=(
          "観たい作品にリアクション（スタンプ）を押してね！\n\n1️⃣"
          f" {movie1}\n2️⃣ {movie2}"
      ),
      color=0x3498DB,
  )
  message = await ctx.send(embed=embed)
  await message.add_reaction("1️⃣")
  await message.add_reaction("2️⃣")


# 2. 鑑賞会の告知をするコマンド
@bot.command(name="映画告知")
async def announce_movie(ctx, title: str, date_time: str, url: str):
  embed = discord.Embed(
      title="🍿 映画鑑賞会のお知らせ",
      description=f"今週もやるよー！みんな集まれ！",
      color=0xE74C3C,
  )
  embed.add_field(name="上映作品", value=title, inline=False)
  embed.add_field(name="日時", value=date_time, inline=False)
  embed.add_field(name="Sync-tube部屋", value=url, inline=False)
  await ctx.send(embed=embed)


# 3. チャットが流れたときにGeminiが自動で相槌を打って盛り上げる機能
@bot.event
async def on_message(message):
  # Bot自身の発言には反応しない
  if message.author == bot.user:
    return

  # 「!」から始まるコマンドは個別の処理に任せる
  await bot.process_commands(message)

  # 特定のチャンネル（例: #映画鑑賞会チャット）での発言に反応させる場合
  # if message.channel.name == "映画鑑賞会チャット":

  # ランダムな確率（例: 3回に1回くらい）で相槌を打つ、または常に反応させるなど調整可能
  if random.random() < 0.4:  -  # 40%の確率で返事をする
    try:
      # Gemini APIを使って、チャットの盛り上げ役として返信を生成
      prompt = (
          "あなたはDiscordの映画鑑賞会をワイワイ盛り上げるフレンドリーなボットです。"
          "ユーザーの以下の発言に対して、短く楽しく相槌を打ったり、ツッコミを入れたりしてください。\n\nユーザーの発言:"
          f" {message.content}"
      )

      response = client_genai.models.generate_content(
          model="gemini-2.5-flash", contents=prompt
      )

      if response.text:
        await message.reply(response.text)

    except Exception as e:
      print(f"エラー: {e}")


# Botの起動
# bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
