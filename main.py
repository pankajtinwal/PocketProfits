import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from data_handler import format_market_message
from chat_handler import start_chat_session, handle_chat_message, end_chat_session
from stock_analyzer import (
    analyze_stock, format_stock_analysis, 
    get_detailed_financials, format_detailed_financials,
    get_step3_financial_statements, format_step3_financial_statements
)
from ai_analyst import get_step1_overview_analysis, format_ai_analysis, get_step2_financial_analysis, get_step3_financial_analysis, get_final_summary_analysis

# User state management
user_states = {}

# Store stock data for AI analysis
user_stock_data = {}

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when the command /start is issued or when returning to menu."""
    user = update.effective_user
    welcome_message_text = f"""👋 *Welcome to FinanceBot, {user.first_name}!* 👋

🔍 *About FinanceBot*
I'm your personal finance assistant, designed to provide you with real-time market updates, financial insights, and analysis.

💼 *Available Commands*:
• /markets - Get current Indian stock market overview
• /chat - Chat with Finance Buddy
• /analyze - Analyze a stock with AI
• More features coming soon!

👨‍💻 *Creator*: Pankaj

How can I assist you with your financial needs today?"""
    
    main_menu_keyboard = [
        [InlineKeyboardButton("Market Overview 📊", callback_data="markets")],
        [InlineKeyboardButton("Chat with Finance Buddy 💬", callback_data="chat")],
        [InlineKeyboardButton("Analyze Stock With AI 📈", callback_data="analyze")]
    ]
    reply_markup = InlineKeyboardMarkup(main_menu_keyboard)
    
    if update.callback_query:
        # Called from a button press (e.g., "Back to Menu")
        # Send a new message, similar to how /start behaves
        await update.callback_query.message.reply_text(
            text=welcome_message_text, 
            parse_mode='Markdown', 
            reply_markup=reply_markup
        )
        # It's good practice to answer the callback query, even if just to remove the 'loading' state on the button
        await update.callback_query.answer()
    elif update.message:
        # Called from /start command
        await update.message.reply_text(
            text=welcome_message_text, 
            parse_mode='Markdown', 
            reply_markup=reply_markup
        )
    else:
        logger.error("Start function called without a valid update context (message or callback_query).")

async def markets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send Indian market overview when the command /markets is issued."""
    await update.message.reply_text("Fetching latest market data... Please wait.")
    
    # Get formatted market message
    market_message = format_market_message()
    
    await update.message.reply_text(market_message, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if query.data == "markets":
        await query.message.reply_text("Fetching latest market data... Please wait.")
        market_message = format_market_message()
        await query.message.reply_text(market_message, parse_mode='Markdown')
    elif query.data == "chat":
        await start_chat_session(update, context)
    elif query.data == "analyze":
        await analyze_stock_prompt(update, context)
    elif query.data == "ai_analysis_step2":
        # Process step 2 of AI analysis
        await process_ai_analysis_step2(update, context)
    elif query.data == "ai_analysis_step3":
        # Process step 3 of AI analysis (Balance Sheet & Cash Flow AI Analysis)
        await process_ai_analysis_step3(update, context)
    elif query.data == "final_analysis_step":
        # Placeholder for final summary analysis step
        await process_final_analysis_step(update, context)
    elif query.data == "back_to_menu":
        # Clear user state and data
        if user_id in user_states:
            del user_states[user_id]
        if user_id in user_stock_data:
            del user_stock_data[user_id]
        
        # End chat session if exists
        await end_chat_session(user_id)
        await start(update, context)

def main() -> None:
    """Start the bot."""
    # Check if token is available
    if not TELEGRAM_BOT_TOKEN:
        logger.error("No Telegram bot token provided. Please set TELEGRAM_BOT_TOKEN in .env file.")
        return
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("markets", markets_command))
    application.add_handler(CommandHandler("chat", start_chat_session))
    application.add_handler(CommandHandler("analyze", analyze_stock_prompt))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add message handler for different modes
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_user_message
    ))

    # Start the Bot
    application.run_polling()
    logger.info("Bot started!")

async def analyze_stock_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt user to enter a stock ticker for analysis."""
    message = "📈 *Stock Analysis with AI*\n\nPlease enter the ticker symbol of the stock you want to analyze.\n\nExample: RELIANCE, TCS etc"
    
    # Create back button
    keyboard = [[InlineKeyboardButton("Back to Menu ⏮️", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Set user state to analyze mode
    user_id = update.effective_user.id
    user_states[user_id] = "analyze_mode"
    
    # Handle both direct command and callback
    if update.callback_query:
        await update.callback_query.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages based on their current state."""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Check user state and route accordingly
    if user_id in user_states and user_states[user_id] == "analyze_mode":
        await handle_stock_analysis(update, context, message_text)
    else:
        # Default to chat handler
        await handle_chat_message(update, context)

