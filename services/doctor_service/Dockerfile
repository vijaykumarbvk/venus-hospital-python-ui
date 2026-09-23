# Build context MUST be the repository root:
#   docker build -f services/doctor_service/Dockerfile -t <image> .
# because every service imports the shared `common/` package.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/doctor_service/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt gunicorn

COPY common/ ./common/
COPY services/__init__.py ./services/
COPY services/doctor_service/ ./services/doctor_service/

EXPOSE 8080

# create_app() is the Flask app factory in every service
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "--timeout", "60", \
     "services.doctor_service.app:create_app()"]
