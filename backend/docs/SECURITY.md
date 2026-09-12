# Finance App Security & Operations Guide

This document covers security measures, incident response, and operational procedures.

---

## Security Checklist

### Before Going Live ✓

- [ ] Change all default passwords
- [ ] Set up SSH key-only authentication
- [ ] Enable firewall (ufw)
- [ ] Configure SSL/HTTPS with Let's Encrypt
- [ ] Set strong `SECRET_KEY` in environment
- [ ] Set strong PostgreSQL database password
- [ ] Enable database backups
- [ ] Review security headers in Nginx config
- [ ] Setup error tracking (Sentry)
- [ ] Setup external monitoring (Uptime Robot)
- [ ] Test CORS configuration
- [ ] Disable debug mode (`DEBUG=False`)
- [ ] Enable rate limiting on auth endpoints
- [ ] Document all user accounts
- [ ] Test backup/restore procedures
- [ ] Document incident response procedures

### Ongoing Security ✓

- [ ] Monthly security updates (`apt-get update && apt-get upgrade`)
- [ ] Quarterly password rotation
- [ ] Quarterly review of firewall rules
- [ ] Monthly review of access logs
- [ ] Monthly test of backup restoration
- [ ] Annual security audit
- [ ] Annual code review for vulnerabilities

---

## Access Control

### SSH Access

**Key-Only Authentication (CRITICAL)**

```bash
# SSH as root to set up
ssh root@finance.example.com

# Create root's SSH key if not done
ssh-keygen -t ed25519 -f ~/.ssh/finance_app_rsa -N ""

# Copy your public key to authorized_keys
cat ~/.ssh/finance_app_rsa.pub >> ~/.ssh/authorized_keys

# Disable password authentication
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Restrict root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart sshd

# TEST: In new terminal, verify you can still login
ssh -i ~/.ssh/finance_app_rsa root@finance.example.com
```

**Application User Access**

```bash
# Create SSH key for finance_app user (application server only)
sudo -u finance_app ssh-keygen -t ed25519 -f /opt/finance_app/.ssh/id_ed25519 -N ""

# Used for Git operations
sudo -u finance_app ssh-add /opt/finance_app/.ssh/id_ed25519
```

### Database Access

**PostgreSQL User Permissions**

```sql
-- Login to PostgreSQL (from your managed database provider)
psql postgresql://admin:PASSWORD@db-host/postgres

-- Create application user (if not already created)
CREATE USER finance_user WITH PASSWORD 'strong_random_password';

-- Grant permissions on finance_db
GRANT ALL PRIVILEGES ON DATABASE finance_db TO finance_user;

-- Restrict to app user only (no password authentication)
ALTER USER finance_user WITH PASSWORD NULL;  -- or use scram-sha-256

-- Verify
\du  -- List users
\l   -- List databases
```

**Restrict Database Access**

```sql
-- Only allow connections from VPS IP (provider firewall)
-- Configured via cloud provider security groups/firewall rules

-- In pg_hba.conf (if self-managed):
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    finance_db      finance_user    192.0.2.1/32            md5
host    finance_db      postgres        localhost               trust
```

---

## Secrets Management

### Environment Variables

**Storage**

```bash
# Production .env file
ls -la /opt/finance_app/.env

# Permissions (readable by finance_app user only)
sudo chmod 600 /opt/finance_app/.env
sudo chown finance_app:finance_app /opt/finance_app/.env

# Never commit .env to git
grep .env .gitignore  # Should see: .env, .env.*
```

**Sensitive Values**

Never store in:
- Code
- Logs
- Comments
- Version control

Always store in:
- Environment variables
- .env file (not committed)
- Cloud provider secret manager (if available)

### Secret Rotation

**Rotate quarterly (every 3 months):**

```bash
# 1. Generate new SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Update .env
sudo nano /opt/finance_app/.env
# Edit: SECRET_KEY=new_value

# 3. Restart application
sudo systemctl restart finance_app

# 4. Verify health check
curl https://finance.example.com/health

# 5. Existing tokens become invalid (users re-login)
# This is expected and acceptable
```

**Rotate database password (if accessible):**

```bash
# 1. Generate new password
openssl rand -base64 32

# 2. Update in PostgreSQL
ALTER USER finance_user WITH PASSWORD 'new_password';

# 3. Update .env
# DATABASE_URL=postgresql://finance_user:new_password@...

# 4. Test connection
psql $DATABASE_URL -c "SELECT 1"

# 5. Restart application
sudo systemctl restart finance_app
```

---

## Firewall & Network Security

### UFW Rules

