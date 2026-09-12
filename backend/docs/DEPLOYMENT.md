# Finance App Production Deployment Guide (Option A)

**Architecture**: Single VPS + Managed PostgreSQL Database + Nginx Reverse Proxy

**Cost**: ~$27/month (VPS $12 + Database $15)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Server Configuration](#server-configuration)
4. [Application Deployment](#application-deployment)
5. [SSL/HTTPS Setup](#sslhttps-setup)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backups & Recovery](#backups--recovery)
8. [Security Hardening](#security-hardening)
9. [Troubleshooting](#troubleshooting)
10. [Operational Runbooks](#operational-runbooks)

---

## Prerequisites

### Required Accounts/Services

1. **DigitalOcean, Linode, or Hetzner Account**
   - For VPS ($5-20/month depending on provider)
   - 2GB RAM, 1 CPU, 50GB SSD minimum

2. **PostgreSQL Managed Database**
   - DigitalOcean Managed Databases
   - AWS RDS
   - Heroku Postgres
   - Cost: $9-20/month

3. **Domain Name**
   - Can use existing domain
   - Cost: $10-15/year
   - Must update DNS to point to VPS IP

4. **Git Repository** (GitHub, GitLab, Gitea)
   - For source code version control
   - Recommended: Private repository

5. **Optional: Sentry Account**
   - For error tracking
   - Free tier: 10,000 errors/month
   - Cost: Free or $29+/month for paid tier

6. **Optional: Slack Workspace**
   - For deployment notifications
   - Cost: Free or $12.50+/month

### Local Tools

- SSH client (built-in on macOS/Linux)
- `ssh-keygen` for creating SSH keys
- `curl` or Postman for testing API

---

## Infrastructure Setup

### Step 1: Create VPS

**DigitalOcean Example:**

1. Log into DigitalOcean Dashboard
2. Click "Create" → "Droplets"
3. Choose:
   - Image: Ubuntu 22.04 LTS x64
   - Plan: Basic, $6/month (2GB RAM, 1 CPU, 50GB SSD)
   - Region: Closest to your location
   - Authentication: SSH key (recommended) or password
   - Hostname: `finance-app` or similar
4. Click "Create Droplet"
5. Wait 1-2 minutes for droplet to boot
6. Note the IP address (e.g., `192.0.2.1`)

**Linode Example:**

1. Log into Linode Manager
2. Create Linode → Choose Ubuntu 22.04 LTS
3. Plan: Nanode 1GB ($5/month) or Linode 2GB ($12/month)
4. Region: Closest to your location
5. Root password or SSH key authentication
6. Create
7. Note the IP address

### Step 2: Create Managed PostgreSQL Database

**DigitalOcean Managed Database Example:**

1. DigitalOcean Dashboard → Databases → Create Database
2. Choose: PostgreSQL, Version 15+
3. Plan: Shared cluster ($15/month) for personal app
4. Region: Same as your VPS
5. DB name: `finance_db`
6. User: `finance_user` (auto-generated with strong password)
7. Create

**Configuration:**
- Save the connection string in format:
  ```
  postgresql://finance_user:PASSWORD@db-abc.db.ondigitalocean.com:25060/finance_db
  ```

### Step 3: Configure DNS

Update your domain DNS records to point to the VPS IP:

```
Type  Name            Value
─────────────────────────────────────────────
A     finance         192.0.2.1  (your VPS IP)
AAAA  finance         2001:db8::1 (IPv6, if available)
```

Wait 5-30 minutes for DNS propagation.

---

## Server Configuration

### Step 4: Run Server Setup Script

Connect to your VPS:

```bash
ssh root@192.0.2.1  # SSH as root initially

# Or with SSH key:
ssh -i ~/.ssh/id_rsa root@192.0.2.1
```

Clone the repository and run setup:

```bash
# Download the repository
git clone https://github.com/YOUR_USERNAME/finance_app.git /tmp/finance_app_setup
cd /tmp/finance_app_setup

# Run setup script (as root)
sudo bash scripts/setup_server.sh
```

This script will:
- ✓ Update system packages
- ✓ Install Python 3.12, PostgreSQL client, Nginx, Certbot
- ✓ Create `finance_app` user
- ✓ Setup directories and permissions
- ✓ Configure firewall (ufw)
- ✓ Install SSH hardening (fail2ban)
- ✓ Setup log rotation
- ✓ Create backup scripts
- ✓ Add cron jobs

**Output:** You'll see instructions for next steps.

### Step 5: Clone Application Code

```bash
# Switch to finance_app user
sudo -u finance_app -s

# Clone the repository into /opt/finance_app
cd /opt/finance_app
git clone https://github.com/YOUR_USERNAME/finance_app.git .

# Setup Python virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Configure Environment Variables

```bash
# Copy production template
sudo -u finance_app cp .env.production .env

# Edit with real values
sudo -u finance_app nano .env
```

**Required values to set:**

```env
DATABASE_URL=postgresql://finance_user:PASSWORD@db-host:25060/finance_db
SECRET_KEY=[GENERATE_NEW_SECURE_KEY_HERE]
ENVIRONMENT=production
DOMAIN=finance.example.com
```

Generate secure `SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set permissions:

```bash
sudo chmod 600 /opt/finance_app/.env
```

### Step 7: Initialize Database

```bash
# As finance_app user
sudo -u finance_app -s
cd /opt/finance_app
source .venv/bin/activate

# Run migrations
alembic upgrade head

# Verify connection
python3 -c "from infrastructure.database.session import engine; print('Database connected:', engine.url)"
```

---

## SSL/HTTPS Setup

### Step 8: Obtain SSL Certificate with Let's Encrypt

```bash
# As root
sudo certbot certonly --nginx -d finance.example.com

# Or if Nginx not yet configured:
sudo certbot certonly --standalone -d finance.example.com

# Follow prompts:
# - Enter email address
# - Accept terms of service
# - No opt-in to EFF mailing list (up to you)
```

Certificate will be saved to:
```
/etc/letsencrypt/live/finance.example.com/
```

### Step 9: Configure Nginx

```bash
# Copy Nginx configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/finance_app

# Edit to set your domain
sudo nano /etc/nginx/sites-available/finance_app
# Change: server_name finance.example.com;
# Change: ssl_certificate paths

# Enable the site
sudo ln -s /etc/nginx/sites-available/finance_app /etc/nginx/sites-enabled/

# Disable default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## Application Deployment

### Step 10: Setup Systemd Service

```bash
# Copy service file
sudo cp deployment/finance_app.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (starts on reboot)
sudo systemctl enable finance_app

# Start the service
sudo systemctl start finance_app

# Check status
sudo systemctl status finance_app

# View logs
sudo journalctl -u finance_app -f
```

### Step 11: Verify Deployment

Test the health endpoint:

```bash
# From your local machine
curl https://finance.example.com/health

# Expected output:
# {"status":"ok","timestamp":"2026-08-25T10:30:45Z","database":"ok"}
```

Test an API endpoint:

```bash
# Register a new user
curl -X POST https://finance.example.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

---

## Monitoring & Logging

### Step 12: Setup Error Tracking with Sentry

1. Create Sentry account: https://sentry.io (free tier available)
2. Create new project: "Finance App"
3. Copy DSN: `https://[key]@[org].ingest.sentry.io/[project]`

Update `.env`:

```env
SENTRY_DSN=https://[key]@[org].ingest.sentry.io/[project]
```

Restart application:

```bash
sudo systemctl restart finance_app
```

### Step 13: Monitor Logs

View real-time logs:

```bash
# Application logs
sudo journalctl -u finance_app -f

# Nginx access logs
sudo tail -f /var/log/nginx/finance_app_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/finance_app_error.log
```

Setup log forwarding (optional, if using external log service):

```bash
# Example: LogDNA, Papertrail, or CloudWatch
# Install agent and configure to send /var/log/finance_app/ to service
```

---

## Backups & Recovery

### Step 14: Verify Backup Strategy

**Database Backups:**
- Configured: Daily automatic via managed database provider
- Retention: 30 days
- Location: Provider infrastructure (geo-redundant)
- Recovery: Point-in-time restore available

**Application Code Backups:**
- Daily via cron: `/usr/local/sbin/backup_finance_app.sh`
- Stored: `/backups/finance_app/daily/`
- Retention: 30 days (auto-rotated)

**Test Restore (Monthly):**

```bash
# Simulate database restore to staging environment
# Contact provider for point-in-time recovery instructions
```

---

## Security Hardening

### Step 15: SSH Key-Only Authentication

```bash
# SSH into server
ssh -i ~/.ssh/id_rsa root@finance.example.com

# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Make these changes:
# PasswordAuthentication no
# PubkeyAuthentication yes
# PermitRootLogin no  # If setting up admin user

# Restart SSH
sudo systemctl restart sshd

# TEST: Don't close current session! Open new one to verify.
# If locked out, use provider console access.
```

### Step 16: Firewall Verification

```bash
# Check firewall status
sudo ufw status

# Should show:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
# [IPv6 versions of above]
```

### Step 17: Security Headers Verification

Test security headers:

```bash
curl -I https://finance.example.com/health

# Check for these headers:
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Content-Security-Policy: default-src 'self'
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check service status
sudo systemctl status finance_app

# View detailed logs
sudo journalctl -u finance_app -n 50

# Check Gunicorn config
sudo cat /opt/finance_app/deployment/gunicorn_config.py

# Try starting manually
cd /opt/finance_app
source .venv/bin/activate
gunicorn -c deployment/gunicorn_config.py main:app
```

### Database Connection Failed

```bash
# Test database connection
psql postgresql://finance_user:PASSWORD@db-host:25060/finance_db

# Check .env file
cat /opt/finance_app/.env | grep DATABASE_URL

# Verify database is running and accessible from VPS IP
# (Provider should allow VPS IP in firewall)
```

### Nginx Shows 502 Bad Gateway

```bash
# Check if Gunicorn is running
sudo systemctl status finance_app

# Check Nginx error log
sudo tail -f /var/log/nginx/finance_app_error.log

# Verify Nginx can connect to 127.0.0.1:8000
sudo netstat -tlnp | grep 8000
```

### High CPU/Memory Usage

```bash
# Check resource usage
top -u finance_app

# Check for specific process consuming resources
ps aux | grep gunicorn

# Reduce worker count if needed
sudo nano /opt/finance_app/deployment/gunicorn_config.py
# Reduce 'workers' from 8 to 4

# Restart
sudo systemctl restart finance_app
```

---

## Operational Runbooks

### Deploying Updates

```bash
# From your local machine
git push origin main

# On server (automatic or manual)
cd /opt/finance_app
bash scripts/deploy.sh

# Monitor deployment
sudo journalctl -u finance_app -f

# Health check
curl https://finance.example.com/health
```

### Rolling Back a Deployment

```bash
# List available backups
ls -la /backups/finance_app/

# Rollback to specific backup
bash scripts/deploy.sh --rollback backup_20260825_023045

# Verify
curl https://finance.example.com/health
```

### Viewing Logs

```bash
# Real-time application logs (last 100 lines)
sudo journalctl -u finance_app -n 100 -f

# Logs from specific time
sudo journalctl -u finance_app --since "2 hours ago"

# Export logs to file
sudo journalctl -u finance_app > /tmp/finance_app.log
```

### Restarting Services

```bash
# Restart application
sudo systemctl restart finance_app

# Restart Nginx
sudo systemctl restart nginx

# Restart all services
sudo systemctl restart finance_app nginx
```

### Checking Disk Usage

```bash
# Disk usage summary
df -h

# Application directory size
du -sh /opt/finance_app

# Backup directory size
du -sh /backups/finance_app

# Log directory size
du -sh /var/log/finance_app

# Clean old backups if needed
find /backups/finance_app -name "backup_*" -mtime +30 -delete
```

---

## Monitoring & Alerts

### Setup External Monitoring (Recommended)

Use free services to monitor your application:

**Option 1: Uptime Robot (Free)**
1. Sign up: https://uptimerobot.com
2. Add monitor: https://finance.example.com/health
3. Check interval: 5 minutes
4. Alert: Email on failure

**Option 2: Sentry (Free tier)**
Already configured in previous steps.

**Option 3: Custom Monitoring Script**

```bash
#!/bin/bash
# Check health every 5 minutes
while true; do
    if ! curl -sf https://finance.example.com/health > /dev/null; then
        # Send alert
        echo "Finance App is down" | mail -s "Alert" your-email@example.com
    fi
    sleep 300
done
```

---

## Summary

✓ Infrastructure set up (VPS, Database)
✓ Server configured (Python, Nginx, Certbot)
✓ Application deployed (Git, venv, dependencies)
✓ Database initialized (Migrations)
✓ SSL/HTTPS enabled (Let's Encrypt)
✓ Gunicorn + Nginx running
✓ Logging configured
✓ Monitoring enabled
✓ Backups automated
✓ Security hardened

**Your app is now live at: https://finance.example.com** 🚀

---

## Support & Resources

- **Documentation**: See README.md in project root
- **Logs**: `sudo journalctl -u finance_app -f`
- **Status**: `sudo systemctl status finance_app`
- **Sentry Errors**: https://sentry.io/organizations/YOUR_ORG/issues/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Nginx Docs**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/docs/

---

**Last updated**: August 25, 2026
**Version**: 1.0
**Author**: Finance App Development Team
