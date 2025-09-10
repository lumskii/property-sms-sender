# Property SMS Sender

A multi-agent system that retrieves property dealer information and sends automated WhatsApp and SMS messages using vision-based automation.

## Architecture

The system consists of 5 main components:

1. **Mobile Retrieval Agent** - Uses Gemini Vision API or OpenCV to navigate websites and extract property dealer information
2. **WhatsApp Agent** - Sends WhatsApp messages via WhatsApp Web using visual automation
3. **SMS Agent** - Sends SMS messages using free APIs or web interfaces
4. **Master Agent** - Orchestrates all agents and provides API endpoints
5. **Dashboard** - Web interface to monitor and control the system

## Setup

### 1. Install Dependencies

First, create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies for each agent:

```bash
cd mobile-retrieval-agent
pip install -r requirements.txt

cd ../whatsapp-agent
pip install -r requirements.txt

cd ../sms-agent
pip install -r requirements.txt

cd ../master-agent
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
- `GEMINI_API_KEY` - Get from https://makersuite.google.com/app/apikey
- `WHATSAPP_PHONE_NUMBER` - Your WhatsApp number
- `SMS_API_KEY` - For SMS services (optional)

### 3. Run the System

#### Option A: Run Master Agent (Recommended)

```bash
cd master-agent
python master_agent.py
```

This will:
- Start the Flask API server on http://localhost:5000
- Schedule automatic runs of all agents
- Provide API endpoints to trigger agents manually

Open the dashboard by navigating to `dashboard/index.html` in your browser.

#### Option B: Run Agents Individually

```bash
# Run retrieval agent
cd mobile-retrieval-agent
python retrieval_agent.py

# Run WhatsApp agent
cd whatsapp-agent
python whatsapp_agent.py

# Run SMS agent
cd sms-agent
python sms_agent.py
```

## Usage

### Safety Features

- **PyAutoGUI Fail-Safe**: Move mouse to any corner to stop the script
- **Rate Limiting**: Built-in delays between messages
- **Manual Override**: Dashboard allows manual control

### Vision Modes

The system supports two vision modes:

1. **Gemini Vision** (Recommended)
   - Uses natural language to find elements
   - More flexible and accurate
   - Requires API key

2. **OpenCV Fallback**
   - Works offline
   - Uses template matching and OCR
   - Less flexible but more stable

### Dashboard Features

- Real-time statistics
- Agent status monitoring
- Dealer count history chart
- Recent dealers table
- Manual agent triggers

## Important Notes

1. **Screen Resolution**: The system works best at 1920x1080 or higher
2. **Browser**: Chrome is recommended for web automation
3. **WhatsApp Web**: Must be logged in before running WhatsApp agent
4. **Rate Limits**: Respect rate limits to avoid being blocked
5. **Privacy**: Handle phone numbers responsibly

## Troubleshooting

### Gemini Vision Not Working
- Check API key is valid
- Ensure you have API quota remaining
- Try OpenCV fallback mode

### Elements Not Found
- Ensure websites are fully loaded
- Check internet connection
- Adjust wait times in code

### WhatsApp Messages Not Sending
- Ensure WhatsApp Web is logged in
- Check phone has internet connection
- Verify contact numbers are correct

## Data Storage

All data is stored in `shared-data/property_dealers.json` with the following structure:

```json
{
  "dealers": [
    {
      "name": "Dealer Name",
      "mobile": "+919876543210",
      "source": "justdial",
      "added_on": "2024-01-01T10:00:00",
      "whatsapp_sent": false,
      "sms_sent": false
    }
  ],
  "metadata": {
    "last_updated": "2024-01-01T10:00:00",
    "total_count": 10,
    "count_history": []
  }
}
```