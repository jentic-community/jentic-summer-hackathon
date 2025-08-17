FROM python:3.11-slim
WORKDIR /app
# TODO: Install browser tooling (e.g., Playwright) and system deps.
COPY . /app

# Placeholder entrypoint to keep container alive during development.
CMD ["sleep", "infinity"]
