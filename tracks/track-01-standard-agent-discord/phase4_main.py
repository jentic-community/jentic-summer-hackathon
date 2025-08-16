# phase4_main.py

import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
JENTIC_KEY = os.getenv("JENTIC_AGENT_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Keep simple per-channel conversation context
conversation_history = defaultdict(list)

def call_standard_agent(prompt: str, history=None) -> str:
    """
    Placeholder for Jentic Standard Agent with history context.
    Replace with SDK when ready.
    """
    if not JENTIC_KEY:
        raise ValueError("Missing JENTIC_AGENT_API_KEY")
    context_text = f"[Context: {history}]" if history else ""
    if prompt.strip().lower() == "hello":
        return f"Hello from Standard Agent (mock). Model={LLM_MODEL or 'default'} {context_text}"
    return f"(mock) You said: {prompt} {context_text}"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"⚠️ Slash command sync failed: {e}")

# -------- Commands --------

@bot.tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.tree.command(name="help", description="Show categorized commands")
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Help", description="Available Commands", color=0x3498db)
    embed.add_field(name="General", value="/ping, /help", inline=False)
    embed.add_field(name="Agent", value="/agent <query>, /clear_context", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="agent", description="Ask the Standard Agent (with context)")
@app_commands.describe(query="Your input to the agent")
async def slash_agent(interaction: discord.Interaction, query: str):
    try:
        await interaction.response.defer(thinking=True)
        channel_id = interaction.channel_id
        history = conversation_history[channel_id]
        reply = call_standard_agent(query, history)
        # store in history
        conversation_history[channel_id].append({"user": query, "bot": reply})
        embed = discord.Embed(title="🤖 Agent Reply", description=reply, color=0x2ecc71)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {e}")

@bot.tree.command(name="clear_context", description="Clear conversation history in this channel")
async def slash_clear(interaction: discord.Interaction):
    conversation_history.pop(interaction.channel_id, None)
    await interaction.response.send_message("🧹 Conversation history cleared!")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("Missing DISCORD_BOT_TOKEN in .env")
    bot.run(DISCORD_TOKEN)
