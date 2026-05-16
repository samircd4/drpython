# Use a multi-stage build to keep the final image small
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

# Set the working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
# We use --no-install-project to only install dependencies
RUN uv sync --frozen --no-install-project

# Now copy the rest of the application
COPY . .

# Final stage
FROM python:3.13-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy the application code
COPY . .

# Create a non-privileged user to run the app
RUN addgroup --system django && adduser --system --group django
USER django

# Expose the port the app runs on
EXPOSE 8000

# Run the application
# Note: Using manage.py runserver for now as gunicorn/uvicorn are not in dependencies.
# In production, you should add gunicorn to your pyproject.toml and use it here.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
