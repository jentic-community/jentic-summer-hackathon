03 – Arazzo Runner Quickstart (15–20 mins)

## Goal
Execute a tiny Arazzo workflow using the Runner.

## Steps
```bash
# 1) Clone Arazzo Engine and install runner
git clone https://github.com/jentic/arazzo-engine.git
cd arazzo-engine/runner
python -m venv .venv && source .venv/bin/activate
pip install -e .    # installs runner

# 2) Run hello-world workflow
cd examples/hello-world     # if not present, use the track example provided
cp .env.example .env        # if required by the example
arazzo-runner run hello.yaml
# or: python -m arazzo_runner run hello.yaml
````

Expected: you see requests executing and a final result printed.

**Common issues**

* Missing `.env` variables → check example README
* Rate limits → try a different public API or add keys
* YAML indentation → validate with `yamllint` or a YAML plugin