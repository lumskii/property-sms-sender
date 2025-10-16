import os
import time
import json
import logging
import pandas as pd
import gspread
import select
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import urllib.parse
from gdrive_attachment_handler import GDriveAttachmentHandler

# Configure the logger
logging.basicConfig(level=logging.DEBUG, format='DEBUG|%(message)s|file:%(filename)s:line No.%(lineno)d')
logger = logging.getLogger(__name__)

# Suppress verbose logs from underlying libraries
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('google.auth.transport.requests').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
logging.getLogger('oauth2client.client').setLevel(logging.WARNING)

load_dotenv()

def get_user_input_with_timeout(prompt, timeout=10):
    """
    Get user input with a timeout. Returns None if timeout expires.
    """
    print(prompt, end='', flush=True)
    
    if sys.platform == 'win32':
        # Windows implementation
        import msvcrt
        start_time = time.time()
        user_input = ''
        
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getch().decode('utf-8')
                if char == '\r':  # Enter key
                    print()  # New line after input
                    return user_input.strip()
                elif char == '\b':  # Backspace
                    if user_input:
                        user_input = user_input[:-1]
                        print('\b \b', end='', flush=True)
                else:
                    user_input += char
                    print(char, end='', flush=True)
            
            if time.time() - start_time > timeout:
                print()  # New line
                return None
            
            time.sleep(0.1)
    else:
        # Unix/Linux/Mac implementation
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            user_input = sys.stdin.readline().strip()
            return user_input
        else:
            print()  # New line
            return None

def attach_files_to_whatsapp(driver, file_paths):
    """
    Attach multiple files to WhatsApp message using the attachment button
    
    Args:
        driver: Selenium WebDriver instance
        file_paths: List of local file paths to attach
    """
    try:
        logger.debug(f"  -> Attaching {len(file_paths)} file(s)...")
        
        # Click the attachment (paperclip) button
        wait = WebDriverWait(driver, 10)
        
        # Try different selectors for the attachment button
        attachment_btn_selectors = [
            '//div[@title="Attach"]',
            '//span[@data-icon="plus"]',
            '//span[@data-icon="clip"]',
        ]
        
        attachment_btn = None
        for selector in attachment_btn_selectors:
            try:
                attachment_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                break
            except:
                continue
        
        if not attachment_btn:
            logger.error("  -> Could not find attachment button")
            return False
        
        attachment_btn.click()
        time.sleep(0.5)
        
        # Click on the "Photos & Videos" option or "Document" option
        # Find the file input element (it's hidden but we can send keys to it)
        file_input_selectors = [
            '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]',
            '//input[@type="file"][@accept]',
            '//input[@type="file"]',
        ]
        
        file_input = None
        for selector in file_input_selectors:
            try:
                file_input = driver.find_element(By.XPATH, selector)
                break
            except:
                continue
        
        if not file_input:
            logger.error("  -> Could not find file input element")
            return False
        
        # Send all file paths at once (separated by newline for multiple files)
        files_string = '\n'.join([str(fp) for fp in file_paths])
        file_input.send_keys(files_string)
        
        logger.debug(f"  -> Files attached successfully, waiting for preview to load...")
        time.sleep(2)  # Wait for preview to load
        
        return True
        
    except Exception as e:
        logger.error(f"  -> Failed to attach files: {e}")
        return False


def get_google_sheet():
    # Define the scope
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # Get the path to the credentials file from the environment variable
    creds_path = os.getenv('GOOGLE_APPSPOT_API_KEY')
    creds_json = None

    # Add credentials to the account
    try:
        with open(creds_path, 'r') as f:
            creds_json = json.load(f)
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    except FileNotFoundError:
        logger.debug(f"Error: credentials.json not found at path: {creds_path}. Please check the GOOGLE_APPSPOT_API_KEY in your .env file.")
        return None
    except Exception as e:
        logger.debug(f"An error occurred: {e}")
        return None

    # Authorize the clientsheet
    client = gspread.authorize(creds)

    # Get the instance of the Spreadsheet
    try:
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1LuOaHtPoJ_FOKPoVLSfLU8pkUeOHt2dOFGBvyJoxnFg/edit?gid=1637417292#gid=1637417292')
        return sheet
    except gspread.exceptions.SpreadsheetNotFound:
        logger.debug("Error: Spreadsheet not found. Please check the URL.")
        return None
    except PermissionError:
        if creds_json:
            logger.debug(f"Permission denied. Please share the Google Sheet with the following email: {creds_json['client_email']}")
        else:
            logger.debug("Permission denied. Could not read client_email from credentials file.")
        return None
    except gspread.exceptions.APIError as e:
        logger.debug(f"An API error occurred: {e}")
        return None

