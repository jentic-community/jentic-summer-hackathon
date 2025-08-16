import os
import sys
import logging
import asyncio
from datetime import datetime
import discord
from discord.ext import commands

STANDARD_AGENT_PATH = os.path.join(os.path.dirname(__file__), "..", "standard-agent")
if STANDARD_AGENT_PATH not in sys.path:
    sys.path.insert(0, STANDARD_AGENT_PATH)

from config import get_config, BotConfig

try:
    config = get_config()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("Please check your .env file and ensure all required variables are set.")
    exit(1)

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format=config.log_format,
    datefmt=config.log_date_format,
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=config.bot_prefix,
    description=config.bot_description,
    intents=intents,
    help_command=None,
)

agent = None


async def initialize_agent():
    """Initialize the Standard Agent.

    Returns
    -------
    bool
        True if initialization successful, False otherwise.
    """
    global agent
    try:
        from agents.prebuilt import ReACTAgent

        os.environ["JENTIC_AGENT_API_KEY"] = config.jentic_agent_api_key
        if config.openai_api_key:
            os.environ["OPENAI_API_KEY"] = config.openai_api_key
        if config.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = config.anthropic_api_key
        if config.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = config.gemini_api_key
        os.environ["LLM_MODEL"] = config.llm_model

        agent = ReACTAgent(model=config.llm_model)
        logger.info(f"✅ Standard Agent initialized with model: {config.llm_model}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize Standard Agent: {e}")
        return False


