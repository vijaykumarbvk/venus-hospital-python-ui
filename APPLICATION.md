# Venus Multispecialty Hospital — Python Edition

Python/Flask/Streamlit port of the original Spring Boot + React system.
Same architecture, same roles, same event-driven design — different stack.

## Architecture

```
┌─────────────────┐
│  Streamlit App   │  Port 8501 — role-based UI (Patient/Doctor/Admin/
│                   │  Assistant Doctor/Surgeon)
└────────┬─────────┘
         │ HTTPS/JSON
┌────────▼─────────┐
│   API Gateway     │  Port 8080 — Flask reverse proxy
│  • JWT validation │
│  • Flask-Limiter (Redis-backed rate limiting)
│  • pybreaker circuit breakers per downstream service
└───┬────┬────┬────┬┘
    │    │    │    │
    ▼    ▼    ▼    ▼
 User  Appt Doctor Patient   each: Flask + SQLAlchemy + MySQL
 :8081 :8082 :8083  :8084    + Redis caching + Kafka events
```

| Concern              | Java/Spring                  | Python equivalent used here          |
|-----------------------|-------------------------------|----------------------------------------|
| Web framework          | Spring Boot                  | Flask                                   |
| Security/JWT           | Spring Security + jjwt       | PyJWT + custom decorators               |
| Service discovery       | Eureka                       | *(omitted — services referenced by URL/env var; add Consul if needed)* |
| API Gateway             | Spring Cloud Gateway         | Flask reverse-proxy app                 |
| Circuit breaker          | Resilience4j                 | pybreaker                               |
| Cache                    | Spring Cache + Redis         | redis-py + `@cached` decorator          |
| Messaging                | Spring Kafka                 | kafka-python                            |
| ORM                      | Spring Data JPA / Hibernate  | Flask-SQLAlchemy                        |
| Validation                | Bean Validation (`@Valid`)   | marshmallow schemas                     |
| Frontend                  | React + TypeScript + Tailwind| Streamlit (Python-only UI)              |

## Project Layout

```
venus-hospital-python/
├── common/                  # shared across every Flask service
│   ├── constants.py         # UserRole, AppointmentStatus enums
│   ├── responses.py         # uniform ApiResponse envelope
│   ├── exceptions.py        # BusinessException, ResourceNotFoundException
│   ├── jwt_utils.py         # token issuance + @token_required / @roles_required
│   ├── cache.py             # @cached / evict() Redis helpers
│   └── resilience.py        # pybreaker + Kafka EventPublisher
├── services/
│   ├── user_service/        # auth, registration, user CRUD  (port 8081)
│   ├── appointment_service/ # booking, scheduling, status     (port 8082)
│   ├── doctor_service/      # doctor profiles                 (port 8083)
│   ├── patient_service/     # patient profiles                (port 8084)
│   └── api_gateway/         # reverse proxy + auth + rate limit (port 8080)
├── streamlit_app/
│   ├── Home.py               # landing + login/register
│   ├── pages/
│   │   ├── 1_Dashboard.py    # role router (Patient/Doctor/Admin/Assistant/Surgeon)
│   │   ├── 2_Appointments.py
│   │   ├── 3_Directory.py
│   │   └── 4_Settings.py
│   └── utils/
│       ├── api_client.py     # requests wrapper for the gateway
│       ├── auth.py           # session_state-based auth
│       └── dashboards.py     # one render_xxx_dashboard() per role
└── docker-compose.yml         # MySQL, Redis, Zookeeper, Kafka
```

## Prerequisites

- Python 3.11+
- MySQL 8.0, Redis, Kafka + Zookeeper (via `docker-compose up -d`)

## Setup

### 1. Infrastructure

```bash
docker-compose up -d
```

Create one database per service (or let SQLAlchemy's `create_all()`
create tables once the databases themselves exist):

```sql
CREATE DATABASE venus_user_db;
CREATE DATABASE venus_appointment_db;
CREATE DATABASE venus_doctor_db;
CREATE DATABASE venus_patient_db;
```

### 2. Backend services

Each service is independent — install its requirements and run it.
Do this in 5 separate terminals (or use a process manager like `honcho`/`foreman`):

```bash
# User service
cd services/user_service && pip install -r requirements.txt
python -m services.user_service.app        # run from repo root, port 8081

# Appointment service
python -m services.appointment_service.app  # port 8082

# Doctor service
python -m services.doctor_service.app       # port 8083

# Patient service
python -m services.patient_service.app      # port 8084

# API Gateway (start last, after the others are up)
python -m services.api_gateway.app          # port 8080
```

> Run all commands from the **repository root** so the `common` package
> resolves correctly, e.g. `python -m services.user_service.app`.

### 3. Streamlit frontend

```bash
cd streamlit_app
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8080     # optional, this is the default
streamlit run Home.py
```

Visit `http://localhost:8501`.

## Environment Variables

| Variable | Default | Used by |
|---|---|---|
| `DATABASE_URL` | `mysql+pymysql://root:root@localhost:3306/<db>` | each service |
| `JWT_SECRET` | dev secret (change in production!) | all services + gateway |
| `REDIS_HOST` / `REDIS_PORT` | `localhost` / `6379` | doctor/appointment services |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | all services |
| `USER_SERVICE_URL` | `http://localhost:8081` | doctor/patient services |
| `API_BASE_URL` | `http://localhost:8080` | Streamlit app |

## Roles & Dashboards

- **ADMIN** — hospital-wide stats, doctor/department overview
- **PATIENT** — book appointments, view health profile
- **DOCTOR** — today's schedule, advance appointment status
- **ASSISTANT_DOCTOR** — task list, assigned doctors, shift schedule
- **SURGEON** — OT schedule, surgical team, OT availability

## Notes on Parity with the Java Version

- **Constructor injection** → Python has no DI container by default; each
  Flask module wires its dependencies explicitly at the top of `app.py`
  (equivalent intent: explicit, testable construction over hidden globals).
- **Service discovery (Eureka)** was intentionally left out for simplicity —
  services are wired via environment variables. Add `python-consul` +
  a Consul container if you need dynamic discovery.
- **Rate limiting** uses Flask-Limiter with a Redis backend, mirroring
  Spring Cloud Gateway's `RequestRateLimiter` + Redis token bucket.
- Each service still owns its own database (database-per-service), same
  as the Java version.
