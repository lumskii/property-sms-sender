#!/usr/bin/env python3
"""
WhatsApp Campaigns Automation Script
Runs both Digital Greens and Godrej Aristocrat campaigns
Includes GitHub auto-update functionality
"""

import os
import sys
import subprocess
import logging
import signal
import time
import psutil
import argparse
from datetime import datetime
from pathlib import Path


class WhatsAppCampaignRunner:
    def __init__(self, skip_business_hours=False):
        self.project_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.project_dir / "venv"
        self.log_dir = self.project_dir / "logs"
        self.lock_file = self.project_dir / "whatsapp_campaigns.lock"
        self.skip_business_hours = skip_business_hours

        # Create logs directory
        self.log_dir.mkdir(exist_ok=True)

        # Set up logging
        self.setup_logging()

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def setup_logging(self):
        """Set up logging configuration"""
        today = datetime.now().strftime('%Y%m%d')
        log_file = self.log_dir / f"campaigns_{today}.log"
        github_log_file = self.log_dir / "github_updates.log"

        # Main logger
        self.logger = logging.getLogger('campaigns')
        self.logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()

        # Formatter with IST timezone
        formatter = logging.Formatter('[%(asctime)s IST] %(message)s',
                                    datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # GitHub logger
        self.github_logger = logging.getLogger('github')
        self.github_logger.setLevel(logging.INFO)
        github_handler = logging.FileHandler(github_log_file)
        github_handler.setFormatter(formatter)
        self.github_logger.addHandler(github_handler)

    def log_message(self, message):
        """Log message with timestamp"""
        self.logger.info(message)

    def _signal_handler(self, signum, frame):
        """Handle cleanup on signals"""
        self.log_message(f"Received signal {signum}, cleaning up...")
        self.cleanup(130 if signum == signal.SIGINT else 143)

    def check_lock(self):
        """Check if another instance is already running"""
        if self.lock_file.exists():
            try:
                with open(self.lock_file, 'r') as f:
                    pid = int(f.read().strip())

                if psutil.pid_exists(pid):
                    self.log_message(f"Another instance is already running (PID: {pid}). Exiting.")
                    sys.exit(1)
                else:
                    self.log_message(f"Removing stale lock file (PID: {pid})")
                    self.lock_file.unlink()
            except (ValueError, FileNotFoundError):
                self.log_message("Removing invalid lock file")
                self.lock_file.unlink(missing_ok=True)

        # Create lock file with current PID
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))

    def cleanup(self, exit_code=0):
        """Cleanup function to remove lock file"""
        self.log_message("Cleaning up...")
        self.lock_file.unlink(missing_ok=True)
        sys.exit(exit_code)

    def run_command(self, cmd, cwd=None, capture_output=True):
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.project_dir,
                capture_output=capture_output,
                text=True,
                timeout=300
            )
            return result
        except subprocess.TimeoutExpired:
            self.log_message(f"Command timed out: {cmd}")
            return None
        except Exception as e:
            self.log_message(f"Command failed: {cmd}, Error: {e}")
            return None

    def check_github_updates(self):
        """Check for and apply GitHub updates"""
        self.log_message("Checking for GitHub updates...")

        # Fetch latest changes
        fetch_result = self.run_command("git fetch origin main")
        if fetch_result and fetch_result.stdout:
            self.github_logger.info(f"Git fetch output: {fetch_result.stdout}")

        # Get current and remote commit hashes
        local_commit_result = self.run_command("git rev-parse HEAD")
        remote_commit_result = self.run_command("git rev-parse origin/main")

        if not local_commit_result or not remote_commit_result:
            self.log_message("ERROR: Failed to get commit hashes")
            return False

        local_commit = local_commit_result.stdout.strip()
        remote_commit = remote_commit_result.stdout.strip()

        if local_commit != remote_commit:
            self.log_message(f"New updates found on GitHub. Current: {local_commit[:8]}, Remote: {remote_commit[:8]}")

            # Backup current version info
            self.github_logger.info(f"Pre-update commit: {local_commit}")
            self.github_logger.info(f"Update time: {datetime.now()}")

            # Pull latest changes
            self.log_message("Pulling latest changes from GitHub...")
            pull_result = self.run_command("git pull origin main")

            if pull_result and pull_result.returncode == 0:
                new_commit_result = self.run_command("git rev-parse HEAD")
                new_commit = new_commit_result.stdout.strip() if new_commit_result else "unknown"
                self.log_message(f"Successfully updated to commit: {new_commit[:8]}")

                if pull_result.stdout:
                    self.github_logger.info(f"Git pull output: {pull_result.stdout}")

                # Check if requirements changed
                diff_result = self.run_command(f"git diff --name-only {local_commit} {new_commit}")
                if diff_result and "requirements.txt" in diff_result.stdout:
                    self.log_message("Requirements files changed. Updating virtual environment...")
                    self.update_requirements()

                self.github_logger.info(f"Post-update commit: {new_commit}")
                self.github_logger.info("---")
                return True
            else:
                self.log_message("ERROR: Failed to pull updates from GitHub")
                return False
        else:
            self.log_message("Code is up to date. No updates needed.")
            return True

    def update_requirements(self):
        """Update virtual environment requirements"""
        if not self.venv_dir.exists():
            self.log_message("Virtual environment not found during requirements update")
            return False

        pip_path = self.venv_dir / "bin" / "pip"

        # Update whatsapp-agent requirements
        whatsapp_req = self.project_dir / "whatsapp-agent" / "requirements.txt"
        if whatsapp_req.exists():
            result = self.run_command(f"{pip_path} install -r {whatsapp_req}")
            if result and result.stdout:
                self.github_logger.info(f"WhatsApp requirements update: {result.stdout}")

        # Update google-sheets-agent requirements
        sheets_req = self.project_dir / "google-sheets-agent" / "requirements.txt"
        if sheets_req.exists():
            result = self.run_command(f"{pip_path} install -r {sheets_req}")
            if result and result.stdout:
                self.github_logger.info(f"Sheets requirements update: {result.stdout}")

        return True

    def activate_venv(self):
        """Activate or create virtual environment"""
        if not self.venv_dir.exists():
            self.log_message("Virtual environment not found. Creating new one...")

            # Create virtual environment
            result = self.run_command(f"python3 -m venv {self.venv_dir}")
            if not result or result.returncode != 0:
                self.log_message("ERROR: Failed to create virtual environment")
                return False

            # Install requirements
            pip_path = self.venv_dir / "bin" / "pip"

            whatsapp_req = self.project_dir / "whatsapp-agent" / "requirements.txt"
            if whatsapp_req.exists():
                self.run_command(f"{pip_path} install -r {whatsapp_req}")

            sheets_req = self.project_dir / "google-sheets-agent" / "requirements.txt"
            if sheets_req.exists():
                self.run_command(f"{pip_path} install -r {sheets_req}")
        else:
            self.log_message("Activating virtual environment...")

        return True

    def run_campaign(self, script_name, campaign_name):
        """Run a specific campaign script"""
        self.log_message(f"Starting {campaign_name} campaign...")

        python_path = self.venv_dir / "bin" / "python"
        script_path = self.project_dir / "whatsapp-agent" / script_name

        if not script_path.exists():
            self.log_message(f"ERROR: {script_name} not found")
            return False

        # Add business hours flag if specified
        cmd = f"{python_path} {script_name}"
        if self.skip_business_hours:
            cmd += " --skip-business-hours"

        result = self.run_command(
            cmd,
            cwd=self.project_dir / "whatsapp-agent",
            capture_output=False
        )

        if result and result.returncode == 0:
            self.log_message(f"{campaign_name} campaign completed successfully")
            return True
        else:
            exit_code = result.returncode if result else -1
            self.log_message(f"{campaign_name} campaign failed with exit code: {exit_code}")
            return False

    def run_digital_greens(self):
        """Run Digital Greens campaign"""
        return self.run_campaign("digital_greens_followup.py", "Digital Greens")

    def run_godrej_campaign(self):
        """Run Godrej Aristocrat campaign"""
        return self.run_campaign("Godrej_aristrocrat_followup.py", "Godrej Aristocrat")

    def main(self):
        """Main execution function"""
        self.log_message("=== WhatsApp Campaigns Automation Started ===")

        try:
            # Check if another instance is running
            self.check_lock()

            # Check for GitHub updates
            if not self.check_github_updates():
                self.log_message("WARNING: GitHub update check failed, continuing with current version")

            # Activate virtual environment
            if not self.activate_venv():
                self.log_message("ERROR: Failed to set up virtual environment")
                self.cleanup(1)

            # Run campaigns sequentially
            digital_greens_success = self.run_digital_greens()
            godrej_success = False

            if digital_greens_success:
                self.log_message("Waiting 2 minutes before starting Godrej campaign...")
                time.sleep(120)
                godrej_success = self.run_godrej_campaign()
            else:
                self.log_message("Skipping Godrej campaign due to Digital Greens failure")

            # Summary
            self.log_message("=== Campaign Summary ===")
            self.log_message(f"Digital Greens: {'SUCCESS' if digital_greens_success else 'FAILED'}")
            self.log_message(f"Godrej Aristocrat: {'SUCCESS' if godrej_success else 'FAILED'}")

            # Overall status
            if digital_greens_success and godrej_success:
                self.log_message("=== All campaigns completed successfully ===")
                self.cleanup(0)
            else:
                self.log_message("=== One or more campaigns failed ===")
                self.cleanup(1)

        except Exception as e:
            self.log_message(f"CRITICAL ERROR: {e}")
            self.cleanup(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WhatsApp Campaigns Automation")
    parser.add_argument('--business_hours_check',
                       choices=['true', 'false'],
                       default='true',
                       help='Enable or disable business hours check (default: true)')

    args = parser.parse_args()
    skip_business_hours = args.business_hours_check.lower() == 'false'

    if skip_business_hours:
        print("[INFO] Business hours check disabled - script will run at any time")

    runner = WhatsAppCampaignRunner(skip_business_hours=skip_business_hours)
    runner.main()