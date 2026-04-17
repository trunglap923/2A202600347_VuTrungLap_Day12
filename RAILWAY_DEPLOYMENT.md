# Railway Deployment Guide: Production AI Agent

Follow these steps to deploy your agent from the `my-production-agent` directory.

## 1. Prerequisites

- A Railway account ([railway.app](https://railway.app)).
- Railway CLI installed (optional but recommended).
  - Install: `npm i -g @railway/cli` (requires Node.js) or download from their site.

## 2. Option A: Deployment via CLI (Fastest)

Run these commands inside your `my-production-agent` folder:

```bash
# 1. Login to your account
railway login

# 2. Initialize a new project
railway init

# 3. Add Redis service
railway add
# Select "Redis" from the list

# 4. Upload and deploy
railway up
```

## 3. Option B: Deployment via GitHub Dashboard (Recommended)

1. **Push to GitHub**: Create a new private repository and push the contents of `my-production-agent`.
2. **Create Project**: On Railway Dashboard, click **New Project** -> **Deploy from GitHub repo**.
3. **Add Redis**: Click **Add Service** -> **Redis**.
4. **Reference Redis URL**:
   - Go to your Agent Service -> **Variables**.
   - Add a new variable `REDIS_URL`.
   - Set its value to `${{Redis.REDIS_URL}}` (This links the two services automatically).

## 4. Required Environment Variables

You MUST add these to your Railway Project Variables:

| Variable         | Description                       |
| :--------------- | :-------------------------------- |
| `OPENAI_API_KEY` | Your real sk-... key from OpenAI. |
| `AGENT_API_KEY`  | `my-secret-key` (or your choice). |
| `JWT_SECRET`     | A random string for JWT signing.  |

## 5. Verification

Once deployed, verify your live URL:

- `https://your-app.up.railway.app/health` -> Should be 200 OK.
- `https://your-app.up.railway.app/ready` -> Should be 200 OK (Redis connected).
