# main.py — Phase 4.4
# /agent -> tools (Giphy / Wikimedia) via Jentic
# /ai    -> Gemini (google-generativeai) with per-channel memory
#
# Improvements in 4.4:
# - More robust tool picking for /agent:
#   * Score-based matching (keywords + schema shape)
#   * Fallbacks if search results don't contain obvious "giphy"/"wiki" strings
# - Clearer error messages
# - tool param remains required (auto|giphy|wiki). If you want it optional, say the word.

import os
import asyncio
from collections import defaultdict, deque
from typing import Deque, Dict, List, Optional

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Jentic SDK (client reads JENTIC_AGENT_API_KEY from env)
from jentic import Jentic, SearchRequest, LoadRequest, ExecutionRequest  # type: ignore

# ---------- Try import Gemini (optional) ----------
_GEMINI_AVAILABLE = True
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    _GEMINI_AVAILABLE = False

# ---------- ENV ----------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
JENTIC_KEY = os.getenv("JENTIC_AGENT_API_KEY", "")  # sanity check only; SDK reads env
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")

# Hint used only to bias Jentic search text (does not affect /ai)
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-pro")

# Optional: direct tool IDs to skip search (stable/fast path)
GIPHY_TOOL_ID = os.getenv("JENTIC_GIPHY_TOOL_ID", "").strip()
WIKI_TOOL_ID = os.getenv("JENTIC_WIKI_TOOL_ID", "").strip()

BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
BOT_DESCRIPTION = os.getenv("BOT_DESCRIPTION", "AI Agent Discord Bot")

# Gemini credentials and model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # e.g., "gemini-1.5-flash" or "gemini-1.5-pro"

# ---------- BOT ----------
intents = discord.Intents.default()  # Slash commands don't need message content intent
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# Per-channel conversation memory (bounded FIFO)
MAX_HISTORY = 6
conversation_history: Dict[int, Deque[dict]] = defaultdict(lambda: deque(maxlen=MAX_HISTORY))

# Jentic client (lazy init; SDK reads key from env)
jentic_client: Optional[Jentic] = None

# Gemini model (lazy config)
_gemini_model = None


# ---------- UTIL (for tools) ----------
def format_required_inputs(input_schema) -> str:
    """Render tool_info.inputs into a concise list of required fields for user-facing errors."""
    try:
        props = (input_schema or {}).get("properties", {}) or {}
        required = (input_schema or {}).get("required", []) or []
        if not props and not required:
            return "No specific inputs required."
        lines = [f"- {k} ({props.get(k, {}).get('type', 'any')})" for k in required]
        return "Required fields:\n" + ("\n".join(lines) if lines else "No required fields (all optional).")
    except Exception:
        return "Unable to read input schema."


def _coerce_schema_dict(schema):
    """Return a plain dict from pydantic/attrs/dict-like input schema objects."""
    if schema is None:
        return {}
    for attr in ("model_dump", "dict"):
        if hasattr(schema, attr):
            try:
                return getattr(schema, attr)()
            except Exception:
                pass
    try:
        return dict(schema)
    except Exception:
        return {}


def _text_blob(info) -> str:
    """Concatenate likely metadata for keyword checks."""
    parts = []
    for attr in ("name", "title", "description", "summary"):
        if hasattr(info, attr):
            try:
                v = getattr(info, attr)
                if isinstance(v, str):
                    parts.append(v)
            except Exception:
                pass
    try:
        parts.append(str(info))
    except Exception:
        pass
    return " ".join(parts).lower()


def _build_inputs_for_mode(user_text: str, schema: dict, mode: str, history: List[dict]) -> dict:
    """Map user_text into the right schema fields based on the mode and available properties."""
    props = schema.get("properties", {}) or {}

    # Giphy: prefer q -> query/term/keyword/search
    if mode == "giphy":
        for key in ("q", "query", "term", "keyword", "search"):
            if key in props:
                return {key: user_text}
        req = schema.get("required", []) or []
        if len(req) == 1 and (props.get(req[0]) or {}).get("type") in (None, "string"):
            return {req[0]: user_text}
        return {}

    # Wiki: prefer title -> query -> search -> page
    if mode == "wiki":
        for key in ("title", "query", "search", "page"):
            if key in props:
                return {key: user_text}
        req = schema.get("required", []) or []
        if len(req) == 1 and (props.get(req[0]) or {}).get("type") in (None, "string"):
            return {req[0]: user_text}
        return {}

    return {}


