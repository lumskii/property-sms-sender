import json
import os
import sys
import time
import subprocess
import schedule
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
import threading

load_dotenv()

class MasterAgent:
    def __init__(self):
        self.data_file = "../shared-data/property_dealers.json"
        self.status = {
            "retrieval_agent": {"status": "idle", "last_run": None, "errors": []},
            "whatsapp_agent": {"status": "idle", "last_run": None, "errors": []},
            "sms_agent": {"status": "idle", "last_run": None, "errors": []},
            "statistics": self.get_statistics()
        }
        
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify(self.status)
        
        @self.app.route('/api/dealers')
        def get_dealers():
            dealers = self.load_dealers()
            return jsonify(dealers)
        
        @self.app.route('/api/statistics')
        def get_statistics():
            return jsonify(self.get_statistics())
        
        @self.app.route('/api/run/retrieval')
        def run_retrieval():
            threading.Thread(target=self.run_retrieval_agent).start()
            return jsonify({"message": "Retrieval agent started"})
        
        @self.app.route('/api/run/whatsapp')
        def run_whatsapp():
            threading.Thread(target=self.run_whatsapp_agent).start()
            return jsonify({"message": "WhatsApp agent started"})
        
        @self.app.route('/api/run/sms')
        def run_sms():
            threading.Thread(target=self.run_sms_agent).start()
            return jsonify({"message": "SMS agent started"})
    
    def load_dealers(self) -> List[Dict]:
        """Load dealers from the shared data file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                return data.get('dealers', [])
        return []
    
    def get_statistics(self) -> Dict:
        """Get current statistics"""
        dealers = self.load_dealers()
        
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                count_history = data.get('metadata', {}).get('count_history', [])
        else:
            count_history = []
        
        stats = {
            "total_dealers": len(dealers),
            "whatsapp_sent": sum(1 for d in dealers if d.get('whatsapp_sent', False)),
            "sms_sent": sum(1 for d in dealers if d.get('sms_sent', False)),
            "both_sent": sum(1 for d in dealers if d.get('whatsapp_sent', False) and d.get('sms_sent', False)),
            "neither_sent": sum(1 for d in dealers if not d.get('whatsapp_sent', False) and not d.get('sms_sent', False)),
            "count_history": count_history[-50:], 
            "sources": {}
        }
        
        for dealer in dealers:
            source = dealer.get('source', 'unknown')
            stats['sources'][source] = stats['sources'].get(source, 0) + 1
        
        return stats
    
    def run_retrieval_agent(self):
        """Run the retrieval agent"""
        print("Starting retrieval agent...")
        self.status["retrieval_agent"]["status"] = "running"
        
        try:
            result = subprocess.run(
                [sys.executable, "../mobile-retrieval-agent/retrieval_agent.py"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                self.status["retrieval_agent"]["status"] = "completed"
                self.status["retrieval_agent"]["last_run"] = datetime.now().isoformat()
                print("Retrieval agent completed successfully")
            else:
                self.status["retrieval_agent"]["status"] = "error"
                self.status["retrieval_agent"]["errors"].append({
                    "time": datetime.now().isoformat(),
                    "error": result.stderr
                })
                print(f"Retrieval agent error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.status["retrieval_agent"]["status"] = "timeout"
            print("Retrieval agent timeout")
        except Exception as e:
            self.status["retrieval_agent"]["status"] = "error"
            self.status["retrieval_agent"]["errors"].append({
                "time": datetime.now().isoformat(),
                "error": str(e)
            })
            print(f"Retrieval agent error: {e}")
        
        self.status["statistics"] = self.get_statistics()
    
    def run_whatsapp_agent(self):
        """Run the WhatsApp agent"""
        print("Starting WhatsApp agent...")
        self.status["whatsapp_agent"]["status"] = "running"
        
        try:
            result = subprocess.run(
                [sys.executable, "../whatsapp-agent/whatsapp_agent.py"],
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            if result.returncode == 0:
                self.status["whatsapp_agent"]["status"] = "completed"
                self.status["whatsapp_agent"]["last_run"] = datetime.now().isoformat()
                print("WhatsApp agent completed successfully")
            else:
                self.status["whatsapp_agent"]["status"] = "error"
                self.status["whatsapp_agent"]["errors"].append({
                    "time": datetime.now().isoformat(),
                    "error": result.stderr
                })
                print(f"WhatsApp agent error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.status["whatsapp_agent"]["status"] = "timeout"
            print("WhatsApp agent timeout")
        except Exception as e:
            self.status["whatsapp_agent"]["status"] = "error"
            self.status["whatsapp_agent"]["errors"].append({
                "time": datetime.now().isoformat(),
                "error": str(e)
            })
            print(f"WhatsApp agent error: {e}")
        
        self.status["statistics"] = self.get_statistics()
    
    def run_sms_agent(self):
        """Run the SMS agent"""
        print("Starting SMS agent...")
        self.status["sms_agent"]["status"] = "running"
        
        try:
            result = subprocess.run(
                [sys.executable, "../sms-agent/sms_agent.py"],
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            if result.returncode == 0:
                self.status["sms_agent"]["status"] = "completed"
                self.status["sms_agent"]["last_run"] = datetime.now().isoformat()
                print("SMS agent completed successfully")
            else:
                self.status["sms_agent"]["status"] = "error"
                self.status["sms_agent"]["errors"].append({
                    "time": datetime.now().isoformat(),
                    "error": result.stderr
                })
                print(f"SMS agent error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.status["sms_agent"]["status"] = "timeout"
            print("SMS agent timeout")
        except Exception as e:
            self.status["sms_agent"]["status"] = "error"
            self.status["sms_agent"]["errors"].append({
                "time": datetime.now().isoformat(),
                "error": str(e)
            })
            print(f"SMS agent error: {e}")
        
        self.status["statistics"] = self.get_statistics()
    
    def scheduled_run(self):
        """Run all agents in sequence"""
        print("\n=== Starting scheduled run ===")
        print(f"Time: {datetime.now()}")
        
        self.run_retrieval_agent()
        time.sleep(60)
        
        self.run_whatsapp_agent()
        time.sleep(60)
        
        self.run_sms_agent()
        
        print("=== Scheduled run completed ===\n")
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        schedule.every(6).hours.do(self.scheduled_run)
        
        schedule.every().day.at("09:00").do(self.run_retrieval_agent)
        schedule.every().day.at("10:00").do(self.run_whatsapp_agent)
        schedule.every().day.at("14:00").do(self.run_sms_agent)
        
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        scheduler_thread.start()
    
    def run(self):
        """Run the master agent"""
        print("Starting Master Agent...")
        print(f"Dashboard will be available at http://localhost:5000")
        print(f"API endpoints:")
        print(f"  - GET /api/status - Get agent status")
        print(f"  - GET /api/dealers - Get all dealers")
        print(f"  - GET /api/statistics - Get statistics")
        print(f"  - GET /api/run/retrieval - Run retrieval agent")
        print(f"  - GET /api/run/whatsapp - Run WhatsApp agent")
        print(f"  - GET /api/run/sms - Run SMS agent")
        
        self.start_scheduler()
        
        self.app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    master = MasterAgent()
    master.run()