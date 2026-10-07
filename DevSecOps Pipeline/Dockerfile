FROM python:3.12-alpine AS base
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-alpine
WORKDIR /srv
# copy only installed packages, not pip caches or build tools
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=base /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY app ./app
# fixed numeric UID so Kubernetes can verify runAsNonRoot without guessing
RUN addgroup -S -g 10001 web && adduser -S -u 10001 -G web web
USER 10001:10001
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION PORT=5000
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app.server:app"]
