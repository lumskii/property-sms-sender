from whatsapp_messaging import send_followup_messages
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'google-sheets-agent'))
from remove_duplicates import remove_duplicate_entries
from google_sheets_agent import get_google_sheet

if __name__ == '__main__':
    # --- CONFIGURATION ---
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
    
    # Step 1: Remove duplicates from IPC Outreach worksheet
    print("Step 1: Removing duplicates from IPC Outreach worksheet...")
    sheet = get_google_sheet()
    if sheet:
        remove_duplicate_entries(sheet, worksheet_name, phone_column, last_message_datetime_col, testing=False)
        print("Duplicate removal completed.\n")
    else:
        print("Could not connect to Google Sheet for duplicate removal. Proceeding with message sending...")
    
    # Step 2: Send messages
    print("Step 2: Starting WhatsApp message sending process...")
    send_followup_messages(worksheet_name, send_column, phone_column, message_column, contact_person_column, 
                           last_message_col, last_message_datetime_col, send_trigger_value, message_send_limit,
                           pause_between_messages, testing=False)