```bash
# View current rules
sudo ufw status

# Default policy: deny incoming, allow outgoing
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP (Let's Encrypt validation, redirect to HTTPS)
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Deny everything else
sudo ufw enable

# Save rules (automatic)
sudo ufw status numbered
```

### DDoS Protection

**Nginx rate limiting** (already configured in `deployment/nginx.conf`):
- Auth endpoints: 5 requests/minute per IP
- API endpoints: 100 requests/minute per user

**Additional measures:**

```bash
# If needed: Install Fail2ban (already installed by setup script)
sudo systemctl status fail2ban

# Review fail2ban rules
sudo cat /etc/fail2ban/jail.d/nginx-http-auth.conf

# See banned IPs
sudo fail2ban-client status nginx-http-auth
```

---

## Monitoring & Logging

### Application Logs

```bash
# View application logs
sudo journalctl -u finance_app -n 100 -f

# Search logs
sudo journalctl -u finance_app | grep "ERROR"

# Export logs
sudo journalctl -u finance_app > /tmp/app.log
```

### Access Logs

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/finance_app_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/finance_app_error.log

# Rotate logs (automatic, configured)
sudo logrotate /etc/logrotate.d/finance_app -f
```

### Suspicious Activity Indicators

Watch for:

```bash
# High rate of 401 (Unauthorized)
sudo grep " 401 " /var/log/nginx/finance_app_access.log | wc -l

# High rate of 403 (Forbidden)
sudo grep " 403 " /var/log/nginx/finance_app_access.log | wc -l

# Requests from unusual IPs
sudo grep -v "YOUR_IP" /var/log/nginx/finance_app_access.log | tail