def _pick_tool_id_for_mode(tool_info_map: dict, mode: str) -> Optional[str]:
    """Pick a tool id that matches the requested mode via metadata+schema score; includes fallbacks."""
    prepared = {tid: _coerce_schema_dict(getattr(info, "inputs", {})) for tid, info in tool_info_map.items()}

    def score_giphy(tid) -> int:
        info = tool_info_map[tid]
        schema = prepared[tid]
        props = schema.get("properties", {}) or {}
        blob = _text_blob(info)
        s = 0
        if any(k in props for k in ("q", "query", "term", "keyword", "search")):
            s += 2
        if any(w in blob for w in ("giphy", "gif", "sticker")):
            s += 4
        if any(w in blob for w in ("image", "media")):
            s += 1
        return s

    def score_wiki(tid) -> int:
        info = tool_info_map[tid]
        schema = prepared[tid]
        props = schema.get("properties", {}) or {}
        blob = _text_blob(info)
        s = 0
        if any(k in props for k in ("title", "page", "query", "search")):
            s += 2
        if any(w in blob for w in ("wiki", "wikipedia", "wikimedia")):
            s += 4
        if "extract" in blob or "summary" in blob:
            s += 1
        return s

    if not tool_info_map:
        return None

    # 1) Score and pick the best match
    scorer = score_giphy if mode == "giphy" else score_wiki
    best_id = None
    best_score = -1
    for tid in tool_info_map.keys():
        try:
            sc = scorer(tid)
            if sc > best_score:
                best_score = sc
                best_id = tid
        except Exception:
            continue

    # 2) If score > 0, accept; else try schema-only fallback
    if best_id and best_score > 0:
        return best_id

    # 3) Fallbacks: pick any tool that looks compatible by schema shape
    if mode == "giphy":
        for tid, schema in prepared.items():
            props = schema.get("properties", {}) or {}
            if any(k in props for k in ("q", "query", "term", "keyword", "search")):
                return tid
    else:  # wiki
        for tid, schema in prepared.items():
            props = schema.get("properties", {}) or {}
            if any(k in props for k in ("title", "page", "query", "search")):
                return tid

    # 4) Last resort: give up (caller will show a helpful message)
    return None


