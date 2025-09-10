import pywhatkit

def send_test_message(phone_number, message):
    """
    Sends a test WhatsApp message using pywhatkit.
    """
    try:
        pywhatkit.sendwhatmsg_instantly(
            phone_number, 
            message, 
            wait_time=20, 
            tab_close=True, 
            close_time=3
        )
        print(f"Successfully sent message to {phone_number}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    phone_number = "+14379877666"
    message = "Hello this is a test message from the WhatsApp agent."
    send_test_message(phone_number, message)
