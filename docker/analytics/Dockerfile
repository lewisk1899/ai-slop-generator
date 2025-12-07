FROM python:3.12-slim

# Set working directory for package install
WORKDIR /app

# Install Python dependencies first (for caching)
COPY docker/analytics/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install the project in editable mode so imports like `models` and `crud` work
RUN pip install --no-cache-dir -e .

# Now run inside the src directory as the working folder
WORKDIR /app/src

# Default environment variables (override via docker-compose)
ENV GOOGLE_API_KEY=""
ENV CHANNELS="@GoogleDevelopers"
ENV DAYS=30
ENV TOP=10

# Run analytics module
CMD ["python", "-m", "youtube_analytics", \
     "--channels", "@GoogleDevelopers", \
     "--days", "30"]
