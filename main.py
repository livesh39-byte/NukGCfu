import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from aiohttp import web

async def health(request):
    return web.Response(text="Bot is online")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"Health server running on port {port}")

TOKEN = os.getenv("DISCORD_TOKEN")
MAX_MESSAGES = 100
INTERVAL = 1.0
USER_COOLDOWN = 1

import discord
from discord.ext import commands

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    intents=intents
)

user_last_used = {}
active_tests = set()
active_lock = asyncio.Lock()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Slash command sync failed: {e}")


@bot.tree.command(
name="spam",
description="GC FUCKING SPAMS "
)
@app_commands.describe(
message="Text to send",
count="Number of messages (1-100)"
)
@app_commands.choices(count=[
app_commands.Choice(name=str(n), value=n)
for n in range(1, MAX_MESSAGES + 1)
])

async def sendmsg(
    interaction: discord.Interaction,
    message: str,
    count: app_commands.Choice[int]
):
    if interaction.guild is None or interaction.channel is None:
        await interaction.response.send_message(
            "Use this command inside a server.",
            ephemeral=True
        )
        return

    # Baaki function ka code bhi yahin
    # 4 spaces indentation ke saath hoga


    now = time.monotonic()
    last_used = user_last_used.get(interaction.user.id, 0)
    remaining = USER_COOLDOWN - (now - last_used)

    if remaining > 0:
        await interaction.response.send_message(
            f"Please wait {int(remaining) + 1}s before trying again.",
            ephemeral=True
        )
        return

    channel_id = interaction.channel.id
    safe_message = message[:1800]

    user_last_used[interaction.user.id] = now

    await interaction.response.send_message(
        "Test started.",
        ephemeral=True
    )

    try:
        await interaction.channel.send(
            spam_message,
            allowed_mentions=discord.AllowedMentions.none()
        )
    except discord.Forbidden:
        print("Missing permission to send messages.")
    except discord.HTTPException as error:
        print(f"Discord API error: {error}")
    async with active_lock:  
        active_tests.discard(channel_id)

@bot.tree.command(
    name="botstatus",
    description="Check bot status"
)
async def botstatus(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Bot Status",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="Status",
        value="Online",
        inline=True
    )
    embed.add_field(
        name="Max messages per test",
        value=str(MAX_MESSAGES),
        inline=True
    )
    embed.add_field(
        name="Interval",
        value=f"{INTERVAL:g} second(s)",
        inline=True
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
)
    

async def main():
    await start_web_server()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is missing.")

    asyncio.run(main())
    
