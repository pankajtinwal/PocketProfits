import os
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import re
from telegram.ext import ContextTypes
from bot_personality import get_personality

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash')

# Store active chat sessions with their configurations
active_chats = {}

def get_back_button():
    """Create a back button for the chat interface."""
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]]
    return InlineKeyboardMarkup(keyboard)

async def start_chat_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new chat session with Gemini, handling both command and button triggers."""
    user_id = update.effective_user.id
    
    # Get personality configuration
    personality = get_personality()
    
    # Initialize a new chat session with personality
    # Ensure any previous chat for this user is cleared to start fresh
    if user_id in active_chats:
        del active_chats[user_id]
        
    chat = model.start_chat(history=[])
    
    # Send the system prompt to set the AI's personality
    # This initial message to Gemini doesn't need to be shown to the user
    try:
        await chat.send_message_async(personality['system_prompt'])
    except Exception as e:
        # Log the error, and decide if we need to inform the user or can proceed
        print(f"Error sending system prompt to Gemini: {e}") # Replace with proper logging
        # Depending on severity, you might want to return or inform the user

    # Store chat session and personality
    active_chats[user_id] = {
        'chat': chat,
        'personality': personality
    }
    
    # Send welcome message from personality configuration
    welcome_text = personality['welcome_message']
    reply_markup = get_back_button()

    if update.callback_query:
        # Called from a button press
        await update.callback_query.message.reply_text(
            text=welcome_text,
            reply_markup=reply_markup
        )
        await update.callback_query.answer() # Acknowledge the button press
    elif update.message:
        # Called from /chat command
        await update.message.reply_text(
            text=welcome_text,
            reply_markup=reply_markup
        )
    else:
        # Fallback or error logging if neither context is available
        print(f"start_chat_session called without a valid update context for user {user_id}") # Replace with proper logging

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming chat messages and generate responses using Gemini."""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Check if user has an active chat session
    if user_id not in active_chats:
        await update.message.reply_text(
            "Please start a chat session first using /chat command."
        )
        return
    
    try:
        # Send typing action to indicate the bot is processing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

        # Get the user's chat session and personality
        chat_session = active_chats[user_id]
        chat = chat_session['chat']
        
        # Generate response
        response = await chat.send_message_async(message_text)
        
        plain_text = response.text.strip()
        # Remove characters that Telegram might interpret as Markdown
        plain_text = plain_text.replace('*', '')
        plain_text = plain_text.replace('_', '')
        plain_text = plain_text.replace('`', '')
        plain_text = plain_text.replace('[', '') # Remove potential start of a link
        plain_text = plain_text.replace(']', '') # Remove potential end of a link

        await update.message.reply_text(
            plain_text,
            # No parse_mode, so Telegram treats it as plain text
            reply_markup=get_back_button()
        )
        
    except Exception as e:
        await update.message.reply_text(
            "Sorry, I encountered an error. Please try again or start a new chat session.",
            reply_markup=get_back_button()
        )

async def end_chat_session(user_id: int) -> None:
    """End a user's chat session."""
    if user_id in active_chats:
        del active_chats[user_id]

def set_personality(personality_type: str):
    """Change the personality of the chatbot."""
    return get_personality(personality_type)