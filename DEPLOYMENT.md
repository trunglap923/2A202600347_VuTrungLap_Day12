# Deployment Guide: Production AI Agent

This guide outlines how to deploy the "Elite" AI Agent found in `my-production-agent/`.

## 1. Local Deployment (Docker Compose)

Best for testing the full cluster (Agent + Redis + Nginx LB).

```bash
cd my-production-agent
# 1. Create .env from .env.example
cp .env.example .env

# 2. Add your OpenAI API Key to .env
# OPENAI_API_KEY=sk-...

# 3. Start the cluster
docker compose up -d --build --scale agent=3
```

## 2. Cloud Deployment (Railway)

The project is pre-configured with `railway.toml`.

1. **Push to GitHub**: Push the contents of the root or `my-production-agent/` to a repo.
2. **Link to Railway**: Create a New Project -> GitHub Repo.
3. **Configure Secrets**: In Railway Dashboard, add:
   - `OPENAI_API_KEY`
   - `AGENT_API_KEY`
   - `JWT_SECRET`
   - `REDIS_URL` (Link a Redis service or use Railway's internal Redis).
4. **Deploy**: Railway will use `railway.toml` to start the agent.

## 3. Post-Deployment Verification

- **Health**: `GET /health`
- **Readiness**: `GET /ready`
- **Chat**: `POST /chat` (Require `X-API-Key`)
- **Management**: `GET /chat/{id}/history` | `DELETE /chat/{id}`
