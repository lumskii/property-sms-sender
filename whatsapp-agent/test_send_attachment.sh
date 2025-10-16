#!/bin/bash
# Quick test script for sending WhatsApp message with attachment

echo "=================================================="
echo "WhatsApp Attachment Test"
echo "=================================================="
echo ""
echo "Test Details:"
echo "  Phone: +919810101049"
echo "  Message: Hi this is a test message"
echo "  Attachment: Google Drive image"
echo ""
echo "=================================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated. Activating now..."
    cd /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/property-sms-sender
    source venv/bin/activate
fi

# Navigate to whatsapp-agent directory
cd /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/property-sms-sender/whatsapp-agent

echo "📋 INSTRUCTIONS:"
echo ""
echo "1. Make sure your Google Sheet has a row with:"
echo "   - Phone Number: 9810101049"
echo "   - Send Now: YES"
echo "   - Message to Send: Hi this is a test message Attachments: [https://drive.google.com/file/d/13zeb-PZkGFEBbtS8NrlKsNIoPyviH8aV/view?usp=drive_link]"
echo ""
echo "2. This script will now run the campaign with --force flag"
echo ""
echo "=================================================="
echo ""

read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "🚀 Starting WhatsApp campaign..."
echo ""

python digital_greens_followup.py --force

echo ""
echo "=================================================="
echo "Test complete!"
echo "=================================================="
