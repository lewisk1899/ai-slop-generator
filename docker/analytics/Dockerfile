FROM python:3.12

# Install dependencies
COPY docker/analytics/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY src ./src
WORKDIR /src

# Default env vars (optional, overridden by docker-compose)
ENV GOOGLE_API_KEY=""
ENV CHANNELS="@GoogleDevelopers"
ENV DAYS=30
ENV TOP=10

# Run the script
# NOTE: the script itself reads GOOGLE_API_KEY (and any others) from the environment
CMD ["python", "youtube_analytics.py", \
     "--channels", "@GoogleDevelopers", \
     "--days", "30"]

