# Security Policy

Do not report vulnerabilities through public GitHub issues. For a real deployment, publish a dedicated security contact.

## Production hardening checklist
- Replace all development secrets and rotate them periodically.
- Terminate TLS at the edge and enforce HTTPS/HSTS.
- Store secrets in AWS Secrets Manager or SSM Parameter Store.
- Enable GitHub secret scanning, Dependabot, CodeQL, image scanning and branch protection.
- Restrict CORS and database/network security groups.
- Add PostgreSQL Row Level Security for defense-in-depth tenant isolation.
- Prefer secure HttpOnly refresh cookies/BFF for browser session refresh.
- Configure Stripe webhook secrets independently per environment.
- Add WAF/API-gateway limits and abuse monitoring.
- Encrypt RDS/Redis backups and define retention/restore drills.