async def handle_stock_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, ticker: str) -> None:
    """Process stock ticker and provide analysis."""
    user_id = update.effective_user.id
    
    # Send typing action
    await update.message.reply_text("Analyzing stock data... Please wait.")
    
    # Get stock analysis
    ticker = ticker.strip().upper()  # Normalize ticker symbol
    if not ticker.endswith(".NS") and not ticker.endswith(".BO") and not "." in ticker:
        # Add .NS suffix for NSE stocks if not provided
        ticker = f"{ticker}.NS"
    
    # Get raw stock data
    analysis_result = analyze_stock(ticker)
    
    if 'error' in analysis_result:
        # Handle error
        await update.message.reply_text(
            f"❌ *Error*: {analysis_result['error']}",
            parse_mode='Markdown'
        )
        return
    
    # Store stock data for further analysis
    user_stock_data[user_id] = analysis_result
    
    # Send data directly to Gemini
    await update.message.reply_text("Generating AI analysis... Please wait.")
    
    # Get AI analysis
    ai_result = await get_step1_overview_analysis(analysis_result)
    formatted_ai_analysis = format_ai_analysis(ai_result)
    
    # Create buttons for next step
    keyboard = [
        [InlineKeyboardButton("Move to Step 2 ⏩", callback_data="ai_analysis_step2")],
        [InlineKeyboardButton("Back to Menu ⏮️", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the AI analysis
    await update.message.reply_text(
        formatted_ai_analysis,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def process_ai_analysis_step2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process second step of AI analysis: Fetch and display detailed financials."""
    user_id = update.effective_user.id
    query = update.callback_query
    
    # Check if we have stock data and the ticker
    if user_id not in user_stock_data or 'data' not in user_stock_data[user_id] or 'ticker' not in user_stock_data[user_id]['data']:
        await query.message.reply_text(
            "⚠️ Could not retrieve stock information for detailed analysis. Please try analyzing the stock again.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Analyze Stock 📈", callback_data="analyze")]])
        )
        return
    
    ticker = user_stock_data[user_id]['data']['ticker']
    stock_name = user_stock_data[user_id]['data'].get('name', ticker)

    await query.message.reply_text(f"Fetching detailed financials for {stock_name} ({ticker})... Please wait. ⏳")
    
    # Get detailed financial data
    financial_data_result = get_detailed_financials(ticker)
    
    if not financial_data_result.get('success'):
        error_message = financial_data_result.get('error', 'Could not fetch detailed financials.')
        await query.message.reply_text(
            f"❌ *Error fetching financials for {stock_name}*:\n{error_message}",
            parse_mode='Markdown'
        )
        return

    # Format the detailed financials
    formatted_financials = format_detailed_financials(financial_data_result)
    
    # Create final buttons
    keyboard = [
        [InlineKeyboardButton("Analyze Another Stock 📈", callback_data="analyze")],
        [InlineKeyboardButton("Back to Menu ⏮️", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the formatted financials to Gemini for Step 2 analysis
    await query.message.reply_text(f"🤖 Analyzing detailed financials for {stock_name} with AI... Please wait. This may take a moment.")
    
    step2_ai_result = await get_step2_financial_analysis(formatted_financials, stock_name, ticker)
    formatted_step2_ai_analysis = format_ai_analysis(step2_ai_result) # Reusing the existing formatter

    # Create new buttons for Step 3
    keyboard_step3 = [
        [InlineKeyboardButton("Move To Step Three ⏩", callback_data="ai_analysis_step3")],
        [InlineKeyboardButton("Back to Menu ⏮️", callback_data="back_to_menu")]
    ]
    reply_markup_step3 = InlineKeyboardMarkup(keyboard_step3)

    # Send the Step 2 AI analysis
    # Split message if too long
    if len(formatted_step2_ai_analysis) > 4096:
        for i in range(0, len(formatted_step2_ai_analysis), 4096):
            chunk = formatted_step2_ai_analysis[i:i+4096]
            if i + 4096 >= len(formatted_step2_ai_analysis):
                await query.message.reply_text(chunk, parse_mode='Markdown', reply_markup=reply_markup_step3)
            else:
                await query.message.reply_text(chunk, parse_mode='Markdown')
    else:
        await query.message.reply_text(
            formatted_step2_ai_analysis,
            parse_mode='Markdown',
            reply_markup=reply_markup_step3
        )
    
    # Clear user state for analyze_mode if it was set, but keep user_stock_data
    # (user_stock_data might be needed for step 3)
    if user_id in user_states and user_states[user_id] == "analyze_mode":
        del user_states[user_id]

async def process_ai_analysis_step3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process Step 3: Fetch Balance Sheet & Cash Flow, send to AI, and display AI analysis."""
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()

    if user_id not in user_stock_data or 'data' not in user_stock_data[user_id] or 'ticker' not in user_stock_data[user_id]['data']:
        await query.message.reply_text(
            "⚠️ Could not retrieve stock information for Step 3 analysis. Please try analyzing the stock again.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📈 Analyze Stock", callback_data="analyze")]])
        )
        return
    
    ticker = user_stock_data[user_id]['data']['ticker']
    stock_name = user_stock_data[user_id]['data'].get('name', ticker)

    await query.message.reply_text(f"Fetching Balance Sheet & Cash Flow for {stock_name} ({ticker}) for AI analysis... Please wait. ⏳")

    step3_data_result = get_step3_financial_statements(ticker)

    if not step3_data_result.get('success'):
        error_message = step3_data_result.get('error', 'Could not fetch Step 3 financial statements.')
        await query.message.reply_text(
            f"❌ *Error fetching Step 3 financials for {stock_name}*:\n{error_message}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back to Menu ⏮️", callback_data="back_to_menu")]])
        )
        return

    # This is the formatted string of Balance Sheet and Cash Flow data
    formatted_step3_raw_data_string = format_step3_financial_statements(step3_data_result)

    await query.message.reply_text(f"Sending Balance Sheet & Cash Flow data of {stock_name} to AI for analysis... Please wait. 🧠")

    # Send the formatted string to Gemini for Step 3 analysis
    step3_ai_analysis_result = await get_step3_financial_analysis(
        formatted_step3_raw_data_string, 
        step3_data_result.get('stock_name', ticker),
        ticker
    )

    formatted_step3_ai_analysis = format_ai_analysis(step3_ai_analysis_result)

    # New buttons for after Step 3 AI analysis
    step3_ai_keyboard = [
        [InlineKeyboardButton("Get Final Analysis 💡", callback_data="final_analysis_step")],
        [InlineKeyboardButton("Analyze Another Stock 📈", callback_data="analyze")],
        [InlineKeyboardButton("Back to Menu ⏮️", callback_data="back_to_menu")]
    ]
    step3_ai_reply_markup = InlineKeyboardMarkup(step3_ai_keyboard)

    # Send the AI's analysis of Step 3 data
    # Split message if too long
    if len(formatted_step3_ai_analysis) > 4096:
        for i in range(0, len(formatted_step3_ai_analysis), 4096):
            chunk = formatted_step3_ai_analysis[i:i+4096]
            if i + 4096 >= len(formatted_step3_ai_analysis):
                await query.message.reply_text(chunk, parse_mode='Markdown', reply_markup=step3_ai_reply_markup)
            else:
                await query.message.reply_text(chunk, parse_mode='Markdown')
    else:
        await query.message.reply_text(
            formatted_step3_ai_analysis,
            parse_mode='Markdown',
            reply_markup=step3_ai_reply_markup
        )
    
    # Note: user_stock_data is NOT cleared here yet, as it might be needed for a final summary.

