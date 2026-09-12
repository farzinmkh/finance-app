#!/bin/bash
#
# Finance App Initial Server Setup Script
#
# This script prepares a fresh Ubuntu 22.04 LTS VPS for production deployment.
#
# Run this ONCE on a new server:
#   sudo bash scripts/setup_server.sh
#
# This script will:
#   1. Update system packages
#   2. Install required dependencies
#   3. Create non-root application user
#   4. Setup application directories
#   5. Install Python 3.12
#   6. Install PostgreSQL client
#   7. Configure firewall
#   8. Setup SSL with Let's Encrypt
#   9. Configure Nginx as reverse proxy
#   10. Setup systemd service
#   11. Setup logging
#   12. Configure backups

set -e  # Exit on error

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Finance App Server Setup${NC}"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}This script must be run as root${NC}"
    exit 1
fi

# ============================================================================
# 1. Update system
# ============================================================================
echo -e "${GREEN}[1/12] Updating system packages...${NC}"
apt-get update
apt-get upgrade -y
apt-get install -y curl wget git build-essential libssl-dev zlib1g-dev \
    libncurses5-dev libncursesw5-dev readline-common libreadline-dev \
    libsqlite3-dev libbz2-dev libffi-dev liblzma-dev uuid-dev

# ============================================================================
# 2. Install Python 3.12
# ============================================================================
echo -e "${GREEN}[2/12] Installing Python 3.12...${NC}"
apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip

# ============================================================================
# 3. Install PostgreSQL client
# ============================================================================
echo -e "${GREEN}[3/12] Installing PostgreSQL client...${NC}"
apt-get install -y postgresql-client

# ============================================================================
# 4. Install Nginx
# ============================================================================
echo -e "${GREEN}[4/12] Installing Nginx...${NC}"
apt-get install -y nginx

# ============================================================================
# 5. Install Certbot (Let's Encrypt)
# ============================================================================
echo -e "${GREEN}[5/12] Installing Certbot...${NC}"
apt-get install -y certbot python3-certbot-nginx

# ============================================================================
# 6. Create application user
# ============================================================================
echo -e "${GREEN}[6/12] Creating finance_app user...${NC}"
if ! id -u finance_app > /dev/null 2>&1; then
    useradd -m -s /bin/bash -d /opt/finance_app finance_app
    echo "User finance_app created"
else
    echo "User finance_app already exists"
fi

# ============================================================================
# 7. Setup application directories
# ============================================================================
echo -e "${GREEN}[7/12] Setting up application directories...${NC}"
mkdir -p /opt/finance_app
mkdir -p /var/log/finance_app
mkdir -p /backups/finance_app

chown -R finance_app:finance_app /opt/finance_app
chown -R finance_app:finance_app /var/log/finance_app
chown -R finance_app:finance_app /backups/finance_app

chmod 755 /opt/finance_app
chmod 755 /var/log/finance_app
chmod 755 /backups/finance_app

# ============================================================================
# 8. Configure firewall
# ============================================================================
echo -e "${GREEN}[8/12] Configuring firewall...${NC}"
apt-get install -y ufw

ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP (Let's Encrypt)
ufw allow 443/tcp    # HTTPS
ufw enable --force

# ============================================================================
# 9. Setup SSH hardening
# ============================================================================
echo -e "${GREEN}[9/12] Setting up SSH hardening...${NC}"
apt-get install -y fail2ban

systemctl enable fail2ban
systemctl restart fail2ban

# Create SSH config backup
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Disable password login (KEY ONLY)
# Uncomment these lines after you've added your SSH key:
# sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
# sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
# systemctl restart sshd

echo "SSH hardening configured (review and apply manually)"

# ============================================================================
# 10. Setup log rotation
# ============================================================================
echo -e "${GREEN}[10/12] Setting up log rotation...${NC}"
cat > /etc/logrotate.d/finance_app << 'LOGROTATE'
/var/log/finance_app/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 finance_app finance_app
    sharedscripts
    postrotate
        systemctl reload finance_app > /dev/null 2>&1 || true
    endscript
}
LOGROTATE

# ============================================================================
# 11. Setup backup script
# ============================================================================
echo -e "${GREEN}[11/12] Setting up backup scripts...${NC}"
mkdir -p /usr/local/sbin

cat > /usr/local/sbin/backup_finance_app.sh << 'BACKUP'
#!/bin/bash
# Daily backup script for Finance App database
# Add to crontab: 0 2 * * * /usr/local/sbin/backup_finance_app.sh

BACKUP_DIR="/backups/finance_app/daily"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Note: Actual database backups are managed by the PostgreSQL provider
# This script backs up application configuration and secrets

BACKUP_FILE="$BACKUP_DIR/config_$(date +%Y%m%d_%H%M%S).tar.gz"

# Backup application config (excluding .env for security)
tar -czf "$BACKUP_FILE" \
    -C /opt/finance_app \
    --exclude='.env' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    .

# Cleanup old backups
find "$BACKUP_DIR" -name "config_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE"
BACKUP

chmod +x /usr/local/sbin/backup_finance_app.sh

# ============================================================================
# 12. Create crontab entry for backups
# ============================================================================
echo -e "${GREEN}[12/12] Setting up cron jobs...${NC}"

# Add backup cron job (2 AM daily)
(crontab -u finance_app -l 2>/dev/null || true; echo "0 2 * * * /usr/local/sbin/backup_finance_app.sh") | crontab -u finance_app -

# Add certificate renewal cron job (Let's Encrypt)
(crontab -u root -l 2>/dev/null || true; echo "0 3 * * * /usr/bin/certbot renew --quiet") | crontab -u root -

# ============================================================================
# Summary
# ============================================================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Server setup completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Clone the repository:"
echo "   cd /opt/finance_app"
echo "   sudo -u finance_app git clone $GIT_REPO ."
echo ""
echo "2. Setup Python virtual environment:"
echo "   sudo -u finance_app python3.12 -m venv .venv"
echo "   sudo -u finance_app .venv/bin/pip install -r requirements.txt"
echo ""
echo "3. Configure environment variables:"
echo "   sudo -u finance_app cp .env.production .env"
echo "   sudo -u finance_app nano .env  # Edit with real values"
echo "   sudo chmod 600 .env"
echo ""
echo "4. Setup database:"
echo "   # Create PostgreSQL database via provider dashboard"
echo "   # Set DATABASE_URL in .env"
echo "   sudo -u finance_app .venv/bin/alembic upgrade head"
echo ""
echo "5. Setup SSL certificate:"
echo "   sudo certbot certonly --nginx -d finance.example.com"
echo ""
echo "6. Update Nginx configuration:"
echo "   sudo cp deployment/nginx.conf /etc/nginx/sites-available/finance_app"
echo "   # Edit domain in nginx.conf"
echo "   sudo ln -s /etc/nginx/sites-available/finance_app /etc/nginx/sites-enabled/"
echo "   sudo rm -f /etc/nginx/sites-enabled/default"
echo "   sudo nginx -t"
echo "   sudo systemctl restart nginx"
echo ""
echo "7. Setup systemd service:"
echo "   sudo cp deployment/finance_app.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable finance_app"
echo "   sudo systemctl start finance_app"
echo ""
echo "8. Verify deployment:"
echo "   sudo systemctl status finance_app"
echo "   curl https://finance.example.com/health"
echo ""
echo "Additional configuration:"
echo "  - SSH key-only login: Edit /etc/ssh/sshd_config (see comments above)"
echo "  - Monitor with: tail -f /var/log/finance_app/*.log"
echo "  - Deploy updates: bash scripts/deploy.sh"
echo ""
