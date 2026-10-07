FROM python:3.12-alpine
WORKDIR /srv
RUN pip install --no-cache-dir prometheus_client==0.21.0
COPY app.py .
EXPOSE 8000
CMD ["python", "-u", "app.py"]
