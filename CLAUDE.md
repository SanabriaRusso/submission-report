# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask web application that provides an interface for querying and displaying report details for block producer submissions over specified time periods. It connects to a PostgreSQL database from the uptime-service-validation (coordinator) system.

## Development Commands

### Environment Setup
```bash
poetry install
poetry shell
```

### Running the Application
```bash
# Local development
python submission_report/app.py

# Docker
docker build -t submission-report .
docker run -p 5000:5000 \
           -e POSTGRES_HOST \
           -e POSTGRES_PORT \
           -e POSTGRES_DB \
           -e POSTGRES_USER \
           -e POSTGRES_PASSWORD \
           submission-report
```

## Required Environment Variables

The application requires these PostgreSQL connection variables:
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## Architecture

### Core Components

- **`submission_report/app.py`**: Main Flask application with routes for home page (`/`) and query endpoint (`/query`)
- **`submission_report/db.py`**: Database abstraction layer with methods for querying submission data
- **`submission_report/templates/results.html`**: Single HTML template for displaying submission reports

### Database Integration

The app uses psycopg2 to connect to a PostgreSQL database with these key tables:
- `submissions`: Block producer submission records with validation status
- `bot_logs`: Batch processing logs with start/end epochs
- `points_summary`: Points awarded per batch
- `nodes`: Node information including block producer keys

### Key Database Queries

- `total_submissions()`: Counts total, validated, unvalidated, and unverified submissions
- `submissions_per_batch()`: Groups submissions by batch time periods
- `points_per_batch()`: Calculates points granted per batch
- `batches_without_points()`: Identifies batches where no points were awarded
- `bad_submissions()`: Finds submissions with validation errors or verification failures

### Application Flow

1. Home page loads with default 90-day date range
2. User submits query with submitter ID and date range
3. App validates date format and queries database for multiple metrics
4. Results rendered with status indicators (✅/⚠️) based on data quality
5. Displays submission counts, batch information, points awarded, and error details

The web interface is available at http://localhost:5000 when running locally.