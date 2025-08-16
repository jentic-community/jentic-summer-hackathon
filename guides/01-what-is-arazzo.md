# 01 – What is Arazzo?

**Arazzo** is a spec (from the OpenAPI Initiative) for **executable workflows** that orchestrate API calls, data passing, and conditions in a declarative file (YAML/JSON). Think: “playbook the agent can run.”

- Human‑readable, LLM‑friendly
- Tells an engine **what** to do (order, inputs, outputs), not how to code it
- Perfect for repeatable, testable API workflows

**Jentic Arazzo Engine** is the home repo for open‑source Arazzo tools. Today it contains the **Runner**, which executes Arazzo workflows end‑to‑end.  
Repo: https://github.com/jentic/arazzo-engine  
Runner: https://github.com/jentic/arazzo-engine/tree/main/runner