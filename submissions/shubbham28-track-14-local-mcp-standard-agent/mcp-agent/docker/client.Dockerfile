FROM python:3.11-slim
WORKDIR /app
# TODO: Install client dependencies (e.g., streamlit).
COPY . /app

# Placeholder entrypoint to keep container alive during development.
CMD ["sleep", "infinity"]
