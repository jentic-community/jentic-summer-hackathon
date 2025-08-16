# 02 – Standard Agent Quickstart (15 mins)

## Goal
Run a baseline agent locally and see it respond via CLI or Discord.

## Steps
```bash
# 1) Clone Standard Agent
git clone https://github.com/jentic/standard-agent.git
cd standard-agent
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2) Minimal run (CLI example)
cd examples/cli
cp .env.example .env   # fill your keys if needed
pip install -r requirements.txt
python main.py
````

Expected: the agent starts, you type a prompt, it reasons and replies.

## Discord example (optional)

```bash
cd examples/discord
cp .env.example .env   # fill DISCORD_TOKEN, JENTIC keys, etc.
pip install -r requirements.txt
python bot.py
```

If it connects and replies, you’re good. See the track for Discord-specific tasks.