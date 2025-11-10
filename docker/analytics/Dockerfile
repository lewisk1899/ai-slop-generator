FROM python:3.12

COPY docker/analytics/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

ENV GOOGLE_API_KEY=""
ENV CHANNELS="@GoogleDevelopers"
ENV DAYS=30
ENV TOP=10

WORKDIR /src

ENTRYPOINT ["python youtube_analytics.py \
    --channels $CHANNELS \
    --days $DAYS \
    --top $TOP \
    --google-api-key $GOOGLE_API_KEY"]
