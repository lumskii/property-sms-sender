#!/usr/bin/env python
"""
Quick test script to send a WhatsApp message with attachment
"""

from whatsapp_messaging import send_followup_messages
import pandas as pd
import sys
import os

# Test data
test_data = {
    'Send Now': ['YES'],
    'Phone Number': ['9810101049'],
    'Message to Send': ['Hi this is a test message Attachments: [https://drive.google.com/file/d/13zeb-PZkGFEBbtS8NrlKsNIoPyviH8aV/view?usp=drive_link]'],
    'Contact Person': ['Test User'],
    'Last Message Sent': [''],
    'Last Message DateTime': ['']
}

# Create a temporary CSV for testing
df = pd.DataFrame(test_data)
temp_csv = 'temp_test_data.csv'
df.to_csv(temp_csv, index=False)

print("=" * 60)
print("TESTING WHATSAPP ATTACHMENT SENDING")
print("=" * 60)
print(f"Phone: +919810101049")
print(f"Message: Hi this is a test message")
print(f"Attachment: https://drive.google.com/file/d/13zeb-PZkGFEBbtS8NrlKsNIoPyviH8aV/view?usp=drive_link")
print("=" * 60)

try:
    # This will use the existing Google Sheets integration, but we'll override with our test data
    # For now, let's just call the function directly with test parameters
    
    # Import required modules
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'google-sheets-agent'))
    
    # We'll create a mock by directly calling the underlying send logic
    # But first, let's use a simpler approach - just import and test
    
    from whatsapp_messaging import send_single_whatsapp_message_with_attachments
    
except ImportError:
    print("\n⚠️  Direct function not available. Using full send_followup_messages instead.\n")
    
    # Create a simple wrapper
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Note: This approach would require creating a test Google Sheet
    print("For this test, please add the following to your Google Sheet:")
    print("- Phone Number: 9810101049")
    print("- Send Now: YES")
    print("- Message: Hi this is a test message Attachments: [https://drive.google.com/file/d/13zeb-PZkGFEBbtS8NrlKsNIoPyviH8aV/view?usp=drive_link]")
    print("\nThen run: python digital_greens_followup.py --force")

# Clean up
if os.path.exists(temp_csv):
    os.remove(temp_csv)

print("\n✅ Test setup complete. Please ensure your test data is in the Google Sheet and run with --force flag.")
