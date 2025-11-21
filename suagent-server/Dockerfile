# suagent-server API service
FROM python:3.13.9-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# System dependencies for Playwright + curl used by healthchecks
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglu1-mesa \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    wget \
    xdg-utils \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Playwright 1.56.0 and browser dependencies first
RUN pip install --no-cache-dir "playwright==1.56.0" \
 && python -m playwright install-deps chromium

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir --upgrade "playwright==1.56.0" \
 && python -m playwright install chromium

COPY . .

EXPOSE 8000
CMD ["python", "start_server.py"]
