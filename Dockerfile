FROM python:3.12-slim

WORKDIR /app

# Copie et installation des dépendances (optimisation du cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home appuser

# Copie du code source en attribuant la propriété à l'utilisateur non-privilégié
COPY --chown=appuser:appuser app.py .

# Passage à l'utilisateur non-root
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]