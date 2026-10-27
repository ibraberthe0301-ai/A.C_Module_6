DOCKER API DASHBOARD (MINIMALIST & SECURE)

Minimalist, sleek, dark-themed Flask REST API served inside a hardened Docker container (appuser non-root mode) with a built-in technical dashboard.

Design System

Background: Ultra Dark Graphite #0a0a0c & #121216

Surface & Borders: #1a1a20 / #2a2d3a

Accents: Electric Cyan #00d2ff & Soft Sky Blue #38bdf8

Typography: JetBrains Mono / Inter System Stack

Aesthetic: Zero emojis, clean precision technical console layout.

Deployment

Run using Docker Compose:

docker compose up -d --build


Access the UI dashboard at: http://localhost:5000

Terminal Testing

# JSON Root Endpoint
curl -H "Accept: application/json" http://localhost:5000/

# Healthcheck Endpoint
curl http://localhost:5000/health

# Security Check
docker exec -it advanced-api whoami
# Output: appuser
