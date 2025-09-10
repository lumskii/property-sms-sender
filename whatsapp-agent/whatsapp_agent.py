import json
import os
import time
import pyautogui
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
import sys

sys.path.append('../mobile-retrieval-agent')
from gemini_vision import GeminiVision
from opencv_vision import OpenCVVision

load_dotenv()

class WhatsAppAgent:
    def __init__(self, use_gemini: bool = True):
        self.data_file = "../shared-data/property_dealers.json"
        self.message_template = """
Hello! 👋

We are a leading property consultancy firm in Gurgaon. We help clients find their dream properties and also assist property owners in finding the right buyers/tenants.

✅ Premium Properties
✅ Best Deals
✅ Legal Documentation Support
✅ Site Visits Arranged

Would you be interested in collaborating with us?

Reply YES to know more.
        """.strip()
        
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0
        
        self.use_gemini = use_gemini and os.getenv('GEMINI_API_KEY')
        
        if self.use_gemini:
            self.vision = GeminiVision(os.getenv('GEMINI_API_KEY'))
            print("Using Gemini Vision API")
        else:
            self.vision = OpenCVVision()
            print("Using OpenCV Vision")
    
    def load_dealers(self) -> List[Dict]:
        """Load dealers from the shared data file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                return data.get('dealers', [])
        return []
    
    def save_dealers(self, dealers: List[Dict]):
        """Save updated dealer information"""
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        data['dealers'] = dealers
        data['metadata']['last_updated'] = datetime.now().isoformat()
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def take_screenshot(self, filename: str = "whatsapp_screenshot.png") -> str:
        """Take a screenshot"""
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return filename
    
    def open_whatsapp_web(self):
        """Open WhatsApp Web in browser"""
        print("Opening WhatsApp Web...")
        
        pyautogui.hotkey('cmd', 'space') if os.name == 'darwin' else pyautogui.hotkey('win')
        time.sleep(1)
        pyautogui.typewrite("chrome")
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(3)
        
        pyautogui.hotkey('cmd', 'l') if os.name == 'darwin' else pyautogui.hotkey('ctrl', 'l')
        pyautogui.typewrite("https://web.whatsapp.com")
        pyautogui.press('enter')
        time.sleep(5)
        
        print("Please scan the QR code if not already logged in...")
        print("Waiting for WhatsApp to load...")
        time.sleep(10)
    
    def search_contact(self, phone_number: str) -> bool:
        """Search for a contact by phone number"""
        screenshot_path = self.take_screenshot()
        
        if self.use_gemini:
            if not self.vision.find_element_coordinates(screenshot_path, "search box or search icon"):
                print("Could not find search box")
                return False
            
            coords = self.vision.find_element_coordinates(screenshot_path, "search box or search icon")
            if coords:
                pyautogui.click(coords[0], coords[1])
        else:
            pyautogui.click(200, 200)
        
        time.sleep(1)
        
        pyautogui.hotkey('ctrl', 'a') if os.name != 'darwin' else pyautogui.hotkey('cmd', 'a')
        pyautogui.press('delete')
        
        pyautogui.typewrite(phone_number, interval=0.1)
        time.sleep(2)
        
        screenshot_path = self.take_screenshot()
        if self.use_gemini:
            return self.vision.check_element_presence(screenshot_path, f"contact with number {phone_number}")
        else:
            return True
    
    def send_message(self, message: str) -> bool:
        """Send a message to the current chat"""
        screenshot_path = self.take_screenshot()
        
        if self.use_gemini:
            coords = self.vision.find_element_coordinates(screenshot_path, "message input box or type a message field")
            if coords:
                pyautogui.click(coords[0], coords[1])
            else:
                print("Could not find message input box")
                return False
        else:
            screen_width, screen_height = pyautogui.size()
            pyautogui.click(screen_width // 2, screen_height - 100)
        
        time.sleep(0.5)
        
        lines = message.split('\n')
        for i, line in enumerate(lines):
            pyautogui.typewrite(line, interval=0.01)
            if i < len(lines) - 1:
                pyautogui.hotkey('shift', 'enter')
        
        time.sleep(0.5)
        
        pyautogui.press('enter')
        time.sleep(2)
        
        return True
    
    def send_to_dealer(self, dealer: Dict) -> bool:
        """Send WhatsApp message to a single dealer"""
        phone = dealer['mobile']
        
        if not phone.startswith('+'):
            if phone.startswith('91'):
                phone = '+' + phone
            else:
                phone = '+91' + phone.replace('-', '').replace(' ', '')
        
        print(f"Sending message to {dealer['name']} ({phone})")
        
        if self.search_contact(phone):
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            
            if self.send_message(self.message_template):
                dealer['whatsapp_sent'] = True
                dealer['whatsapp_sent_at'] = datetime.now().isoformat()
                print(f"✓ Message sent to {dealer['name']}")
                return True
            else:
                print(f"✗ Failed to send message to {dealer['name']}")
        else:
            print(f"✗ Contact not found: {dealer['name']} ({phone})")
        
        return False
    
    def run(self, limit: int = None):
        """Run the WhatsApp agent"""
        print("Starting WhatsApp messaging agent...")
        print("Move mouse to any corner to stop the script.")
        
        dealers = self.load_dealers()
        
        pending_dealers = [d for d in dealers if not d.get('whatsapp_sent', False)]
        
        if not pending_dealers:
            print("No pending dealers to message.")
            return
        
        print(f"Found {len(pending_dealers)} dealers to message.")
        
        if limit:
            pending_dealers = pending_dealers[:limit]
            print(f"Limiting to {limit} dealers.")
        
        try:
            self.open_whatsapp_web()
            
            messages_sent = 0
            
            for i, dealer in enumerate(pending_dealers):
                print(f"\nProcessing {i+1}/{len(pending_dealers)}")
                
                if self.send_to_dealer(dealer):
                    messages_sent += 1
                    
                    self.save_dealers(dealers)
                    
                    if i < len(pending_dealers) - 1:
                        wait_time = 30
                        print(f"Waiting {wait_time} seconds before next message...")
                        time.sleep(wait_time)
                
                if messages_sent >= 10:
                    print("\nReached 10 messages. Taking a longer break...")
                    time.sleep(300)
                    messages_sent = 0
            
            print(f"\n✓ Completed! Sent messages to {messages_sent} dealers.")
            
        except pyautogui.FailSafeException:
            print("\nScript stopped by user (mouse moved to corner)")
            self.save_dealers(dealers)
        except Exception as e:
            print(f"\nError occurred: {e}")
            self.save_dealers(dealers)

if __name__ == "__main__":
    agent = WhatsAppAgent(use_gemini=True)
    agent.run(limit=5)