async def process_final_analysis_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the final comprehensive AI summary step."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if user_id not in user_stock_data or 'data' not in user_stock_data[user_id]:
        await query.message.reply_text(
            "⚠️ Sorry, I don't have the previous analysis data for this stock. Please start a new analysis.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Analyze Another Stock 📈", callback_data="analyze")],
                [InlineKeyboardButton("Back to Menu ⏮️", callback_data="back_to_menu")]
            ])
        )
        return

    ticker = user_stock_data[user_id]['data']['ticker']
    stock_name = user_stock_data[user_id]['data'].get('name', ticker)

    await query.message.reply_text(f"🤖 Generating final AI summary for {stock_name} ({ticker})... Please wait. This might take a moment. ⏳")

    final_ai_result = await get_final_summary_analysis(stock_name, ticker)
    formatted_final_summary = format_ai_analysis(final_ai_result) # Reusing the existing formatter

    final_keyboard = [
        [InlineKeyboardButton("Thanks 👍", callback_data="back_to_menu")]
    ]
    final_reply_markup = InlineKeyboardMarkup(final_keyboard)

    # Send the final AI summary
    # Split message if too long
    if len(formatted_final_summary) > 4096:
        for i in range(0, len(formatted_final_summary), 4096):
            chunk = formatted_final_summary[i:i+4096]
            if i + 4096 >= len(formatted_final_summary):
                await query.message.reply_text(chunk, parse_mode='Markdown', reply_markup=final_reply_markup)
            else:
                await query.message.reply_text(chunk, parse_mode='Markdown')
    else:
        await query.message.reply_text(
            formatted_final_summary,
            parse_mode='Markdown',
            reply_markup=final_reply_markup
        )
    
    # Clear user_stock_data after completing the final analysis for this stock
    if user_id in user_stock_data:
        del user_stock_data[user_id]

if __name__ == '__main__':
    main()