def send_followup_messages(worksheet_name, send_col, phone_col, message_col, contact_person_col, last_message_col, last_message_datetime_col, send_col_val, message_send_limit, pause_between_messages=1, testing=False):
    """
    Sends follow-up messages based on the 'IPC Outreach' Google Sheet.
    Supports attachments from Google Drive links in the format:
    Message text Attachments: [url1, url2, url3]
    """
    driver = None
    attachment_handler = None
    try:
        logger.debug("Connecting to Google Sheet...")
        sheet = get_google_sheet()
        if not sheet:
            logger.debug("Could not connect to Google Sheet. Exiting.")
            return
        
        # Initialize attachment handler
        attachment_handler = GDriveAttachmentHandler(cache_dir="./gdrive_cache")
        logger.debug("Attachment handler initialized with caching enabled")

        worksheet = sheet.worksheet(worksheet_name)
        
        logger.debug(f"Reading data from '{worksheet_name}' worksheet...")
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Get the 1-based index for the 'send' column
        try:
            headers = worksheet.row_values(1)
            send_col_index = headers.index(send_col) + 1
            message_col_index = headers.index(message_col) + 1
            last_message_col_index = headers.index(last_message_col) + 1
            last_message_datetime_col_index = headers.index(last_message_datetime_col) + 1
        except ValueError as e:
            logger.debug(f"Error: Column not found in the worksheet - {e}")
            return
        except Exception as e:
            logger.debug(f"An error occurred while finding the column index: {e}")
            return

        logger.debug("Setting up Chrome driver...")
        options = Options()
        # Create a new, dedicated profile for this script
        options.add_argument("user-data-dir=./chrome_profile_for_whatsapp")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--remote-debugging-port=9222")
        
        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.debug("Checking for messages to send...")
        messages_sent_count = 0
        for index, row in df.iterrows():
            if message_send_limit != -1 and messages_sent_count >= message_send_limit:
                logger.debug(f"Message send limit of {message_send_limit} reached. Stopping.")
                break

            send_value = str(row.get(send_col, '')).strip()
            # Check if the value in the 'send' column matches the trigger value
            if send_value.upper() == send_col_val.upper():
                phone_number = str(row.get(phone_col, '')).strip()
                message = str(row.get(message_col, '')).strip()
                contact_person = str(row.get(contact_person_col, '')).strip()

                first_name = ''
                if contact_person and contact_person.lower() != 'unknown':
                    first_name = contact_person.split()[0].capitalize()
                
                if first_name:
                    message = message.replace('{first_name}', first_name)
                else:
                    message = message.replace(' {first_name}', '')

                cleaned_number = "".join(filter(str.isdigit, phone_number))
                if not cleaned_number:
                    logger.debug(f"Skipping row {index + 2}: Invalid phone number '{phone_number}'")
                    continue
                
                full_phone_number = f"91{cleaned_number}"

                logger.debug(f"Found message for {full_phone_number} in row {index + 2}. Sending...")
                
                try:
                    # Parse message for attachments
                    clean_message, attachment_urls = attachment_handler.parse_attachments_from_message(message)
                    
                    if attachment_urls:
                        logger.debug(f"  -> Found {len(attachment_urls)} attachment(s) in message")
                    
                    # Open chat without pre-filled message
                    url = f"https://web.whatsapp.com/send?phone={full_phone_number}"
                    logger.debug(f"  -> Opening URL to chat: {url}")
                    driver.get(url)
                    
                    wait = WebDriverWait(driver, 60)
                    
                    logger.debug("  -> Waiting for the text input field to be ready...")
                    text_input_selector = '/html/body/div[1]/div/div[1]/div[3]/div/div[4]/div/footer/div[1]/div/span/div/div[2]/div/div[3]/div/p'
                    text_input = wait.until(EC.element_to_be_clickable((By.XPATH, text_input_selector)))
                    logger.debug("  -> Text input field is ready.")
                    
                    # Handle attachments if present
                    if attachment_urls:
                        logger.debug("  -> Downloading attachments from Google Drive...")
                        downloaded_files = attachment_handler.download_multiple(attachment_urls)
                        
                        if downloaded_files:
                            logger.debug(f"  -> Successfully downloaded {len(downloaded_files)} file(s)")
                            
                            # Attach files to WhatsApp
                            if not attach_files_to_whatsapp(driver, downloaded_files):
                                logger.error("  -> Failed to attach files, proceeding with text only")
                            else:
                                # Wait for attachment preview to load
                                time.sleep(2)
                                
                                # After attaching files, the text input field might change to a caption field
                                # Try to find the caption input field
                                try:
                                    caption_selector = '//div[@contenteditable="true"][@data-tab="10"]'
                                    text_input = wait.until(EC.element_to_be_clickable((By.XPATH, caption_selector)))
                                    logger.debug("  -> Caption field found after attaching files")
                                except:
                                    logger.debug("  -> Using original text input field")
                        else:
                            logger.warning("  -> No files downloaded, sending text only")

                    logger.debug("  -> Typing the message line by line...")
                    lines = clean_message.split('\n')
                    for i, line in enumerate(lines):
                        text_input.send_keys(line)
                        if i < len(lines) - 1: # If it's not the last line
                            ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
                    logger.debug("  -> Message typed.")
                    
                    time.sleep(5) # Brief pause after typing

                    send_message = True
                    if testing:
                        decision = input("Send this message? (Y/N): ").strip().upper()
                        if decision != 'Y':
                            send_message = False
                            logger.debug("  -> User chose not to send. Clearing message...")
                            text_input.clear()
                            worksheet.update_cell(index + 2, send_col_index, 'Skipped')
                            logger.debug(f"  -> Marked row {index + 2} as 'Skipped'")
                    else:
                        # Non-testing mode: 10-second timeout to press 'N' to skip
                        logger.debug("  -> You have 10 seconds to press 'N' and Enter to skip this message...")
                        decision = get_user_input_with_timeout("Press 'N' and Enter to skip (auto-send in 10s): ", 10)
                        if decision and decision.upper() == 'N':
                            send_message = False
                            logger.debug("  -> User chose not to send. Clearing message...")
                            text_input.clear()
                            worksheet.update_cell(index + 2, send_col_index, 'Skipped')
                            logger.debug(f"  -> Marked row {index + 2} as 'Skipped'")
                        else:
                            if decision is None:
                                logger.debug("  -> No input received within 10 seconds. Proceeding to send...")
                            else:
                                logger.debug("  -> Input received but not 'N'. Proceeding to send...")

                    if send_message:
                        logger.debug("  -> Sending 'Enter' key to send the message...")
                        text_input.send_keys(Keys.RETURN)
                        logger.debug("  -> 'Enter' key sent.")
                        
                        logger.debug(f"  -> Message sent to +{full_phone_number}")
                        time.sleep(5)

                        messages_sent_count += 1
                        logger.debug(f"  -> Updating Google Sheet for row {index + 2}...")
                        worksheet.update_cell(index + 2, send_col_index, 'Sent')
                        worksheet.update_cell(index + 2, message_col_index, '')
                        # Save the clean message without attachment URLs
                        worksheet.update_cell(index + 2, last_message_col_index, clean_message)
                        worksheet.update_cell(index + 2, last_message_datetime_col_index, time.strftime('%Y-%m-%d %H:%M:%S'))
                        logger.debug(f"  -> Marked row {index + 2} as 'Sent'")

                        logger.debug(f"  -> Pausing for {pause_between_messages} second(s)...")
                        time.sleep(pause_between_messages)

                except TimeoutException:
                    logger.debug(f"  -> Failed to find message box for +{full_phone_number}. Likely not a valid WhatsApp number.")
                    worksheet.update_cell(index + 2, send_col_index, 'Not a valid WhatsApp number')
                    logger.debug(f"  -> Marked row {index + 2} as 'Not a valid WhatsApp number'")
                except Exception as e:
                    logger.debug(f"  -> An unexpected error occurred for +{full_phone_number}: {e}")
                    worksheet.update_cell(index + 2, send_col_index, 'Failed')
                    logger.debug(f"  -> Marked row {index + 2} as 'Failed'")

        logger.debug("\nProcess complete. All pending messages have been handled.")

    except gspread.exceptions.WorksheetNotFound:
        logger.debug(f"Error: Worksheet '{worksheet_name}' not found.")
    except KeyboardInterrupt:
        logger.debug("Process interrupted by user. Closing Chrome driver...")
    except Exception as e:
        logger.debug(f"An unexpected error occurred: {e}")
    finally:
        if driver:
            driver.quit()
            logger.debug("Chrome driver closed.")