# Errors in application logs
sudo journalctl -u finance_app | grep ERROR
```

---

## Incident Response

### Suspected Breach

**Immediate Actions (< 1 hour):**

1. **Isolate the system**
   ```bash
   # Stop the application
   sudo systemctl stop finance_app
   
   # Block all but your IP
   sudo ufw default deny incoming
   sudo ufw allow from YOUR_IP to any port 22
   sudo ufw enable
   ```

2. **Preserve evidence**
   ```bash
   # Copy logs
   sudo journalctl -u finance_app > /tmp/finance_app.log
   cp /var/log/nginx/* /tmp/
   tar -czf /tmp/evidence_$(date +%s).tar.gz /tmp/*.log
   ```

3. **Change all passwords**
   ```bash
   # Root password
   sudo passwd
   
   # Database password
   # See "Secret Rotation" section above
   ```

4. **Rotate SECRET_KEY**
   ```bash
   # See "Secret Rotation" section
   ```

5. **Notify stakeholders**
   - Document timeline
   - Identify what was compromised (if anything)
   - Plan communication to users

**Investigation (1-24 hours):**

1. Review logs for unauthorized access
2. Check database for suspicious data modifications
3. Review Git history for code changes
4. Scan system for malware/backdoors
5. Verify backup integrity

**Recovery:**

1. If backup needed: Restore from clean backup
2. If code compromised: Deploy fresh code from GitHub
3. Run security audit
4. Update all dependencies
5. Enable enhanced monitoring

### Service Degradation

**Application slow or unresponsive:**

1. Check resource usage
   ```bash
   top
   free -h
   df -h
   ```

2. Check for errors
   ```bash
   sudo journalctl -u finance_app | grep ERROR
   ```

3. Restart application
   ```bash
   sudo systemctl restart finance_app
   ```

4. Check database
   ```bash
   # Query database
   psql $DATABASE_URL -c "SELECT count(*) FROM transactions;"
   
   # Check query performance
   # Investigate slow queries in logs
   ```

5. Increase resources if needed
   ```bash
   # Scale up VPS
   # Note: Requires migration or load balancing
   ```

### Database Issues

**Connection failures:**

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check connection string in .env
cat /opt/finance_app/.env | grep DATABASE_URL

# Check Nginx/app logs
sudo systemctl status finance_app
```

**Disk space:**

```bash
# Check disk usage
df -h

# Identify large files
du -sh /var/log/*
du -sh /backups/finance_app/*

# Clean old logs
sudo logrotate /etc/logrotate.d/finance_app -f

# Clean old backups (keep 30 days)
find /backups/finance_app -name "*.tar.gz" -mtime +30 -delete
```

**Replication lag (if using read replicas):**

```bash
-- Connect to replica
psql postgresql://replica-user:password@replica-host/finance_db

-- Check lag
SELECT slot_name, restart_lsn FROM pg_replication_slots;

-- If lagged, restart replica or investigate slow queries
```

---

## Audit & Compliance

### Access Audit

```bash
# Who logged in recently
sudo lastlog

# Failed login attempts
sudo grep "Failed" /var/log/auth.log | tail -20

# sudo usage
sudo grep sudo /var/log/auth.log
```

### Data Audit

```bash
# Application audit logs (if implemented)
curl https://finance.example.com/api/audit-log \
  -H "Authorization: Bearer $TOKEN"

# Database audit (if enabled)
-- SELECT * FROM audit_log;
```

### Compliance Checklist

- [ ] No hardcoded secrets in code
- [ ] No plaintext passwords in logs
- [ ] All data encrypted in transit (HTTPS)
- [ ] Database backups automated
- [ ] Access logs maintained
- [ ] Error monitoring enabled
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Firewall configured

---

## Disaster Recovery

### Test Restore Procedure (Monthly)

```bash
# 1. Take backup of current database
# (via cloud provider)

# 2. Restore to staging environment
# (via cloud provider)

# 3. Verify restored data
curl https://staging.finance.example.com/health

# 4. Compare record counts
# On production:
curl https://finance.example.com/api/stats

# On staging:
curl https://staging.finance.example.com/api/stats

# 5. Document any discrepancies
```

### Disaster Recovery Plan

| Scenario | RTO | Recovery Steps |
|---|---|---|
| Database corruption | 1-2 hours | Restore from latest backup |
| VPS failure | 30 min | Provision new VPS, restore config, restart |
| Lost SSH key | 1 hour | Use provider console, reset SSH keys |
| Forgotten password | 30 min | Reset via provider console or password reset |
| Code corruption | 30 min | Redeploy from clean Git branch |

**RTO** (Recovery Time Objective) = Max time to restore service

---

## Regular Maintenance

### Weekly

```bash
# Check system health
df -h              # Disk usage
free -h            # Memory usage
top -b -n1 | head  # CPU usage

# Review error logs
sudo journalctl -u finance_app | grep ERROR | tail -20

# Check if updates available
apt-get update
apt list --upgradable
```

### Monthly

```bash
# Security updates
sudo apt-get update && apt-get upgrade -y

# Test backup/restore
# See Disaster Recovery section

# Review access logs for suspicious activity
sudo grep "401\|403\|500" /var/log/nginx/finance_app_access.log | wc -l

# Rotate logs manually if needed
sudo logrotate -f /etc/logrotate.d/finance_app
```

### Quarterly

```bash
# Rotate secrets (see Secret Rotation section)

# Security audit
# Review firewall rules, access controls, logs

# Performance review
# Check for slow queries, memory leaks, errors

# Update all dependencies
cd /opt/finance_app
source .venv/bin/activate
pip list --outdated
pip install --upgrade [packages]
bash scripts/deploy.sh
```

### Annually

```bash
# Full security audit
# - Code review
# - Dependency scan
# - Infrastructure review
# - Access control review

# Disaster recovery drill
# - Restore from backup to staging
# - Verify all functionality
# - Document lessons learned

# Update documentation
# - Update runbooks
# - Update security procedures
# - Update contact information
```

---

## Emergency Contacts & Escalation

**In case of emergency:**

1. **Application down**: Restart and check logs
   ```bash
   sudo systemctl restart finance_app
   sudo journalctl -u finance_app -f
   ```

2. **Database down**: Contact database provider support

3. **Security breach**: Isolate system, preserve evidence, notify stakeholders

4. **Data loss**: Restore from backup (keep backups tested)

---

## Compliance Standards

This deployment follows:

- **OWASP Top 10**: Protections against injection, broken auth, sensitive data exposure, XML external entities, broken access control, security misconfiguration, XSS, insecure deserialization, using components with known vulnerabilities, insufficient logging

- **NIST Cybersecurity Framework**: Identify, Protect, Detect, Respond, Recover

- **PCI DSS** (if handling payments): Secure network, protect cardholder data, vulnerability management, access control, monitoring and testing, security policy

---

## Resources

- **OWASP Security**: https://owasp.org/
- **Let's Encrypt**: https://letsencrypt.org/
- **Nginx Security**: https://nginx.org/en/docs/
- **PostgreSQL Security**: https://www.postgresql.org/docs/current/sql-createuser.html
- **Linux Security**: https://ubuntu.com/security
- **Sentry Monitoring**: https://sentry.io/
- **Have I Been Pwned**: https://haveibeenpwned.com/

---

**Version**: 1.0
**Last Updated**: August 25, 2026
**Document Owner**: DevOps Team
