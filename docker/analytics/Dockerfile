FROM python:3.12

COPY docker/analytics/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

ENTRYPOINT ["sh", "-c", "touch /tmp/keepalive && tail -f /tmp/keepalive"]
