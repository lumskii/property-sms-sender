from whatsapp_messaging import send_followup_messages
import sys
import os
import time
from datetime import datetime
import pytz
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'google-sheets-agent'))
from remove_duplicates import remove_duplicate_entries
from google_sheets_agent import get_google_sheet

def is_within_business_hours():
    """Check if current time is within business hours (11am-6pm IST)"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    current_hour = current_time.hour
    
    if 11 <= current_hour < 18:  # 11am to 6pm (18 is 6pm in 24hr format)
        return True, current_time
    else:
        return False, current_time

def log_with_timestamp(message):
    """Log message with IST timestamp"""
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')
    print(f"[{timestamp}] {message}")

def wait_for_business_hours():
    """Wait until business hours if currently outside the window"""
    is_business_hours, current_time = is_within_business_hours()
    
    if not is_business_hours:
        current_hour = current_time.hour
        if current_hour < 11:
            wait_minutes = (11 - current_hour) * 60 - current_time.minute
            log_with_timestamp(f"Too early (current time: {current_time.strftime('%H:%M')}). Waiting {wait_minutes} minutes until 11:00 AM...")
        else:  # current_hour >= 18
            # Wait until 11 AM next day
            hours_until_11am = (24 - current_hour + 11) % 24
            wait_minutes = hours_until_11am * 60 - current_time.minute
            log_with_timestamp(f"Too late (current time: {current_time.strftime('%H:%M')}). Waiting {wait_minutes} minutes until 11:00 AM tomorrow...")
        
        time.sleep(wait_minutes * 60)  # Convert minutes to seconds

if __name__ == '__main__':
    # --- CONFIGURATION ---
    automated_script_sending = True  # Set to True for automated daily runs
    
    # Define the columns in your Google Sheet
    worksheet_name = "IPC Outreach"
    send_column = 'Send Now'
    phone_column = 'Phone Number'
    message_column = 'Message to Send'
    contact_person_column = 'Contact Person'
    last_message_col = 'Last Message Sent'
    last_message_datetime_col = 'Last Message DateTime'
    
    # Define the value that triggers a message to be sent
    send_trigger_value = 'YES'
    message_send_limit = -1  # Limit the number of messages sent in one run, if needed and if the value is -1 then keep sending.
    pause_between_messages = 1 # Pause in seconds

    # --- END CONFIGURATION ---
    
    log_with_timestamp("=== Digital Greens Campaign Started ===")
    
    # Check if within business hours
    if automated_script_sending:
        is_business_hours, current_time = is_within_business_hours()
        if not is_business_hours:
            log_with_timestamp(f"Outside business hours (11am-6pm IST). Current time: {current_time.strftime('%H:%M:%S')}. Exiting.")
            exit(0)
        else:
            log_with_timestamp(f"Within business hours. Current time: {current_time.strftime('%H:%M:%S')}. Proceeding with campaign.")
    
    # Step 1: Remove duplicates from IPC Outreach worksheet
    log_with_timestamp("Step 1: Removing duplicates from IPC Outreach worksheet...")
    sheet = get_google_sheet()
    if sheet:
        remove_duplicate_entries(sheet, worksheet_name, phone_column, last_message_datetime_col, testing=False)
        log_with_timestamp("Duplicate removal completed.")
    else:
        log_with_timestamp("Could not connect to Google Sheet for duplicate removal. Proceeding with message sending...")
    
    # Step 2: Send messages
    log_with_timestamp("Step 2: Starting WhatsApp message sending process...")
    send_followup_messages(worksheet_name, send_column, phone_column, message_column, contact_person_column, 
                           last_message_col, last_message_datetime_col, send_trigger_value, message_send_limit,
                           pause_between_messages, testing=False)
    
    log_with_timestamp("=== Digital Greens Campaign Completed ===")
