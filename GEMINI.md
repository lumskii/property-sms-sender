use venv: /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/property-sms-sender/venv/bin/python3 for this project only. 

Lets look at the file for our To-dos and wrap then up one by one. Keep making the human test each task manually and getting an OK from them before you mark it [DONE] and decide to move on.

NEW TO DO:
[DONE] 0. Standalone File: Log into the google sheet (https://docs.google.com/spreadsheets/d/1LuOaHtPoJ_FOKPoVLSfLU8pkUeOHt2dOFGBvyJoxnFg/edit?gid=1637417292#gid=1637417292)
[DONE] 1. Stand alone function: Find duplicate numbers in the google sheet.
[DONE] 3. Stand Alone function: Convert numbers to whatsapp links (http://api.whatsapp.com/send/?phone=91{phone%20number)) phone numbers are in column E
4. Start Sending Messages: Look for the column, 'Send Now' and only send out those messages.
    1. Use the first name if it's available.
    2. Then take the message from 'message' column and send it.
    3. Figure out how to send the pdf if needed.
    4. Figure out how to send links in a way that unknown numbers can view them as links.
5. Save all your actions to a json file, so that it can be nicely formatted and seen on the frontend.