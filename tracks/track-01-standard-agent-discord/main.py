# import os
# from dotenv import load_dotenv

# load_dotenv()
# print("✅ Standard Agent Discord starter ready. Implement your bot here.")
# # Tip: pull in standard-agent client and discord.py (optional) if you extend.

# main.py
# Commands:
#  - !ping  -> "Pong!"
#  - !help  -> list commands
#  - !agent hello -> placeholder response (swap in Jentic SDK later)

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
JENTIC_KEY = os.getenv("JENTIC_AGENT_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

# Intents (make sure Message Content Intent is enabled in portal)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

def call_standard_agent(prompt: str) -> str:
    """
    Placeholder for Jentic Standard Agent.
    Replace this with the official SDK call when you have it, e.g.:
        from jentic import StandardAgent
        agent = StandardAgent(api_key=JENTIC_KEY, model=LLM_MODEL)
        return agent.run(prompt)
    """
    if not JENTIC_KEY:
        return "Standard Agent not configured (missing JENTIC_AGENT_API_KEY)."
    # Temporary success message so Phase 2 can pass
    if prompt.strip().lower() == "hello":
        return f"Hello from Standard Agent (mock). Model={LLM_MODEL or 'default'}"
    return f"(mock) You said: {prompt}"

@bot.event
async def on_ready():
    print(f"✅ Discord bot logged in as {bot.user} (ID: {bot.user.id})")
    if JENTIC_KEY:
        print("✅ Standard Agent initialized (mock). Replace with SDK when ready.")
    else:
        print("ℹ️  No JENTIC_AGENT_API_KEY found — !agent 會回覆未設定訊息。")
    print("🤖 Bot ready! Try '!ping' in Discord")

@bot.command(name="ping")
async def ping(ctx: commands.Context):
    await ctx.send("Pong!")

@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    lines = [
        "**Available Commands**",
        "`!ping` — Bot responds with `Pong!`",
        "`!help` — Shows available commands",
        "`!agent hello` — Bot uses Standard Agent to respond (mock until SDK wired)",
    ]
    await ctx.send("\n".join(lines))

@bot.command(name="agent")
async def agent_cmd(ctx: commands.Context, *, query: str = "hello"):
    await ctx.trigger_typing()
    reply = call_standard_agent(query)
    if len(reply) > 1800:
        reply = reply[:1800] + " …"
    await ctx.send(reply)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("Missing DISCORD_BOT_TOKEN in .env")
    bot.run(DISCORD_TOKEN)
