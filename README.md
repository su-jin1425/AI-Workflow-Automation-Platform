# AI Workflow Automation Platform

A full-stack platform for creating, executing, and monitoring AI-powered workflows.

## What This Project Does

Users build a workflow by connecting visual nodes. The backend stores the workflow, validates the graph, executes each node in order, records logs and metrics, and streams execution updates back to the UI.

## Stack

- Frontend: Next.js, React, TypeScript, React Flow, Zustand, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Alembic, AsyncIO
- AI: OpenAI API through a real AI prompt node
- Queue: Celery with Redis
- Database: PostgreSQL
- Monitoring: Prometheus and Grafana
- Deployment: Docker Compose and Nginx

## Main Features

- Register and login with JWT authentication
- Create and update workflows
- Drag and connect workflow nodes
- Configure nodes using JSON
- Execute workflows in the background
- Track execution logs through WebSockets
- Store workflow runs, node runs, logs, and metrics
- View dashboard analytics
- Run with Docker Compose

## Supported Node Types

- AI Prompt
- API Request
- Condition
- Delay
- Database
- Webhook
- Email
- Scheduler
- Logic
- File Processing

## Run Locally

Create an environment file:

```bash
copy .env.example .env
```

Start the full platform:

```bash
docker-compose up --build
```

Open:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

## AI Setup

To run AI Prompt nodes, set this in `.env`:

```env
OPENAI_API_KEY=your_api_key
```

If the key is missing, AI nodes fail clearly during execution instead of returning fake output.

## Production Run

Set real secrets and production URLs in `.env`, then run:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

The production compose file runs:

- PostgreSQL
- Redis
- FastAPI backend
- Celery worker
- Next.js frontend
- Nginx reverse proxy

## Simple Explanation

The frontend is the screen where you draw the workflow.

The backend is the brain that saves and runs the workflow.

PostgreSQL stores users, workflows, executions, logs, and metrics.

Redis and Celery run heavy workflow jobs in the background.

WebSockets send live progress updates to the browser.

Prometheus and Grafana show system health and metrics.
