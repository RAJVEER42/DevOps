FROM python:3.12-alpine
WORKDIR /srv
# stdlib only at runtime, so nothing to pip install
COPY app ./app
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION PORT=8000
EXPOSE 8000
HEALTHCHECK --interval=15s CMD wget -qO- http://127.0.0.1:8000/health || exit 1
CMD ["python", "-m", "app.main"]
