from google_sheets_agent import get_google_sheet
import pandas as pd
import gspread
from datetime import datetime
import time

# Rate limiting variables
request_count = 0
request_start_time = time.time()
MAX_REQUESTS_PER_MINUTE = 40

def check_rate_limit():
    """Check if we're approaching rate limits and pause if necessary"""
    global request_count, request_start_time
    
    current_time = time.time()
    time_elapsed = current_time - request_start_time
    
    # If more than a minute has passed, reset the counter
    if time_elapsed >= 60:
        request_count = 0
        request_start_time = current_time
    
    # If we're approaching the limit, take a break
    if request_count >= MAX_REQUESTS_PER_MINUTE:
        remaining_time = 60 - time_elapsed
        if remaining_time > 0:
            print(f"⏸️  Taking a 1-minute breather to avoid hitting Google Sheets API rate limits...")
            print(f"   (Made {request_count} requests, waiting {remaining_time:.0f} seconds)")
            time.sleep(remaining_time + 5)  # Add 5 seconds buffer
        
        # Reset counters after the break
        request_count = 0
        request_start_time = time.time()
        print("✅ Resuming operations...")

def increment_request_count():
    """Increment the request counter for rate limiting"""
    global request_count
    request_count += 1

def remove_duplicate_entries(sheet, sheet_name, phone_column, datetime_column='Last Message DateTime', testing=False):
    """
    Removes duplicate phone number entries, keeping only the one with the latest datetime.
    """
    try:
        worksheet = sheet.worksheet(sheet_name)
        
        # Get all data from the worksheet
        all_data = worksheet.get_all_records()
        if not all_data:
            print("No data found in the worksheet.")
            return
        
        df = pd.DataFrame(all_data)
        
        # Check if required columns exist
        if phone_column not in df.columns:
            print(f"Error: Column '{phone_column}' not found in the worksheet.")
            return
        
        if datetime_column not in df.columns:
            print(f"Error: Column '{datetime_column}' not found in the worksheet.")
            return
        
        # Convert datetime column to proper datetime format, handling empty/invalid values
        def parse_datetime(dt_str):
            if pd.isna(dt_str) or str(dt_str).strip() == '':
                return datetime.min  # Use minimum datetime for empty values
            try:
                return pd.to_datetime(str(dt_str))
            except:
                return datetime.min
        
        df[datetime_column] = df[datetime_column].apply(parse_datetime)
        
        # Find duplicates based on phone column
        phone_duplicates = df[df.duplicated(subset=[phone_column], keep=False)]
        
        if phone_duplicates.empty:
            print("No duplicate phone numbers found.")
            return
        
        print(f"Found {len(phone_duplicates)} duplicate entries for phone numbers:")
        for phone in phone_duplicates[phone_column].unique():
            print(f"  - {phone}")
        
        # For each group of duplicates, keep only the one with the latest datetime
        rows_to_delete = []
        for phone in phone_duplicates[phone_column].unique():
            duplicate_group = df[df[phone_column] == phone].copy()
            # Sort by datetime descending to get the latest first
            duplicate_group = duplicate_group.sort_values(by=datetime_column, ascending=False)
            # Mark all but the first (latest) for deletion
            rows_to_delete.extend(duplicate_group.index[1:].tolist())
        
        if not rows_to_delete:
            print("No rows to delete.")
            return
        
        print(f"Will delete {len(rows_to_delete)} duplicate rows.")
        
        if testing:
            print(f"\nTESTING MODE: About to delete rows from sheet '{sheet_name}', column '{phone_column}':")
            for row_index in sorted(rows_to_delete, reverse=True):
                actual_row_number = row_index + 2
                phone_value = df.iloc[row_index][phone_column]
                datetime_value = df.iloc[row_index][datetime_column]
                print(f"  Row {actual_row_number}: Phone={phone_value}, DateTime={datetime_value}")
            
            confirmation = input("\nProceed with deletion? (Y/N): ").strip().upper()
            if confirmation != 'Y':
                print("Deletion cancelled.")
                return
        
        # Sort in descending order to delete from bottom up (to maintain row indices)
        rows_to_delete.sort(reverse=True)
        
        # Delete the rows (adding 2 because: 1 for header row, 1 for 0-based to 1-based conversion)
        for row_index in rows_to_delete:
            check_rate_limit()  # Check rate limit before each deletion
            actual_row_number = row_index + 2
            print(f"Deleting row {actual_row_number} (phone: {df.iloc[row_index][phone_column]})")
            worksheet.delete_rows(actual_row_number)
            increment_request_count()  # Track the API request
        
        print(f"Successfully removed {len(rows_to_delete)} duplicate entries.")
        
    except gspread.exceptions.WorksheetNotFound:
        print(f"Error: Worksheet '{sheet_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def remove_cross_sheet_duplicates(sheet, source_sheet_name, target_sheet_name, phone_column, testing=False):
    """
    Removes phone numbers from target_sheet that already exist in source_sheet.
    """
    try:
        source_worksheet = sheet.worksheet(source_sheet_name)
        target_worksheet = sheet.worksheet(target_sheet_name)
        
        # Get phone numbers from source sheet
        source_data = source_worksheet.get_all_records()
        source_df = pd.DataFrame(source_data)
        
        if phone_column not in source_df.columns:
            print(f"Error: Column '{phone_column}' not found in {source_sheet_name}.")
            return
        
        source_phones = set(str(phone).strip() for phone in source_df[phone_column] if str(phone).strip())
        
        # Get data from target sheet
        target_data = target_worksheet.get_all_records()
        target_df = pd.DataFrame(target_data)
        
        if phone_column not in target_df.columns:
            print(f"Error: Column '{phone_column}' not found in {target_sheet_name}.")
            return
        
        # Find rows in target that have phones matching source
        rows_to_delete = []
        for index, row in target_df.iterrows():
            target_phone = str(row[phone_column]).strip()
            if target_phone and target_phone in source_phones:
                rows_to_delete.append(index)
        
        if not rows_to_delete:
            print(f"No cross-sheet duplicates found between {source_sheet_name} and {target_sheet_name}.")
            return
        
        print(f"Found {len(rows_to_delete)} numbers in {target_sheet_name} that already exist in {source_sheet_name}.")
        
        if testing:
            print(f"\nTESTING MODE: About to delete rows from '{target_sheet_name}' that exist in '{source_sheet_name}':")
            for row_index in sorted(rows_to_delete, reverse=True):
                actual_row_number = row_index + 2
                phone_value = target_df.iloc[row_index][phone_column]
                print(f"  Row {actual_row_number}: Phone={phone_value}")
            
            confirmation = input(f"\nProceed with deleting {len(rows_to_delete)} rows from {target_sheet_name}? (Y/N): ").strip().upper()
            if confirmation != 'Y':
                print("Cross-sheet deletion cancelled.")
                return
        
        # Sort in descending order to delete from bottom up
        rows_to_delete.sort(reverse=True)
        
        # Delete the rows
        for row_index in rows_to_delete:
            check_rate_limit()  # Check rate limit before each deletion
            actual_row_number = row_index + 2
            print(f"Deleting row {actual_row_number} from {target_sheet_name} (phone: {target_df.iloc[row_index][phone_column]})")
            target_worksheet.delete_rows(actual_row_number)
            increment_request_count()  # Track the API request
        
        print(f"Successfully removed {len(rows_to_delete)} cross-sheet duplicate entries from {target_sheet_name}.")
        
    except gspread.exceptions.WorksheetNotFound as e:
        print(f"Error: Worksheet not found - {e}")
    except Exception as e:
        print(f"An error occurred in cross-sheet duplicate removal: {e}")

if __name__ == '__main__':
    testing = True  # Set to False to automatically delete without confirmation
    
    sheet = get_google_sheet()
    if sheet:
        # Step 1: Remove duplicates within IPC Outreach worksheet
        print("Step 1: Processing IPC Outreach worksheet for internal duplicates...")
        remove_duplicate_entries(sheet, 'IPC Outreach', 'Phone Number', 'Last Message DateTime', testing=testing)
        
        # Step 2: Remove duplicates within AnarockGodrejList worksheet
        print("\nStep 2: Processing AnarockGodrejList worksheet for internal duplicates...")
        remove_duplicate_entries(sheet, 'AnarockGodrejList', 'Phone Number', 'Last Message DateTime', testing=testing)
        
        # Step 3: Remove cross-sheet duplicates (remove from AnarockGodrejList if exists in IPC Outreach)
        print("\nStep 3: Removing cross-sheet duplicates (AnarockGodrejList numbers that exist in IPC Outreach)...")
        remove_cross_sheet_duplicates(sheet, 'IPC Outreach', 'AnarockGodrejList', 'Phone Number', testing=testing)
        
        print("\nAll duplicate removal operations completed!")
