#!/bin/bash
"""
Quick Start Script for Property SMS Sender
This script helps you get started quickly with the application
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Property SMS Sender - Quick Start${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run the setup first:${NC}"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment found${NC}"

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo -e "${BLUE}Creating .env from example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env file with your API keys:${NC}"
    echo "  - GEMINI_API_KEY: Get from https://makersuite.google.com/app/apikey"
    echo "  - WHATSAPP_PHONE_NUMBER: Your WhatsApp number"
    echo ""
    echo -e "${YELLOW}Press Enter when ready to continue...${NC}"
    read
fi

echo -e "${GREEN}✓ Configuration file found${NC}"

# Start options
echo ""
echo -e "${BLUE}Choose how to start the application:${NC}"
echo "1. Master Agent (Recommended) - Starts API server and dashboard"
echo "2. Individual WhatsApp Agent"
echo "3. Individual SMS Agent"
echo "4. Run WhatsApp Campaigns"
echo "5. Setup Verification"
echo "6. Open Dashboard Only"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo -e "${GREEN}Starting Master Agent...${NC}"
        echo -e "${YELLOW}Dashboard will be available at: http://localhost:5000${NC}"
        cd master-agent
        python master_agent.py
        ;;
    2)
        echo -e "${GREEN}Starting WhatsApp Agent...${NC}"
        echo -e "${YELLOW}Note: Requires GUI environment or virtual display${NC}"
        cd whatsapp-agent
        DISPLAY=:99 xvfb-run -a python whatsapp_agent.py
        ;;
    3)
        echo -e "${GREEN}Starting SMS Agent...${NC}"
        cd sms-agent
        python sms_agent.py
        ;;
    4)
        echo -e "${GREEN}Running WhatsApp Campaigns...${NC}"
        echo -e "${YELLOW}This will run both Digital Greens and Godrej campaigns${NC}"
        DISPLAY=:99 xvfb-run -a python run_whatsapp_campaigns.py
        ;;
    5)
        echo -e "${GREEN}Running Setup Verification...${NC}"
        DISPLAY=:99 xvfb-run -a python verify_setup.py
        ;;
    6)
        echo -e "${GREEN}Opening Dashboard...${NC}"
        echo -e "${YELLOW}Dashboard files located in: dashboard/${NC}"
        echo -e "${YELLOW}Open dashboard/index.html in your browser${NC}"
        if command -v xdg-open > /dev/null; then
            xdg-open dashboard/index.html
        elif command -v open > /dev/null; then
            open dashboard/index.html
        else
            echo "Please manually open dashboard/index.html in your browser"
        fi
        ;;
    *)
        echo -e "${RED}Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Thanks for using Property SMS Sender!${NC}"