# 1. Start with a lightweight Debian-based Python image
FROM python:3.11-slim-bullseye

# 2. Install the system-level CBC solver required by PuLP
RUN apt-get update && apt-get install -y coinor-cbc \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your DFS architecture into the container
COPY . .

# 6. Scrub Windows line-endings and make the script executable
RUN sed -i 's/\r$//' run_daily_pipeline.sh && chmod +x run_daily_pipeline.sh

# 7. Set the orchestrator as the default command when the container boots
CMD ["./run_daily_pipeline.sh"]