# Cyber Buddy - Full Stack Cybersecurity Application

A comprehensive cybersecurity platform with chatbot, URL risk checking, cybercrime reporting, and news features.

## Features

### 🤖 Bot
- Cybersecurity-focused chatbot powered by Google AI
- Cyber law and awareness information
- Scam detection and prevention guidance

### 🔍 Risk-Checker
- URL safety verification using Google Safe Browsing API
- Clear safe/risky indicators

### 📋 Report
- Cybercrime office locator by state/city
- Contact information and helpline numbers
- Official website links

### 📰 News
- Daily cybersecurity news updates
- Key highlights and summaries

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **APIs**: 
  - Google AI API for chatbot
  - Google Safe Browsing API for URL checking
  - News API for cybersecurity news

### Frontend
- **Framework**: HTML/CSS/JavaScript (Single Page Application)
- **Styling**: Custom CSS with cybersecurity theme
- **UI**: Clean interface with curved navigation buttons

## Project Structure

```
cyber-buddy/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── services/
│   │   └── data/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
└── README.md
```

## Quick Start

### Option 1: Automatic Setup (Recommended)
1. **Install Python** from [python.org](https://python.org) (Make sure to check "Add Python to PATH")
2. **Double-click `setup.bat`** - This will install dependencies and start the server
3. **Open `frontend/index.html`** in your web browser

### Option 2: Manual Setup
1. **Install Python** from [python.org](https://python.org)
2. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Start backend server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
4. **Open frontend**: Open `frontend/index.html` in your browser

### Quick Test
Run `python test_setup.py` to verify everything is working correctly.

## API Endpoints

- `POST /bot/chat` - Cybersecurity chatbot
- `POST /risk-checker/check-url` - URL safety verification
- `GET /report/offices/{location}` - Cybercrime office information
- `GET /news/cybersecurity` - Latest cybersecurity news

## Environment Variables

```
GOOGLE_AI_API_KEY=your_google_ai_key
GOOGLE_SAFE_BROWSING_API_KEY=your_safe_browsing_key
NEWS_API_KEY=your_news_api_key
```