async def _execute_by_tool_id(client: Jentic, tool_id: str, user_text: str, mode: str, history: List[dict]) -> str:
    """Load tool, adapt inputs per schema, execute, and normalize the result into a short string."""
    load_res = await client.load(LoadRequest(ids=[tool_id]))
    info = (load_res.tool_info or {}).get(tool_id)
    if not info:
        return "Configured tool not found. Please verify the tool ID and agent permissions."

    schema = _coerce_schema_dict(getattr(info, "inputs", {}))
    inputs = _build_inputs_for_mode(user_text, schema, mode, history)

    required = (schema or {}).get("required", []) or []
    missing = [k for k in required if k not in inputs]
    if missing:
        pretty = format_required_inputs(schema)
        return (
            "This action needs more specific parameters.\n"
            f"{pretty}\n\n"
            "Tip: try a clearer phrasing."
        )

    exec_res = await client.execute(ExecutionRequest(id=tool_id, inputs=inputs))
    data = getattr(exec_res, "result", None) or getattr(exec_res, "data", None) or exec_res

    # Try to return human-friendly text or a likely URL
    if isinstance(data, dict):
        for k in ("output", "message", "text", "summary", "result", "extract", "description"):
            if isinstance(data.get(k), str) and data[k].strip():
                return data[k][:1900]

        # Fallback: search for a URL within nested structures (useful for media tools)
        def _find_url(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    u = _find_url(v)
                    if u:
                        return u
            elif isinstance(obj, list):
                for v in obj:
                    u = _find_url(v)
                    if u:
                        return u
            elif isinstance(obj, str) and obj.startswith("http"):
                return obj
            return None

        url = _find_url(data)
        if url:
            return url[:1900]
        return str(data)[:1900]
    return str(data)[:1900]


async def _search_load_execute(query: str, mode: str, history: List[dict]) -> str:
    """
    For Giphy/Wiki:
      - If tool ID env vars are present, execute directly.
      - Else: Search -> Load -> Pick -> Execute (with robust fallbacks).
    """
    if not JENTIC_KEY:
        raise ValueError("Missing JENTIC_AGENT_API_KEY")

    global jentic_client
    if jentic_client is None:
        jentic_client = Jentic()  # SDK auto-reads the API key from env

    # Direct tool-id path
    if mode == "giphy" and GIPHY_TOOL_ID:
        return await _execute_by_tool_id(jentic_client, GIPHY_TOOL_ID, query, mode, history)
    if mode == "wiki" and WIKI_TOOL_ID:
        return await _execute_by_tool_id(jentic_client, WIKI_TOOL_ID, query, mode, history)

    # Otherwise: search with a biased query to prefer the right tool type
    search_q = "giphy gif search: " + query if mode == "giphy" else "wikipedia/wikimedia summary: " + query
    search_res = await jentic_client.search(SearchRequest(query=search_q))
    if not getattr(search_res, "results", None):
        return (
            "No tools were found via Jentic search. "
            "Tip: set JENTIC_GIPHY_TOOL_ID / JENTIC_WIKI_TOOL_ID in your .env to skip search."
        )

    top_ids = [r.id for r in search_res.results[:6]]
    load_res = await jentic_client.load(LoadRequest(ids=top_ids))
    tool_info_map = load_res.tool_info or {}
    picked_id = _pick_tool_id_for_mode(tool_info_map, mode)
    if not picked_id:
        return (
            "Could not find a matching tool for this query.\n"
            "Tip: add the tool to your Jentic Agent **or** set the env var "
            "`JENTIC_GIPHY_TOOL_ID` / `JENTIC_WIKI_TOOL_ID` to a known tool id."
        )

    return await _execute_by_tool_id(jentic_client, picked_id, query, mode, history)


# ---------- GEMINI HELPERS ----------
def _ensure_gemini_model():
    """Configure and cache a Gemini model instance according to env settings."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model

    if not _GEMINI_AVAILABLE:
        raise RuntimeError("google-generativeai is not installed. Run: pip install google-generativeai")
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY in environment.")

    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_model = genai.GenerativeModel(GEMINI_MODEL)  # Use model name from env
    return _gemini_model


def _gemini_history_from_channel(history_deque: List[dict]) -> List[dict]:
    """Transform our minimal history into Gemini chat history format."""
    hist = []
    for t in history_deque[-3:]:
        u = t.get("user")
        b = t.get("bot")
        if u:
            hist.append({"role": "user", "parts": [u]})
        if b:
            hist.append({"role": "model", "parts": [b]})
    return hist


def _gemini_generate_sync(prompt: str, history: List[dict]) -> str:
    """Blocking Gemini call; intended to run in a worker thread via asyncio.to_thread."""
    model = _ensure_gemini_model()
    chat = model.start_chat(history=_gemini_history_from_channel(history))
    resp = chat.send_message(prompt)
    text = getattr(resp, "text", None) or str(resp)
    return (text or "").strip()[:1900] or "No response."


# ---------- LIFECYCLE ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    if bot.guilds:
        print("🔎 Guilds I can see:")
        for g in bot.guilds:
            print(f"- {g.name} (ID: {g.id})")
    try:
        if DEV_GUILD_ID:
            guild = discord.Object(id=int(DEV_GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            cmds = await bot.tree.sync(guild=guild)
            print(f"✅ Synced {len(cmds)} slash commands to guild {DEV_GUILD_ID}")
        else:
            cmds = await bot.tree.sync()
            print(f"✅ Synced {len(cmds)} global slash commands")
    except Exception as e:
        print(f"⚠️ Slash command sync failed: {e}")


# ---------- GLOBAL ERROR HANDLER ----------
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Return user-friendly error messages for common slash command issues."""
    msg = "⚠️ Something went wrong. Please try again."
    if isinstance(error, app_commands.CommandOnCooldown):
        msg = f"⏳ You're going too fast. Try again in {error.retry_after:.1f}s."
    elif isinstance(error, app_commands.MissingPermissions):
        msg = "🔒 You don't have permission to use this command."
    elif isinstance(error, app_commands.CommandInvokeError):
        inner = getattr(error, "original", None)
        if isinstance(inner, asyncio.TimeoutError):
            msg = "⌛ The agent took too long to respond. Try a shorter request."
        elif isinstance(inner, ValueError) and "JENTIC_AGENT_API_KEY" in str(inner):
            msg = "⚙️ Jentic is not configured. Please set JENTIC_AGENT_API_KEY in `.env`."
        else:
            msg = f"⚠️ Error: {inner or error}"
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass


# ---------- COMMANDS ----------
@bot.tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


@bot.tree.command(name="help", description="Show categorized commands and usage")
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Bot Help",
        description="Commands overview",
        color=0x3498DB,
    )
    embed.add_field(
        name="General",
        value="/ping — latency check\n/help — this help message",
        inline=False,
    )
    embed.add_field(
        name="Agent (Tools)",
        value=(
            "/agent <tool> <query>\n"
            "  • tool = auto | giphy | wiki\n"
            "  • auto: 'gif/動圖' -> Giphy；'wiki/wikipedia/維基' -> Wikimedia\n"
        ),
        inline=False,
    )
    embed.add_field(
        name="AI (Gemini)",
        value="/ai <prompt> — chat via Gemini",
        inline=False,
    )
    embed.add_field(
        name="Context",
        value="/clear_context — clear conversation memory for this channel",
        inline=False,
    )
    embed.set_footer(text="Tip: /ai uses GEMINI_API_KEY & GEMINI_MODEL; /agent uses Jentic tools.")
    await interaction.response.send_message(embed=embed)


