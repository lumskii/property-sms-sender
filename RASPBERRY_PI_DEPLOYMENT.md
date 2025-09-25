# Raspberry Pi Deployment Guide

## Quick Setup

After cloning this repository to your Raspberry Pi:

```bash
# Run the automated setup script
python3 setup_raspberry_pi.py
```

This will handle everything automatically and provide you with cron job instructions.

## Manual Setup (if needed)

### 1. System Requirements
- Raspberry Pi with Raspbian/Raspberry Pi OS
- Python 3.7+
- Internet connection for GitHub auto-updates

### 2. Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv git
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-automation.txt
pip install -r whatsapp-agent/requirements.txt
pip install -r google-sheets-agent/requirements.txt
```

### 4. Configure Git (for auto-updates)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set up SSH key for GitHub
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
# Add the public key to your GitHub account
```

### 5. Make Script Executable
```bash
chmod +x run_whatsapp_campaigns.py
```

### 6. Set Up Cron Job

For weekdays at 11:30 AM IST:

```bash
crontab -e
```

Add this line (assuming UTC timezone):
```
0 6 * * 1-5 /full/path/to/your/repo/run_whatsapp_campaigns.py
```

**Note:** Adjust the time based on your Pi's timezone:
- IST (UTC+5:30) → 11:30 AM IST = 6:00 AM UTC
- Check your timezone with: `timedatectl`

## Testing

### Test Manual Run
```bash
./run_whatsapp_campaigns.py
```

### Check Logs
```bash
# View today's campaign logs
tail -f logs/campaigns_$(date +%Y%m%d).log

# View GitHub update logs
tail -f logs/github_updates.log
```

### Verify Cron Job
```bash
# List cron jobs
crontab -l

# Check cron service status
sudo systemctl status cron

# View cron logs
sudo journalctl -u cron | tail -20
```

## File Structure After Setup

```
property-sms-sender/
├── run_whatsapp_campaigns.py        # Main automation script
├── requirements-automation.txt       # Dependencies for automation
├── setup_raspberry_pi.py            # Setup script
├── venv/                            # Virtual environment
├── logs/                            # Log files
│   ├── campaigns_YYYYMMDD.log      # Daily campaign logs
│   └── github_updates.log          # GitHub update logs
├── whatsapp-agent/                  # WhatsApp campaign scripts
└── google-sheets-agent/             # Google Sheets scripts
```

## Troubleshooting

### Script Won't Run
- Check file permissions: `ls -la run_whatsapp_campaigns.py`
- Verify Python path: `which python3`
- Check virtual environment: `source venv/bin/activate`

### Git Auto-Updates Failing
- Verify SSH key: `ssh -T git@github.com`
- Check Git configuration: `git config --list`
- Test manual pull: `git pull origin main`

### Cron Job Not Running
- Check cron service: `sudo systemctl status cron`
- Verify cron job syntax: `crontab -l`
- Check system timezone: `timedatectl`
- Review cron logs: `sudo journalctl -u cron`

### Campaign Failures
- Check individual campaign logs in the `logs/` directory
- Verify WhatsApp agent dependencies are installed
- Test campaigns manually from the `whatsapp-agent/` directory

## Monitoring

The automation script creates detailed logs:

- **Campaign Logs:** `logs/campaigns_YYYYMMDD.log` - Daily execution logs
- **GitHub Logs:** `logs/github_updates.log` - Auto-update activity
- **Lock Files:** `whatsapp_campaigns.lock` - Prevents duplicate runs

## Security Notes

- The script runs with your user permissions
- SSH keys are stored in `~/.ssh/`
- No sensitive data is logged
- Lock file prevents multiple simultaneous executions

## Support

If you encounter issues:
1. Check the log files first
2. Verify system requirements
3. Test components individually
4. Re-run the setup script if needed