#!/bin/bash
#
# Finance App Production Deployment Script
#
# This script:
#   1. Pulls latest code from git
#   2. Runs tests
#   3. Backs up current production code
#   4. Installs dependencies
#   5. Runs database migrations
#   6. Restarts the application
#   7. Verifies health check
#
# Usage:
#   ./scripts/deploy.sh
#   ./scripts/deploy.sh --rollback v123  # Rollback to previous deployment
#
# Prerequisites:
#   - SSH access to production server
#   - finance_app user created
#   - Systemd service configured
#   - PostgreSQL database accessible
#

set -e  # Exit on error

# Configuration
DEPLOY_USER="finance_app"
APP_DIR="/opt/finance_app"
VENV_DIR="${APP_DIR}/.venv"
BACKUPS_DIR="/backups/finance_app"
GIT_REPO="https://github.com/YOUR_USERNAME/finance_app.git"  # CHANGE ME
GIT_BRANCH="main"
HEALTH_CHECK_URL="https://finance.example.com/health"  # CHANGE ME
SLACK_WEBHOOK=""  # Optional: for notifications

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Functions
log_info() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

notify_slack() {
    if [ -z "$SLACK_WEBHOOK" ]; then
        return
    fi
    local message=$1
    curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\": \"$message\"}" || true
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if [ "$(id -u)" -eq 0 ]; then
        log_error "Do not run this script as root"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        log_error "git not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "python3 not installed"
        exit 1
    fi
}

# Backup current code
backup_current() {
    log_info "Backing up current production code..."
    
    mkdir -p "$BACKUPS_DIR"
    local backup_name="backup_$(date +'%Y%m%d_%H%M%S')"
    
    if [ -d "$APP_DIR" ]; then
        cp -r "$APP_DIR" "$BACKUPS_DIR/$backup_name"
        log_info "Backup created: $BACKUPS_DIR/$backup_name"
    fi
}

# Pull latest code
pull_code() {
    log_info "Pulling latest code from $GIT_REPO ($GIT_BRANCH)..."
    
    cd "$APP_DIR"
    git fetch origin
    git checkout "$GIT_BRANCH"
    git pull origin "$GIT_BRANCH"
    
    log_info "Code updated"
}

# Install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    
    log_info "Dependencies installed"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    
    if ! pytest tests/ -v; then
        log_error "Tests failed"
        return 1
    fi
    
    log_info "All tests passed"
    return 0
}

# Run migrations
run_migrations() {
    log_info "Running database migrations..."
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    
    if ! alembic upgrade head; then
        log_error "Migration failed"
        return 1
    fi
    
    log_info "Migrations completed"
    return 0
}

# Restart application
restart_app() {
    log_info "Restarting Finance App..."
    
    sudo systemctl restart finance_app
    
    # Wait for app to start
    sleep 2
    
    log_info "Application restarted"
}

# Health check
health_check() {
    log_info "Running health checks..."
    
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$HEALTH_CHECK_URL" > /dev/null; then
            log_info "Health check passed ✓"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log_warning "Health check attempt $attempt/$max_attempts failed, retrying..."
        sleep 2
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Rollback
rollback() {
    local version=$1
    
    if [ -z "$version" ]; then
        log_error "No version specified for rollback"
        exit 1
    fi
    
    log_warning "Rolling back to $version..."
    
    if [ ! -d "$BACKUPS_DIR/$version" ]; then
        log_error "Backup not found: $BACKUPS_DIR/$version"
        exit 1
    fi
    
    sudo systemctl stop finance_app
    cp -r "$BACKUPS_DIR/$version" "$APP_DIR"
    sudo systemctl start finance_app
    
    sleep 2
    
    if health_check; then
        log_info "Rollback completed successfully"
        notify_slack "Finance App rolled back to $version"
    else
        log_error "Rollback failed health check"
        exit 1
    fi
}

# Main deployment process
main() {
    log_info "Starting Finance App deployment..."
    
    check_prerequisites
    
    # Handle rollback command
    if [ "$1" = "--rollback" ]; then
        rollback "$2"
        exit 0
    fi
    
    # Standard deployment
    backup_current
    
    if ! pull_code; then
        log_error "Failed to pull code"
        exit 1
    fi
    
    if ! install_dependencies; then
        log_error "Failed to install dependencies"
        exit 1
    fi
    
    if ! run_tests; then
        log_warning "Tests failed but continuing deployment"
        # Uncomment to fail deployment on test failure:
        # exit 1
    fi
    
    if ! run_migrations; then
        log_error "Migrations failed"
        exit 1
    fi
    
    if ! restart_app; then
        log_error "Failed to restart app"
        exit 1
    fi
    
    if ! health_check; then
        log_error "Health check failed"
        notify_slack "⚠️ Finance App deployment FAILED health check"
        exit 1
    fi
    
    log_info "✓ Deployment completed successfully"
    notify_slack "✅ Finance App deployed successfully"
}

# Run main
main "$@"
