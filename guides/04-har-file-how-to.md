# 04 – HAR File: What / Why / How (10–15 mins)

**HAR** = HTTP Archive (JSON) of your browser’s network activity.

## Why we need it
To reverse‑engineer undocumented APIs → convert real calls into an OpenAPI spec.

## How to record (Chrome/Edge)
1. Open the website, press **F12** → **Network** tab
2. Check **Preserve log**
3. Perform the action you want (search, create, etc.)
4. Right‑click in the request list → **Save all as HAR**

## Sanitize (very important)
- Open HAR in an editor
- Replace tokens/cookies/emails with placeholders like `{{API_KEY}}`, `{{SESSION}}`
- Remove any PII

## Convert to OpenAPI (choose one)
- **Manual**: Identify base URL, paths, methods, headers, query/body, responses → write `openapi.yaml`
- **Scripted**: Use your script/tool to map HAR → OpenAPI skeleton, then edit
- **LLM‑assist**: Paste **sanitized** HAR chunks, ask for OpenAPI 3.0+ output, then validate

## Validate
- Run a validator (e.g. `openapi-spec-validator`, Swagger Editor)
- Use **Arazzo Runner** to call endpoints referenced in your workflow