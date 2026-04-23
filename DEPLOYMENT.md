# Deployment

Production deployment entry points. This file is intentionally short; depth lives in linked guides.

---

## Railway (recommended path for this repo)

1. Connect the **GitHub** repository to a Railway **service**.  
2. Set the **deploy branch** under *Settings → Source* (team-dependent: e.g. `feature/railway-deployment`, `updated-edu-tools`).  
3. **Start command** / **healthcheck** — see `railway.toml` (e.g. Gunicorn on `$PORT`, `/health`).  
4. **Variables** — at minimum `SECRET_KEY`, `DATABASE_URL`, `ANTHROPIC_API_KEY`; see [RAILWAY_ENV_VERIFICATION.md](RAILWAY_ENV_VERIFICATION.md) and [DEVELOPMENT.md](DEVELOPMENT.md).  
5. Run migrations after deploy or via release phase as configured: `alembic upgrade head`.  
6. Verify: `https://<your-service>.up.railway.app/health` and `/ready` if exposed.  

**Full guide:** [docs/RAILWAY_DEPLOYMENT.md](docs/RAILWAY_DEPLOYMENT.md)

---

## Digital Ocean / Nginx / Gunicorn

```bash
bash deployment/deploy.sh
```

Or install `requirements_production.txt`, set `FLASK_ENV=production` and `DATABASE_URL`, migrate, then:

```bash
gunicorn wsgi:app
```

---

## Custom domains (Railway)

- Prefer a subdomain, e.g. `app.example.com`  
- **CNAME** to your `*.up.railway.app` hostname; complete verification in Railway **Networking**  
- With **Cloudflare**, use **DNS-only** during verification if TLS fails  

---

## Troubleshooting

- **Anthropic 529 / overload** — retries and template fallback; check provider status and quotas.  
- **Railway endpoint name** — globally unique; change slug under Networking.  
- **Static 404 on Linux** — case-sensitive paths (`static/` vs `Static/`).  
- **CSRF on JSON** — app may use a fetch helper that sends `X-CSRFToken`; match your client.  

---

## Related docs

- [RAILWAY_ENV_VERIFICATION.md](RAILWAY_ENV_VERIFICATION.md)  
- [NEXT_STEPS_MIGRATION_FIX.md](NEXT_STEPS_MIGRATION_FIX.md)  
- [ROLLOUT_PLAN_ENHANCED.md](ROLLOUT_PLAN_ENHANCED.md)  
