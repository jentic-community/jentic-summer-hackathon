# HAR → OpenAPI — Project Delivery

**Prepared for:** Jentic (track-02)

**Contributors:** Sanidhya Arora, Conor McLeod, Maccollins Obikiaku and Thomas Nolan

---

## Executive summary

This repository contains a finished, production-quality deliverable that reverse-engineers an undocumented API using browser HAR captures and produces a validated OpenAPI 3.x specification. The deliverable includes sanitized HAR captures, an OpenAPI spec with representative schemas and examples, test workflows, analysis tooling, and documentation outlining our process and results.

This document summarizes what we built, how to review it in a pull request, and how to run validation and tests locally.

---

## Highlights / Key outcomes

* Complete OpenAPI 3.x specification for the discovered API (`specs/api-spec.yaml`).
* Sanitized evidence of discovery (`captures/sanitized-capture.har`) and original capture (`captures/raw-capture.har`).
* Test workflow for automated validation and execution (`specs/test-workflow.arazzo.yaml`).
* Analysis tooling enabling repeatable HAR → OpenAPI conversion (`tools/har_analyzer.py`, `tools/sanitizer.py`, `tools/validator.py`).
* Examples and documentation demonstrating how to call endpoints and interpret responses (`examples/sample-requests.md`, `examples/response-samples/`).

---

## What we did (step-by-step)

1. **Capture**

   * Performed a controlled browser session to trigger API traffic and saved a full HAR (`captures/raw-capture.har`).
2. **Analyze**

   * Used `tools/har_analyzer.py` to parse the HAR and infer endpoints, parameters, response payloads, and authentication patterns.
3. **Sanitize**

   * Removed sensitive tokens, user identifiers, and PII using `tools/sanitizer.py` and reviewed the result manually. Sanitized output: `captures/sanitized-capture.har`.
4. **Model & Author**

   * Created a clear OpenAPI 3.x spec with well-named operationIds, request/response schemas in `components.schemas`, and representative examples: `specs/api-spec.yaml`.
5. **Validate**

   * Performed automated validation (OpenAPI validator + custom checks in `tools/validator.py`) and manual smoke tests using the Arazzo test workflow: `specs/test-workflow.arazzo.yaml`.
6. **Document**

   * Wrote the discovery report and README that explain methodology, assumptions, limitations, and how to reproduce the results.

---

## File structure

```
har-to-openapi-project/
├── README.md                         # Project overview & contributor-facing README (this file)
├── discovery-report.md               # Detailed analysis, findings, and design decisions
├── captures/
│   ├── raw-capture.har               # Original HAR file (kept for traceability)
│   └── sanitized-capture.har         # Sanitized HAR used to derive spec
├── specs/
│   ├── api-spec.yaml                 # Final OpenAPI 3.x specification (primary deliverable)
│   └── test-workflow.arazzo.yaml     # Test workflow showing example use-cases
├── tools/
│   ├── har_analyzer.py               # Tools to extract endpoints and generate skeletons
│   ├── sanitizer.py                  # Tools to remove PII and secrets from HAR
│   └── validator.py                  # Validation helpers and custom checks
└── examples/
    ├── sample-requests.md            # Example API calls and short how-to
    └── response-samples/             # Representative response JSON examples
```

---

## How to review (PR checklist)

Use this checklist when reviewing the pull request:

* [ ] **Spec presence**: `specs/api-spec.yaml` exists and is the authoritative spec.
* [ ] **Sanitization**: `captures/sanitized-capture.har` contains no tokens, auth headers, emails, or PII.
* [ ] **Validation**: `tools/validator.py` reports no blocking errors; `openapi_spec_validator` returns success.
* [ ] **Examples**: `examples/sample-requests.md` includes at least one successful request and response example per major endpoint.
* [ ] **Operation coverage**: Spec covers the primary flows discovered during capture (search/list/detail, pagination, filters where applicable).
* [ ] **Documentation**: `discovery-report.md` documents assumptions, edge cases, and any unsupported behaviors.
* [ ] **Tests**: `specs/test-workflow.arazzo.yaml` runs without requiring secrets (or with mocked auth) and demonstrates key operations.

When approving, leave notes about any missing examples or suggested schema improvements.

---

## How to run locally (quick start)

```bash
# 1. clone & enter repo
git clone <this-repo-url>
cd har-to-openapi-project

# 2. create virtualenv and install dependencies
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. run validator on spec
python tools/validator.py specs/api-spec.yaml
# or use openapi_spec_validator directly
python -c "from openapi_spec_validator import validate_spec; import yaml; print('valid' if validate_spec(yaml.safe_load(open('specs/api-spec.yaml')) ) is None else 'invalid')"

# 4. run the analyzer (optional repeatable step)
python tools/har_analyzer.py captures/sanitized-capture.har --output specs/api-skeleton.yaml

# 5. run the test workflow (Arazzo runner)
arazzo-runner execute-workflow --workflow-path specs/test-workflow.arazzo.yaml --openapi-path specs/api-spec.yaml
```

> Note: tests are designed to run against a mocked or staging server if the real API is protected. Do not add real secrets to the repository.

---

## Validation & security

* The OpenAPI spec was validated against OpenAPI 3.x rules and a set of custom checks (see `tools/validator.py`).
* All captured HAR files checked for PII and authentication secrets. Sanitization is automated and followed by a manual review.
* Example requests use sanitized or placeholder values. Any required secrets for integration tests should be provided via environment variables in CI only and never checked in.

---

## Known limitations & assumptions

* The spec targets the API surface observed during the capture session. Unobserved endpoints or optional parameters may not be modeled.
* Authentication flows that require interactive login were recorded only to the extent visible in the HAR; full OAuth flows may require additional tests to document fully.
* Rate-limit behavior, long-polling, and other operational concerns were not exhaustively tested.

---

---

## Contact & support

If reviewers or maintainers have questions, reach out to the contributors in the PR comments or ping the project lead: **Sanidhya**.

---

