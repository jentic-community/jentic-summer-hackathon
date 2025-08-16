# 05 – OpenAPI Validation & Quality

- [ ] `openapi: "3.x"` and top fields (`info`, `servers`)
- [ ] Auth documented (API key, OAuth2, etc.)
- [ ] Each operation has:
  - [ ] Path + method
  - [ ] Request parameters (query/path/header) typed
  - [ ] Request body schema (if applicable)
  - [ ] Response `200` with schema + examples
  - [ ] Error responses (`4xx/5xx`) with at least minimal schema
- [ ] Pagination / rate limits explained (if applicable)
- [ ] Descriptions are clear, no placeholders
- [ ] Example curl or request bodies for the **happy path**
- [ ] Spec passes a linter/validator