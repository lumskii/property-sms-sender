# Raspberry Pi Deployment Guide

This guide will help you deploy the WhatsApp campaigns automation system on a Raspberry Pi with automatic daily execution and GitHub updates.

## Prerequisites

- Raspberry Pi OS (Bullseye or newer)
- Python 3.8+
- Git
- Internet connection
- Chrome/Chromium browser

## Initial Setup

### 1. System Updates
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git chromium-browser -y
```

### 2. Clone Repository
```bash
cd ~
git clone https://github.com/vandanchopra/property-sms-sender.git
cd property-sms-sender
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r whatsapp-agent/requirements.txt
pip install -r google-sheets-agent/requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Add your configuration:
```
GOOGLE_APPSPOT_API_KEY=/path/to/your/service_account_key.json
# Add other environment variables as needed
```

### 5. Upload Google Service Account Key
- Upload your Google service account JSON file to the Pi
- Update the path in `.env` file
- Set proper permissions: `chmod 600 /path/to/service_account_key.json`

## WhatsApp Web Setup

### 1. Initial Chrome Profile Setup
```bash
# Run the script once to set up WhatsApp Web login
source venv/bin/activate
cd whatsapp-agent
python digital_greens_followup.py
```

- This will open Chrome and navigate to WhatsApp Web
- Scan QR code with your phone to login
- Close the browser after successful login
- The login session will be saved for future automated runs

## Automated Execution Setup

### 1. Make Shell Script Executable
```bash
chmod +x run_whatsapp_campaigns.sh
```

### 2. Test Manual Execution
```bash
# Test the automation script
./run_whatsapp_campaigns.sh
```

### 3. Setup Cron Job for Daily Execution
```bash
# Edit crontab
crontab -e

# Add this line for daily execution at 12:30 PM IST
30 12 * * * /home/pi/property-sms-sender/run_whatsapp_campaigns.sh >/dev/null 2>&1

# Or add this line to see output in logs
30 12 * * * /home/pi/property-sms-sender/run_whatsapp_campaigns.sh
```

### 4. Alternative: Systemd Service (Recommended)

Create systemd service file:
```bash
sudo nano /etc/systemd/system/whatsapp-campaigns.service
```

Add this content:
```ini
[Unit]
Description=WhatsApp Campaigns Daily Automation
After=network.target

[Service]
Type=oneshot
User=pi
WorkingDirectory=/home/pi/property-sms-sender
ExecStart=/home/pi/property-sms-sender/run_whatsapp_campaigns.sh
StandardOutput=append:/home/pi/property-sms-sender/logs/systemd.log
StandardError=append:/home/pi/property-sms-sender/logs/systemd.log

[Install]
WantedBy=multi-user.target
```

Create systemd timer:
```bash
sudo nano /etc/systemd/system/whatsapp-campaigns.timer
```

Add this content:
```ini
[Unit]
Description=Run WhatsApp Campaigns Daily
Requires=whatsapp-campaigns.service

[Timer]
OnCalendar=*-*-* 12:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-campaigns.timer
sudo systemctl start whatsapp-campaigns.timer

# Check status
sudo systemctl status whatsapp-campaigns.timer
```

## Monitoring and Logs

### 1. Log Files Location
```bash
# Campaign logs (daily rotation)
/home/pi/property-sms-sender/logs/campaigns_YYYYMMDD.log

# GitHub update logs
/home/pi/property-sms-sender/logs/github_updates.log

# Systemd logs (if using systemd)
/home/pi/property-sms-sender/logs/systemd.log
```

### 2. Check Current Status
```bash
# Check if script is running
ps aux | grep whatsapp_campaigns

# Check recent logs
tail -f logs/campaigns_$(date '+%Y%m%d').log

# Check systemd timer status
sudo systemctl status whatsapp-campaigns.timer
```

### 3. Manual Testing
```bash
# Test time restrictions (should exit if outside 11am-6pm IST)
cd whatsapp-agent
python digital_greens_followup.py

# Test full automation script
./run_whatsapp_campaigns.sh
```

## Troubleshooting

### 1. Chrome/Chromium Issues
If Chrome doesn't start properly:
```bash
# Install additional dependencies
sudo apt install chromium-chromedriver xvfb -y

# For headless operation, modify the Chrome options in whatsapp_messaging.py:
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")  # Only if running headless
```

### 2. WhatsApp Session Expired
- Delete the chrome profile: `rm -rf chrome_profile_for_whatsapp`
- Run the script manually to re-authenticate
- Scan QR code again with your phone

### 3. GitHub Update Issues
```bash
# Check git status
git status
git log --oneline -5

# Force update if needed
git fetch origin main
git reset --hard origin/main
```

### 4. Permission Issues
```bash
# Fix file permissions
chmod +x run_whatsapp_campaigns.sh
chmod 600 .env
chmod 600 /path/to/service_account_key.json
```

## Security Considerations

1. **Secure API Keys**: Ensure `.env` and service account files have restricted permissions
2. **Network Security**: Consider using VPN if accessing from public networks  
3. **Regular Updates**: The system automatically updates from GitHub daily
4. **Backup**: Regularly backup your configuration and chrome profile

## Features

✅ **Time-based Execution**: Only runs between 11am-6pm IST  
✅ **Daily Automation**: Runs once per day automatically  
✅ **GitHub Auto-updates**: Pulls latest code changes daily  
✅ **Duplicate Management**: Removes duplicates before sending  
✅ **Cross-campaign Deduplication**: Prevents duplicate messages across campaigns  
✅ **Rate Limiting**: Respects Google Sheets API limits  
✅ **Comprehensive Logging**: Detailed logs with timestamps  
✅ **Error Recovery**: Handles failures and continues operation  
✅ **Lock File Protection**: Prevents multiple instances  

## Support

For issues or questions:
1. Check the log files first
2. Ensure all dependencies are installed
3. Verify environment variables are set correctly
4. Test individual components manually before automated execution