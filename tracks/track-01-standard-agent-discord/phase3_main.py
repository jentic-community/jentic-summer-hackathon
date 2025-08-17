# phase3_main.py

import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load environment
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
JENTIC_KEY = os.getenv("JENTIC_AGENT_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def call_standard_agent(prompt: str) -> str:
    """
    Placeholder for Jentic Standard Agent.
    Replace with real SDK when available.
    """
    if not JENTIC_KEY:
        raise ValueError("Missing JENTIC_AGENT_API_KEY")
    if prompt.strip().lower() == "hello":
        return f"Hello from Standard Agent (mock). Model={LLM_MODEL or 'default'}"
    return f"(mock) You said: {prompt}"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"⚠️ Slash command sync failed: {e}")

# --------- Slash Commands ---------

@bot.tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.tree.command(name="help", description="Show available commands")
async def slash_help(interaction: discord.Interaction):
    text = (
        "**Available Commands**\n"
        "/ping — Bot responds with Pong!\n"
        "/help — Show this message\n"
        "/agent <query> — Ask Standard Agent (mock until SDK wired)"
    )
    await interaction.response.send_message(text)

@bot.tree.command(name="agent", description="Ask the Standard Agent")
@app_commands.describe(query="Your input to the agent")
async def slash_agent(interaction: discord.Interaction, query: str):
    try:
        # progress indicator
        await interaction.response.defer(thinking=True)
        reply = call_standard_agent(query)
        await interaction.followup.send(reply)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {e}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("Missing DISCORD_BOT_TOKEN in .env")
    bot.run(DISCORD_TOKEN)
