import json
import os
import time
import requests
import pyautogui
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
import sys

sys.path.append('../mobile-retrieval-agent')
from gemini_vision import GeminiVision
from opencv_vision import OpenCVVision

load_dotenv()

class SMSAgent:
    def __init__(self, use_gemini: bool = True):
        self.data_file = "../shared-data/property_dealers.json"
        self.message_template = """
        Property consultancy in Gurgaon. Premium properties, best deals, legal support. 
        Interested in collaboration? Reply YES.
        """.strip()
        
        self.textbelt_key = os.getenv('TEXTBELT_KEY', 'textbelt')
        
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
    
    def send_sms_via_textbelt(self, phone: str) -> bool:
        """Send SMS using TextBelt API (1 free SMS per day)"""
        try:
            phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            response = requests.post('https://textbelt.com/text', {
                'phone': phone_clean,
                'message': self.message_template,
                'key': self.textbelt_key,
            })
            
            result = response.json()
            
            if result.get('success'):
                print(f"✓ SMS sent successfully via TextBelt")
                return True
            else:
                print(f"✗ TextBelt error: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"✗ Error sending SMS via TextBelt: {e}")
            return False
    
    def send_sms_via_way2sms_web(self, phone: str) -> bool:
        """Send SMS using Way2SMS web interface with PyAutoGUI"""
        try:
            print("Opening Way2SMS website...")
            
            pyautogui.hotkey('cmd', 't') if os.name == 'darwin' else pyautogui.hotkey('ctrl', 't')
            time.sleep(1)
            
            pyautogui.hotkey('cmd', 'l') if os.name == 'darwin' else pyautogui.hotkey('ctrl', 'l')
            pyautogui.typewrite("https://www.way2sms.com")
            pyautogui.press('enter')
            time.sleep(5)
            
            screenshot_path = self.take_screenshot()
            
            if self.use_gemini:
                if self.vision.check_element_presence(screenshot_path, "login form or sign in button"):
                    print("Please login manually if required...")
                    time.sleep(10)
            
            if self.use_gemini:
                coords = self.vision.find_element_coordinates(screenshot_path, "send SMS button or compose message")
                if coords:
                    pyautogui.click(coords[0], coords[1])
                    time.sleep(2)
            
            screenshot_path = self.take_screenshot()
            
            if self.use_gemini:
                coords = self.vision.find_element_coordinates(screenshot_path, "mobile number input field")
                if coords:
                    pyautogui.click(coords[0], coords[1])
                    pyautogui.typewrite(phone)
                    time.sleep(1)
            
            if self.use_gemini:
                coords = self.vision.find_element_coordinates(screenshot_path, "message text area")
                if coords:
                    pyautogui.click(coords[0], coords[1])
                    pyautogui.typewrite(self.message_template)
                    time.sleep(1)
            
            if self.use_gemini:
                coords = self.vision.find_element_coordinates(screenshot_path, "send button")
                if coords:
                    pyautogui.click(coords[0], coords[1])
                    time.sleep(3)
                    return True
            
            return False
            
        except Exception as e:
            print(f"✗ Error using Way2SMS web: {e}")
            return False
    
    def take_screenshot(self, filename: str = "sms_screenshot.png") -> str:
        """Take a screenshot"""
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return filename
    
    def send_sms_via_fast2sms_web(self, phone: str) -> bool:
        """Alternative: Use Fast2SMS web interface"""
        try:
            print("Opening Fast2SMS website...")
            
            pyautogui.hotkey('cmd', 't') if os.name == 'darwin' else pyautogui.hotkey('ctrl', 't')
            time.sleep(1)
            
            pyautogui.hotkey('cmd', 'l') if os.name == 'darwin' else pyautogui.hotkey('ctrl', 'l')
            pyautogui.typewrite("https://www.fast2sms.com/dashboard/sms")
            pyautogui.press('enter')
            time.sleep(5)
            
            print("Please ensure you're logged in to Fast2SMS...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"✗ Error using Fast2SMS web: {e}")
            return False
    
    def send_to_dealer(self, dealer: Dict) -> bool:
        """Send SMS to a single dealer"""
        phone = dealer['mobile']
        
        if not phone.startswith('+'):
            if phone.startswith('91'):
                phone = '+' + phone
            else:
                phone = '+91' + phone.replace('-', '').replace(' ', '')
        
        print(f"Sending SMS to {dealer['name']} ({phone})")
        
        success = self.send_sms_via_textbelt(phone)
        
        if not success:
            print("Trying web-based SMS service...")
            success = self.send_sms_via_way2sms_web(phone)
        
        if success:
            dealer['sms_sent'] = True
            dealer['sms_sent_at'] = datetime.now().isoformat()
            print(f"✓ SMS sent to {dealer['name']}")
            return True
        else:
            print(f"✗ Failed to send SMS to {dealer['name']}")
            return False
    
    def run(self, limit: int = None):
        """Run the SMS agent"""
        print("Starting SMS messaging agent...")
        print("Move mouse to any corner to stop the script.")
        
        dealers = self.load_dealers()
        
        pending_dealers = [d for d in dealers if not d.get('sms_sent', False)]
        
        whatsapp_only = [d for d in dealers if d.get('whatsapp_sent', False) and not d.get('sms_sent', False)]
        if whatsapp_only:
            print(f"Prioritizing {len(whatsapp_only)} dealers who received WhatsApp but not SMS.")
            pending_dealers = whatsapp_only + [d for d in pending_dealers if d not in whatsapp_only]
        
        if not pending_dealers:
            print("No pending dealers to message.")
            return
        
        print(f"Found {len(pending_dealers)} dealers to send SMS.")
        
        if limit:
            pending_dealers = pending_dealers[:limit]
            print(f"Limiting to {limit} dealers.")
        
        try:
            messages_sent = 0
            
            for i, dealer in enumerate(pending_dealers):
                print(f"\nProcessing {i+1}/{len(pending_dealers)}")
                
                if self.send_to_dealer(dealer):
                    messages_sent += 1
                    
                    self.save_dealers(dealers)
                    
                    if i < len(pending_dealers) - 1:
                        wait_time = 60
                        print(f"Waiting {wait_time} seconds before next message...")
                        time.sleep(wait_time)
            
            print(f"\n✓ Completed! Sent SMS to {messages_sent} dealers.")
            
        except pyautogui.FailSafeException:
            print("\nScript stopped by user (mouse moved to corner)")
            self.save_dealers(dealers)
        except Exception as e:
            print(f"\nError occurred: {e}")
            self.save_dealers(dealers)

if __name__ == "__main__":
    agent = SMSAgent(use_gemini=True)
    agent.run(limit=3)