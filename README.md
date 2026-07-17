# Poland Rent Analytics

An automated scraping and analytics tool for the Polish real estate rental market. The system asynchronously extracts apartment listings, stores them in a local SQLite database, analyzes the data to find the most cost-effective offers (lowest price per square meter), and sends a summarized report directly to Telegram.

## Features

* Asynchronous web scraping using Playwright (Headless Chromium).
* Data validation and local storage using SQLAlchemy and SQLite.
* Database schema versioning and management with Alembic migrations.
* Data processing and metric calculations using Pandas.
* Automated Telegram notifications via Aiogram.
* Fully containerized environment using Docker for cross-platform execution.

## Tech Stack

* Python 3.12
* Playwright
* SQLAlchemy & Alembic
* Pandas
* Aiogram
* Docker & Docker Compose

## Prerequisites

* Docker and Docker Compose installed on your local machine or server.
* A Telegram Bot Token (can be obtained via @BotFather on Telegram).
* Your personal Telegram Chat ID (can be obtained via @userinfobot).

## Setup and Installation

1. Clone the repository to your local machine.

2. Create a `.env` file in the root directory of the project and add your Telegram credentials:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

3. Build and launch the Docker container for the first time:

```bash
docker-compose up --build
```

## Usage

The `docker-compose.yml` file is configured to execute the pipeline sequentially: it applies database migrations, runs the scraping script, and then executes the analytics script to send the Telegram notification.

To run the pipeline on demand:

```bash
docker-compose up
```

To run the service in the background (detached mode):

```bash
docker-compose up -d
```

### Automation

For daily updates, it is recommended to schedule the `docker-compose up` command using a system task scheduler (e.g., Windows Task Scheduler or Linux Cron) to run at a specific time each day. 

## Project Structure

* `app/services/scraper.py`: Core asynchronous web scraping logic.
* `app/services/analytics.py`: Data cleaning, processinggi.
* `app/services/notifier.py`: Telegram bot integration and message formatting.
* `app/models/`: SQLAlchemy database schema definitions.
* `migrations/`: Alembic migration scripts and version control.
* `docker-compose.yml` & `Dockerfile`: Docker configuration and orchestration.