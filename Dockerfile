FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

# Verify uv installation
RUN which uv && uv --version

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies with verbose output
RUN uv sync --frozen --no-dev --verbose

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Start application
CMD ["uv", "run", "adk", "web", "--host", "0.0.0.0", "--port", "8000"]