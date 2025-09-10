#!/bin/bash

# WhatsApp Campaigns Automation Script
# Runs both Digital Greens and Godrej Aristocrat campaigns
# Includes GitHub auto-update functionality

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
LOCK_FILE="$PROJECT_DIR/whatsapp_campaigns.lock"
LOG_FILE="$LOG_DIR/campaigns_$(date '+%Y%m%d').log"
GITHUB_UPDATE_LOG="$LOG_DIR/github_updates.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S IST')] $1" | tee -a "$LOG_FILE"
}

# Function to check if script is already running
check_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local pid=$(cat "$LOCK_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log_message "Another instance is already running (PID: $pid). Exiting."
            exit 1
        else
            log_message "Removing stale lock file (PID: $pid)"
            rm -f "$LOCK_FILE"
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

# Function to cleanup on exit
cleanup() {
    log_message "Cleaning up..."
    rm -f "$LOCK_FILE"
    exit $1
}

# Function to check for GitHub updates
check_github_updates() {
    log_message "Checking for GitHub updates..."
    cd "$PROJECT_DIR"
    
    # Fetch latest changes
    git fetch origin main 2>&1 | tee -a "$GITHUB_UPDATE_LOG"
    
    # Get current and remote commit hashes
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/main)
    
    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        log_message "New updates found on GitHub. Current: ${LOCAL_COMMIT:0:8}, Remote: ${REMOTE_COMMIT:0:8}"
        
        # Backup current version info
        echo "Pre-update commit: $LOCAL_COMMIT" >> "$GITHUB_UPDATE_LOG"
        echo "Update time: $(date)" >> "$GITHUB_UPDATE_LOG"
        
        # Pull latest changes
        log_message "Pulling latest changes from GitHub..."
        git pull origin main 2>&1 | tee -a "$GITHUB_UPDATE_LOG"
        
        if [ $? -eq 0 ]; then
            NEW_COMMIT=$(git rev-parse HEAD)
            log_message "Successfully updated to commit: ${NEW_COMMIT:0:8}"
            
            # Update virtual environment if requirements changed
            if git diff --name-only "$LOCAL_COMMIT" "$NEW_COMMIT" | grep -q "requirements.txt"; then
                log_message "Requirements files changed. Updating virtual environment..."
                source "$VENV_DIR/bin/activate"
                pip install -r whatsapp-agent/requirements.txt 2>&1 | tee -a "$GITHUB_UPDATE_LOG"
                pip install -r google-sheets-agent/requirements.txt 2>&1 | tee -a "$GITHUB_UPDATE_LOG"
            fi
            
            echo "Post-update commit: $NEW_COMMIT" >> "$GITHUB_UPDATE_LOG"
            echo "---" >> "$GITHUB_UPDATE_LOG"
        else
            log_message "ERROR: Failed to pull updates from GitHub"
            return 1
        fi
    else
        log_message "Code is up to date. No updates needed."
    fi
    
    return 0
}

# Function to activate virtual environment
activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        log_message "Virtual environment not found. Creating new one..."
        python3 -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        pip install -r whatsapp-agent/requirements.txt
        pip install -r google-sheets-agent/requirements.txt
    else
        log_message "Activating virtual environment..."
        source "$VENV_DIR/bin/activate"
    fi
}

# Function to run Digital Greens campaign
run_digital_greens() {
    log_message "Starting Digital Greens campaign..."
    cd "$PROJECT_DIR/whatsapp-agent"
    python digital_greens_followup.py 2>&1 | tee -a "$LOG_FILE"
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        log_message "Digital Greens campaign completed successfully"
    else
        log_message "Digital Greens campaign failed with exit code: $exit_code"
    fi
    return $exit_code
}

# Function to run Godrej campaign
run_godrej_campaign() {
    log_message "Starting Godrej Aristocrat campaign..."
    cd "$PROJECT_DIR/whatsapp-agent"
    python Godrej_aristrocrat_followup.py 2>&1 | tee -a "$LOG_FILE"
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        log_message "Godrej Aristocrat campaign completed successfully"
    else
        log_message "Godrej Aristocrat campaign failed with exit code: $exit_code"
    fi
    return $exit_code
}

# Main execution
main() {
    log_message "=== WhatsApp Campaigns Automation Started ==="
    
    # Set up signal handlers for cleanup
    trap 'cleanup $?' EXIT
    trap 'cleanup 130' INT
    trap 'cleanup 143' TERM
    
    # Check if another instance is running
    check_lock
    
    # Check for GitHub updates
    if ! check_github_updates; then
        log_message "WARNING: GitHub update check failed, continuing with current version"
    fi
    
    # Activate virtual environment
    activate_venv
    
    # Run campaigns sequentially
    local digital_greens_status=0
    local godrej_status=0
    
    # Run Digital Greens campaign
    run_digital_greens
    digital_greens_status=$?
    
    # Wait 2 minutes between campaigns to avoid overwhelming the system
    if [ $digital_greens_status -eq 0 ]; then
        log_message "Waiting 2 minutes before starting Godrej campaign..."
        sleep 120
        
        # Run Godrej campaign
        run_godrej_campaign
        godrej_status=$?
    else
        log_message "Skipping Godrej campaign due to Digital Greens failure"
    fi
    
    # Summary
    log_message "=== Campaign Summary ==="
    log_message "Digital Greens: $([ $digital_greens_status -eq 0 ] && echo "SUCCESS" || echo "FAILED")"
    log_message "Godrej Aristocrat: $([ $godrej_status -eq 0 ] && echo "SUCCESS" || echo "FAILED")"
    
    # Overall status
    if [ $digital_greens_status -eq 0 ] && [ $godrej_status -eq 0 ]; then
        log_message "=== All campaigns completed successfully ==="
        cleanup 0
    else
        log_message "=== One or more campaigns failed ==="
        cleanup 1
    fi
}

# Run main function
main "$@"