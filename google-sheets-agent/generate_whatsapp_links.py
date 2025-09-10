import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_sheets_agent import get_google_sheet
import gspread

def create_whatsapp_links(sheet, sheet_name, source_column, dest_column):
    """
    Converts phone numbers in a source column to WhatsApp links in a destination column.
    """
    try:
        worksheet = sheet.worksheet(sheet_name)
        phone_numbers = worksheet.col_values(ord(source_column.upper()) - 64)
        
        formulas = []
        for number in phone_numbers:
            # Clean the number by removing non-digit characters
            cleaned_number = "".join(filter(str.isdigit, number))
            if cleaned_number:
                formulas.append(f'=HYPERLINK("http://api.whatsapp.com/send/?phone=91{cleaned_number}", "{cleaned_number}")')
            else:
                formulas.append("") # Keep the cell empty if it's not a valid number

        # Prepare the data for updating the sheet
        cell_list = worksheet.range(f"{dest_column}1:{dest_column}{len(formulas)}")
        for i, cell in enumerate(cell_list):
            cell.value = formulas[i]

        # Update the sheet
        worksheet.update_cells(cell_list, value_input_option='USER_ENTERED')
        print(f"Successfully created WhatsApp links in column {dest_column}.")

    except gspread.exceptions.WorksheetNotFound:
        print(f"Error: Worksheet '{sheet_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    sheet = get_google_sheet()
    if sheet:
        create_whatsapp_links(sheet, 'IPC Outreach', 'E', 'S')
