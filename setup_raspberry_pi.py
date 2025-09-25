#!/usr/bin/env python3
"""
Raspberry Pi Setup Script for WhatsApp Campaigns Automation
Run this script after cloning the repository to your Raspberry Pi
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class RaspberryPiSetup:
    def __init__(self):
        self.project_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.project_dir / "venv"
        self.automation_script = self.project_dir / "run_whatsapp_campaigns.py"

    def print_step(self, step_num, description):
        """Print step with formatting"""
        print(f"\n{'='*60}")
        print(f"STEP {step_num}: {description}")
        print('='*60)

    def run_command(self, cmd, description="", check=True):
        """Run shell command with error handling"""
        print(f"Running: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, check=check, text=True, capture_output=True)
            if result.stdout:
                print(f"Output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"ERROR: {description} failed")
            print(f"Command: {cmd}")
            print(f"Exit code: {e.returncode}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            return None

    def check_system(self):
        """Check system requirements"""
        self.print_step(1, "CHECKING SYSTEM REQUIREMENTS")

        print(f"Python version: {sys.version}")
        print(f"Platform: {platform.platform()}")
        print(f"Project directory: {self.project_dir}")

        # Check if we're on a Raspberry Pi
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'Raspberry Pi' in cpuinfo:
                    print("✓ Running on Raspberry Pi")
                else:
                    print("⚠ Warning: Not detected as Raspberry Pi, but continuing...")
        except FileNotFoundError:
            print("⚠ Warning: Cannot determine if running on Raspberry Pi")

        # Check Python version
        if sys.version_info < (3, 7):
            print("❌ ERROR: Python 3.7 or higher is required")
            return False

        print("✓ System check passed")
        return True

    def update_system(self):
        """Update system packages"""
        self.print_step(2, "UPDATING SYSTEM PACKAGES")

        print("Updating package lists...")
        result = self.run_command("sudo apt update", "Package update", check=False)
        if result and result.returncode != 0:
            print("⚠ Warning: apt update had issues, continuing...")

        print("Installing required system packages...")
        packages = ["python3-pip", "python3-venv", "git"]
        for package in packages:
            result = self.run_command(f"dpkg -l | grep -q {package}", check=False)
            if result and result.returncode == 0:
                print(f"✓ {package} already installed")
            else:
                print(f"Installing {package}...")
                self.run_command(f"sudo apt install -y {package}", f"Install {package}")

        print("✓ System packages updated")

    def setup_virtual_environment(self):
        """Set up Python virtual environment"""
        self.print_step(3, "SETTING UP VIRTUAL ENVIRONMENT")

        if self.venv_dir.exists():
            print("Virtual environment already exists, removing and recreating...")
            self.run_command(f"rm -rf {self.venv_dir}", "Remove existing venv")

        print("Creating virtual environment...")
        result = self.run_command(f"python3 -m venv {self.venv_dir}", "Create virtual environment")
        if not result:
            return False

        # Install automation script requirements
        pip_path = self.venv_dir / "bin" / "pip"
        automation_req = self.project_dir / "requirements-automation.txt"

        if automation_req.exists():
            print("Installing automation script requirements...")
            self.run_command(f"{pip_path} install -r {automation_req}", "Install automation requirements")
        else:
            print("Installing psutil directly...")
            self.run_command(f"{pip_path} install psutil", "Install psutil")

        # Install WhatsApp agent requirements
        whatsapp_req = self.project_dir / "whatsapp-agent" / "requirements.txt"
        if whatsapp_req.exists():
            print("Installing WhatsApp agent requirements...")
            self.run_command(f"{pip_path} install -r {whatsapp_req}", "Install WhatsApp requirements")
        else:
            print("⚠ Warning: whatsapp-agent/requirements.txt not found")

        # Install Google Sheets agent requirements
        sheets_req = self.project_dir / "google-sheets-agent" / "requirements.txt"
        if sheets_req.exists():
            print("Installing Google Sheets agent requirements...")
            self.run_command(f"{pip_path} install -r {sheets_req}", "Install Sheets requirements")
        else:
            print("⚠ Warning: google-sheets-agent/requirements.txt not found")

        print("✓ Virtual environment setup complete")
        return True

    def setup_git_credentials(self):
        """Set up Git credentials for auto-updates"""
        self.print_step(4, "SETTING UP GIT CREDENTIALS")

        # Check if git is already configured
        result = self.run_command("git config --global user.name", check=False)
        if result and result.stdout.strip():
            print(f"✓ Git user.name already set: {result.stdout.strip()}")
        else:
            print("\nGit user.name not configured.")
            print("The automation script needs git configured for auto-updates.")
            print("You can set it up later with: git config --global user.name 'Your Name'")

        result = self.run_command("git config --global user.email", check=False)
        if result and result.stdout.strip():
            print(f"✓ Git user.email already set: {result.stdout.strip()}")
        else:
            print("Git user.email not configured.")
            print("You can set it up later with: git config --global user.email 'your.email@example.com'")

        # Check for SSH key or suggest HTTPS with token
        ssh_key_path = Path.home() / ".ssh" / "id_rsa"
        if ssh_key_path.exists():
            print("✓ SSH key found for Git authentication")
        else:
            print("\n⚠ No SSH key found. For auto-updates, you'll need either:")
            print("  1. Generate SSH key: ssh-keygen -t rsa -b 4096 -C 'your.email@example.com'")
            print("  2. Or use HTTPS with personal access token")
            print("  3. Or disable auto-updates in the script")

        print("✓ Git credentials check complete")

    def make_executable(self):
        """Make the automation script executable"""
        self.print_step(5, "MAKING SCRIPTS EXECUTABLE")

        self.run_command(f"chmod +x {self.automation_script}", "Make automation script executable")
        print(f"✓ {self.automation_script.name} is now executable")

    def test_automation_script(self):
        """Test the automation script"""
        self.print_step(6, "TESTING AUTOMATION SCRIPT")

        print("Testing the automation script (dry run check)...")

        # Just test that the script loads without errors
        python_path = self.venv_dir / "bin" / "python"
        test_cmd = f"{python_path} -c 'import sys; sys.path.insert(0, \"{self.project_dir}\"); from run_whatsapp_campaigns import WhatsAppCampaignRunner; print(\"Script loads successfully\")'"

        result = self.run_command(test_cmd, "Test script loading", check=False)

        if result and result.returncode == 0:
            print("✓ Automation script loads successfully")
        else:
            print("⚠ Warning: Automation script test failed")
            print("The script may still work, but check dependencies")


    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 RASPBERRY PI SETUP FOR WHATSAPP CAMPAIGNS AUTOMATION")
        print(f"Project directory: {self.project_dir}")

        try:
            # Run setup steps
            if not self.check_system():
                return False

            self.update_system()

            if not self.setup_virtual_environment():
                return False

            self.setup_git_credentials()
            self.make_executable()
            self.test_automation_script()

            print("\n" + "="*60)
            print("🎉 SETUP COMPLETE!")
            print("="*60)
            print(f"✓ Virtual environment created at: {self.venv_dir}")
            print(f"✓ Automation script ready at: {self.automation_script}")
            print("✓ All dependencies installed")
            print()
            print("NEXT STEPS:")
            print("1. Configure git credentials if needed")
            print("2. Set up SSH key or personal access token for GitHub")
            print("3. Test run the script manually first:")
            print(f"   {self.automation_script}")
            print()
            print("For support, check the logs directory after running.")

            return True

        except KeyboardInterrupt:
            print("\n\n❌ Setup interrupted by user")
            return False
        except Exception as e:
            print(f"\n\n❌ Setup failed with error: {e}")
            return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Raspberry Pi Setup Script for WhatsApp Campaigns")
        print("Usage: python3 setup_raspberry_pi.py")
        print("\nThis script will:")
        print("- Update system packages")
        print("- Create virtual environment")
        print("- Install all dependencies")
        print("- Configure the automation script")
        sys.exit(0)

    setup = RaspberryPiSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)