# ---- /agent: tool runner (Giphy/Wiki) ----
@bot.tree.command(name="agent", description="Run tools: Giphy or Wikimedia via Jentic")
@app_commands.describe(
    tool="auto | giphy | wiki",
    query="Your request (e.g., cat gif ; Alan Turing ; 維基 史蒂夫喬布斯)"
)
@app_commands.choices(
    tool=[
        app_commands.Choice(name="auto", value="auto"),
        app_commands.Choice(name="Giphy", value="giphy"),
        app_commands.Choice(name="Wikimedia", value="wiki"),
    ]
)
async def slash_agent(interaction: discord.Interaction, tool: app_commands.Choice[str], query: str):
    await interaction.response.defer(thinking=True)

    # Decide routing mode
    choice = tool.value
    q_lower = query.lower()
    if choice == "auto":
        if ("gif" in q_lower) or ("動圖" in query):
            mode = "giphy"
        elif ("wiki" in q_lower) or ("wikipedia" in q_lower) or ("維基" in query):
            mode = "wiki"
        else:
            await interaction.followup.send(
                "請選擇工具（giphy/wiki），或在 Auto 模式下包含關鍵字：`gif/動圖` 或 `wiki/wikipedia/維基`。",
                ephemeral=True
            )
            return
    else:
        mode = choice  # 'giphy' or 'wiki'

    history = list(conversation_history[interaction.channel_id])  # snapshot
    try:
        answer = await _search_load_execute(query, mode, history)
    except Exception as e:
        try:
            await interaction.followup.send(f"⚠️ Agent error: {e}", ephemeral=True)
        except Exception:
            pass
        return

    conversation_history[interaction.channel_id].append({"user": f"[{mode}] {query}", "bot": answer})

    title = "🖼️ Giphy" if mode == "giphy" else "📚 Wikimedia"
    color = 0x9B59B6 if mode == "giphy" else 0xF1C40F
    embed = discord.Embed(
        title=title,
        description=answer if len(answer) < 2000 else (answer[:1990] + " …"),
        color=color,
    )
    embed.add_field(name="History size", value=str(len(conversation_history[interaction.channel_id])), inline=True)
    await interaction.followup.send(embed=embed)


# ---- /ai: Gemini chat ----
@bot.tree.command(name="ai", description="Chat with Gemini (uses GEMINI_API_KEY)")
@app_commands.describe(prompt="Your prompt (e.g., Explain transformers; 幫我寫一段說明)")
async def slash_ai(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)

    history = list(conversation_history[interaction.channel_id])  # snapshot
    try:
        # Run blocking Gemini call in a worker thread to keep the event loop responsive
        answer = await asyncio.to_thread(_gemini_generate_sync, prompt, history)
    except Exception as e:
        err = str(e)
        if "google-generativeai" in err or "not installed" in err:
            msg = "需要安裝套件：`pip install google-generativeai`。"
        elif "GEMINI_API_KEY" in err:
            msg = "未找到 `GEMINI_API_KEY`，請在 `.env` 設定。"
        else:
            msg = f"⚠️ Gemini 呼叫錯誤：{err}"
        try:
            await interaction.followup.send(msg, ephemeral=True)
        except Exception:
            pass
        return

    conversation_history[interaction.channel_id].append({"user": f"[ai] {prompt}", "bot": answer})

    embed = discord.Embed(
        title="🤖 Gemini",
        description=answer if len(answer) < 2000 else (answer[:1990] + " …"),
        color=0x2ECC71,
    )
    embed.add_field(name="History size", value=str(len(conversation_history[interaction.channel_id])), inline=True)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="clear_context", description="Clear conversation history in this channel")
async def slash_clear_context(interaction: discord.Interaction):
    conversation_history.pop(interaction.channel_id, None)
    await interaction.response.send_message("🧹 Context cleared for this channel.", ephemeral=True)


# ---------- MAIN ----------
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("Missing DISCORD_BOT_TOKEN in `.env`")
    bot.run(DISCORD_TOKEN)
