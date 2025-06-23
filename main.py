import os
import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

connections = {}

@bot.event
async def on_ready():
    print(f"✅ {bot.user} جاهز!")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        vc = await ctx.author.voice.channel.connect()
        connections[ctx.guild.id] = vc
        await ctx.send("🎤 دخلت الروم الصوتي.")
    else:
        await ctx.send("❌ ادخل روم صوتي أولًا.")

@bot.command()
async def record(ctx):
    vc = connections.get(ctx.guild.id)
    if not vc:
        return await ctx.send("❌ لم يتم الاتصال بالروم بعد. استخدم !join أولا.")
    vc.start_recording(discord.sinks.WaveSink(), finished_recording, ctx.channel)
    await ctx.send("🔴 بدأ التسجيل!")

async def finished_recording(sink, channel):
    files = [discord.File(audio.file, f"{user}.{sink.encoding}") for user, audio in sink.audio_data.items()]
    await channel.send("✅ انتهى التسجيل:", files=files)
    vc = connections.pop(channel.guild.id, None)
    if vc:
        await vc.disconnect()

@bot.command()
async def stop(ctx):
    vc = connections.get(ctx.guild.id)
    if vc:
        vc.stop_recording()
        await ctx.send("🛑 تم إيقاف التسجيل")
    else:
        await ctx.send("❌ لا يوجد تسجيل جاري.")

@bot.command()
async def leave(ctx):
    vc = connections.get(ctx.guild.id)
    if vc:
        await vc.disconnect()
        connections.pop(ctx.guild.id, None)
        await ctx.send("📤 خرجت من الروم.")
    else:
        await ctx.send("❌ لست في الروم الصوتي.")

if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    bot.run(TOKEN)
