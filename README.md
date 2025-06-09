# PocketProfits (Finance Bot AI)

PocketProfits is a Telegram bot designed to provide stock analysis and financial insights. It leverages the Google Gemini API for AI-driven analysis and yfinance for fetching stock data. For broader market overview data, it's configured to use the "Yahoo Finance by API DOJO" via RapidAPI.

## Features

*   **Multi-Step Stock Analysis**: Performs a detailed, multi-step fundamental analysis of stocks, covering:
    *   Step 1: Stock Overview
    *   Step 2: Detailed Financial Statements & Ratios (Income Statement focused)
    *   Step 3: Balance Sheet & Cash Flow Analysis
    *   Final Step: Comprehensive AI Summary with strengths, weaknesses, and ratings.
*   **AI-Powered Insights**: Uses Gemini to interpret financial data and provide qualitative analysis.
*   **Interactive Chat**: Engage in a conversational chat about finance topics with FinBuddy, your AI finance assistant.
*   **User-Friendly Interface**: Easy navigation through Telegram inline keyboard buttons.
*   **Customizable Bot Personality**: AI responses are guided by a defined personality for consistency.
*   **Large Number Formatting**: Financial figures like market cap are formatted into Crores/Lakhs for INR stocks for better readability.

## Prerequisites

*   Python 3.8 or higher
*   Pip (Python package installer)

## Setup Instructions

**1. Clone the Repository**
   Clone the PocketProfits repository from GitHub:
   ```bash
   git clone https://github.com/pankajtinwal/PocketProfits.git
   cd PocketProfits
   ```

**2. Install Dependencies**
   Install the required Python packages using the `requirements.txt` file. Navigate to the project directory (`PocketProfits`) if you haven't already, then run:
   ```bash
   pip install -r requirements.txt
   ```

**3. Obtain API Keys and Token**

   You will need the following API keys and tokens:

   *   **Telegram Bot Token**:
      1.  Open Telegram and search for "BotFather".
      2.  Start a chat with BotFather and send the `/newbot` command.
      3.  Follow the instructions to choose a name and username for your bot.
      4.  BotFather will provide you with an HTTP API token. Keep this token secure.

   *   **Google Gemini API Key**:
      1.  Go to the [Google AI Studio](https://aistudio.google.com/app/apikey) (formerly MakerSuite).
      2.  Sign in with your Google account.
      3.  Click on "Get API key" or "Create API key in new project".
      4.  Follow the instructions to generate your API key. Copy it and keep it secure.

   *   **RapidAPI Key (for Yahoo Finance by API DOJO)**:
      This key is used for fetching market overview data, as per the project's setup.
      1.  Go to [RapidAPI](https://rapidapi.com/).
      2.  Sign up for a free account or log in if you already have one.
      3.  Search for "Yahoo Finance by API DOJO".
      4.  Subscribe to the API (it usually has a free basic plan that should be sufficient for moderate use).
      5.  Once subscribed, navigate to the API's dashboard or endpoints tab. You will find your `X-RapidAPI-Key` there. Copy this key.

**4. Configure Environment Variables**

   Create a file named `.env` in the root directory of your project (`PocketProfits`). Add your API keys and token to this file as follows:

   ```env
   TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
   RAPIDAPI_KEY=YOUR_RAPIDAPI_KEY_HERE
   ```

   Replace the placeholder values with your actual token and keys.

## Running the Bot

   Once you have completed the setup and configuration, you can run the bot by executing the main Python file (usually `main.py`):

   ```bash
   python main.py
   ```

   Your Telegram bot should now be online and responsive.

## Usage

   Interact with your bot on Telegram:
   *   Use the `/start` command to see the main menu.
   *   Navigate through the inline buttons to analyze stocks or chat with the AI.

---
