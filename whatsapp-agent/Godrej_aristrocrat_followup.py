from whatsapp_messaging import send_followup_messages
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'google-sheets-agent'))
from remove_duplicates import remove_duplicate_entries, remove_cross_sheet_duplicates
from google_sheets_agent import get_google_sheet

if __name__ == '__main__':
    # --- CONFIGURATION ---
    # Define the columns in your Google Sheet
    worksheet_name = "AnarockGodrejList"
    send_column = 'Send Now'
    phone_column = 'Phone Number'
    message_column = 'Message to Send'
    contact_person_column = 'Contact Person'
    last_message_col = 'Last Message Sent'
    last_message_datetime_col = 'Last Message DateTime'
    
    # Define the value that triggers a message to be sent
    send_trigger_value = 'YES'
    message_send_limit = -1
    pause_between_messages = 1 # Pause in seconds
    
    # --- END CONFIGURATION ---
    
    # Step 1: Remove duplicates from AnarockGodrejList worksheet
    print("Step 1: Removing internal duplicates from AnarockGodrejList worksheet...")
    sheet = get_google_sheet()
    if sheet:
        remove_duplicate_entries(sheet, worksheet_name, phone_column, last_message_datetime_col, testing=False)
        print("Internal duplicate removal completed.")
        
        # Step 2: Remove cross-sheet duplicates (remove from AnarockGodrejList if exists in IPC Outreach)
        print("\nStep 2: Removing cross-sheet duplicates (AnarockGodrejList numbers that exist in IPC Outreach)...")
        remove_cross_sheet_duplicates(sheet, 'IPC Outreach', worksheet_name, phone_column, testing=False)
        print("Cross-sheet duplicate removal completed.\n")
    else:
        print("Could not connect to Google Sheet for duplicate removal. Proceeding with message sending...")
    
    # Step 3: Send messages
    print("Step 3: Starting WhatsApp message sending process...")
    send_followup_messages(worksheet_name, send_column, phone_column, message_column, contact_person_column, 
                           last_message_col, last_message_datetime_col, send_trigger_value, message_send_limit, 
                           pause_between_messages, testing=False)
