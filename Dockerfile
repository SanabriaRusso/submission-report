FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    libpq5 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

ENV PYTHONUNBUFFERED 1

EXPOSE 5000
ENV FLASK_ENV=production
ENV FLASK_APP=/app/submission_report/app.py

CMD ["flask", "run", "--host=0.0.0.0"]