@bot.event
async def on_ready():
    """Handle bot ready event."""
    logger.info(f"Bot connected successfully!")
    logger.info(f"Bot Name: {bot.user.name}")
    logger.info(f"Bot ID: {bot.user.id}")
    logger.info(f"Connected to {len(bot.guilds)} guild(s)")
    logger.info(f"Command prefix: {config.bot_prefix}")
    logger.info(f"Active LLM Provider: {config.get_active_llm_provider()}")
    logger.info(f"LLM Model: {config.llm_model}")

    if await initialize_agent():
        logger.info("🤖 Standard Agent ready!")
    else:
        logger.error("❌ Standard Agent initialization failed!")

    logger.info("Discord bot is ready and operational! 🚀")


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors.

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The command context.
    error : Exception
        The error that occurred.
    """
    if isinstance(error, commands.CommandNotFound):
        if config.enable_dm_commands or ctx.guild:
            await ctx.send(
                f"❌ Command not found. Use `{config.bot_prefix}help` to see available commands."
            )
        logger.warning(f"Unknown command attempted: {ctx.message.content}")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"❌ Missing required argument. Use `{config.bot_prefix}help {ctx.command}` for usage info."
        )
        logger.warning(f"Missing argument for command: {ctx.command}")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("❌ This command cannot be used in private messages.")
    else:
        await ctx.send("❌ An unexpected error occurred while processing your command.")
        logger.error(f"Unexpected error in command {ctx.command}: {error}")


@bot.command(name="ping")
async def ping_command(ctx):
    """Respond with bot latency and status.

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The command context.
    """
    latency = round(bot.latency * 1000)

    embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
    embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
    embed.add_field(name="Status", value="✅ Online", inline=True)
    embed.add_field(name="Agent", value="✅ Ready" if agent else "❌ Not Ready", inline=True)
    embed.timestamp = datetime.now(datetime.timezone.utc)

    await ctx.send(embed=embed)
    logger.info(f"Ping command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")


@bot.command(name="agent")
async def agent_command(ctx, *, query: str):
    """Execute a task using the Standard Agent.

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The command context.
    query : str
        The query to process through the agent.
    """
    if not agent:
        await ctx.send("❌ Standard Agent is not initialized. Please try again later.")
        return

    if not query.strip():
        await ctx.send("❌ Please provide a query for the agent to process.")
        return

    async with ctx.typing():
        try:
            logger.info(f"Processing agent query from {ctx.author}: {query[:100]}...")

            progress_msg = await ctx.send("🤖 Agent is thinking...")
            result = agent.solve(query)
            await progress_msg.edit(content="🤖 Agent is working...")

            if len(result) > 2000:
                chunks = [result[i : i + 1900] for i in range(0, len(result), 1900)]
                await progress_msg.delete()

                for i, chunk in enumerate(chunks):
                    embed = discord.Embed(
                        title=f"🤖 Agent Response (Part {i+1}/{len(chunks)})",
                        description=chunk,
                        color=discord.Color.blue(),
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="🤖 Agent Response", description=result, color=discord.Color.blue()
                )
                embed.set_footer(text=f"Query: {query[:100]}{'...' if len(query) > 100 else ''}")
                await progress_msg.edit(content="", embed=embed)

            logger.info(f"Successfully processed agent query for {ctx.author}")

        except Exception as e:
            logger.error(f"Error processing agent query: {e}")
            await ctx.send(
                f"❌ Sorry, I encountered an error while processing your request: {str(e)}"
            )


@bot.command(name="ask")
async def ask_command(ctx, *, question: str):
    """Ask the agent a question.

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The command context.
    question : str
        The question to ask the agent.
    """
    await agent_command(ctx, query=question)


@bot.command(name="help")
async def help_command(ctx, command_name=None):
    """Show available commands with descriptions.

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The command context.
    command_name : str, optional
        Specific command to get help for.
    """
    if command_name:
        command = bot.get_command(command_name)
        if command:
            embed = discord.Embed(
                title=f"Help: {config.bot_prefix}{command.name}",
                description=command.help or "No description available.",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Usage",
                value=f"`{config.bot_prefix}{command.name} {command.signature}`",
                inline=False,
            )
        else:
            embed = discord.Embed(
                title="Command Not Found",
                description=f"No command named `{command_name}` found.",
                color=discord.Color.red(),
            )
    else:
        embed = discord.Embed(
            title="🤖 AI Agent Discord Bot",
            description=config.bot_description,
            color=discord.Color.green(),
        )

        embed.add_field(
            name=f"{config.bot_prefix}ping",
            value="Check if the bot is responsive and show latency",
            inline=False,
        )
        embed.add_field(
            name=f"{config.bot_prefix}agent <query>",
            value="Execute a complex task using the Standard Agent",
            inline=False,
        )
        embed.add_field(
            name=f"{config.bot_prefix}ask <question>",
            value="Ask the agent a question (same as agent command)",
            inline=False,
        )
        embed.add_field(
            name=f"{config.bot_prefix}help [command]",
            value="Show this help message or get help for a specific command",
            inline=False,
        )
        embed.add_field(
            name=f"{config.bot_prefix}config",
            value="Show current bot configuration (admin only)",
            inline=False,
        )

        embed.add_field(
            name="🌟 Example Usage",
            value=f"`{config.bot_prefix}agent Find the latest AI papers on Figshare and summarize them`\n"
            f"`{config.bot_prefix}ask What is machine learning?`",
            inline=False,
        )

        embed.add_field(
            name="🔧 Configuration",
            value=f"Prefix: `{config.bot_prefix}`\nLLM: {config.llm_model}\nProvider: {config.get_active_llm_provider()}",
            inline=False,
        )

        embed.set_footer(
            text=f"Use {config.bot_prefix}help <command> for detailed information about a command"
        )

    await ctx.send(embed=embed)
    logger.info(f"Help command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")


@bot.command(name="config")
@commands.has_permissions(administrator=True)
async def config_command(ctx):
    """Show current bot configuration (admin only).

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The command context.
    """
    embed = discord.Embed(title="🔧 Bot Configuration", color=discord.Color.blue())

    embed.add_field(name="Prefix", value=config.bot_prefix, inline=True)
    embed.add_field(name="LLM Model", value=config.llm_model, inline=True)
    embed.add_field(
        name="LLM Provider", value=config.get_active_llm_provider() or "None", inline=True
    )
    embed.add_field(name="Log Level", value=config.log_level, inline=True)
    embed.add_field(
        name="DM Commands", value="✅" if config.enable_dm_commands else "❌", inline=True
    )
    embed.add_field(name="Command Timeout", value=f"{config.command_timeout}s", inline=True)
    embed.add_field(
        name="Agent Status", value="✅ Ready" if agent else "❌ Not Ready", inline=True
    )

    embed.timestamp = datetime.now(datetime.timezone.utc)
    embed.set_footer(text="Configuration loaded from .env file")

    await ctx.send(embed=embed)
    logger.info(f"Config command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")


async def main():
    """Start the Discord bot."""
    try:
        logger.info("Starting Discord bot...")
        logger.info(f"Bot prefix: {config.bot_prefix}")
        logger.info(f"Bot description: {config.bot_description}")
        logger.info(f"Log level: {config.log_level}")
        logger.info(f"LLM Model: {config.llm_model}")
        logger.info(f"Active LLM Provider: {config.get_active_llm_provider()}")

        async with bot:
            await bot.start(config.discord_bot_token)

    except discord.LoginFailure:
        logger.error("Failed to login to Discord. Please check your bot token.")
        return
    except Exception as e:
        logger.error(f"Unexpected error starting bot: {e}")
        return


if __name__ == "__main__":
    print("✅ Standard Agent Discord Bot Foundation with Pydantic Config")
    print("🚀 Starting Discord bot with Standard Agent integration...")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
        print("\n👋 Discord bot stopped gracefully")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Bot crashed: {e}")
