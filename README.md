# Submission Report Web App

This Flask application provides an interface for querying and displaying report details for block producer submissions over specified time periods.

## Features

 - Query submissions by block producer over a given time period.
 - Display a detailed report including validation statuses, batch information, and points awarded per batch.
 - Responsive web design using Bootstrap for optimal viewing on various devices.

## Getting Started

### Prerequisites

- Python >= 3.10
- [Poetry](https://python-poetry.org/docs/), a tool for dependency management and packaging in Python.

### Setting Up Your Development Environment

1. **Install dependencies:**

```sh
git clone https://github.com/MinaFoundation/submission_report.git
cd submission_report

poetry install
```

2. **Activate the Virtual Environment:**

After installing the project dependencies with `poetry install`, you can activate the virtual environment by running:

```sh
poetry shell
```

This will spawn a new shell (subshell) with the virtual environment activated. It ensures that all commands and scripts are run within the context of your project's dependencies.


## Configuration

The program requires setting environment variables to connect to [uptime-service-validation (coordinator)](https://github.com/MinaFoundation/uptime-service-validation) Postgres database, e.g.: 

```sh
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=coordinator
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
```

## Running the web app

```sh
python submission_report/app.py
```

The web interface will be available at: http://localhost:5000.

## Docker

Program is also shipped as a docker image.

### Building Docker

```sh
docker build -t submission-report .
```

### Running Docker

When running pass all relevant env variables to the docker (see `.env`), e.g.:

```sh
docker run -p 5000:5000 \
           -e POSTGRES_HOST \
           -e POSTGRES_PORT \
           -e POSTGRES_DB \
           -e POSTGRES_USER \
           -e POSTGRES_PASSWORD \
           submission-report
```