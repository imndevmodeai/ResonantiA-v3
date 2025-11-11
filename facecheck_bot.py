#!/usr/bin/env python3
"""
FaceCheck Telegram Bot
Integrates with the FaceCheck Flask app to provide Telegram bot functionality
Similar to youscrape bot integration pattern
"""

import os
import logging
import threading
from typing import Dict, Any, Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import requests
import re

# Import FaceCheck API client
try:
    from app import FaceCheckAPIClient, process_and_render
except ImportError:
    # Fallback if app.py is not in same directory
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import FaceCheckAPIClient, process_and_render

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app (for web interface)
app = Flask(__name__)

# Telegram bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv('FACECHECK_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    logger.warning("FACECHECK_BOT_TOKEN not set. Bot functionality will be disabled.")

# Initialize FaceCheck API client
facecheck_client = FaceCheckAPIClient()

# Flask routes (for web interface)
@app.route('/')
def index():
    return """
    <h1>FaceCheck Service</h1>
    <p>Web interface available at /web</p>
    <p>Telegram bot is running</p>
    """

@app.route('/web')
def web_interface():
    """Redirect to Flask app if running separately"""
    return "FaceCheck Web Interface - Use Telegram bot or visit Flask app directly"

# Telegram bot handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🎭 <b>FaceCheck Bot</b>

I can help you search for faces using FaceCheck.ID!

<b>How to use:</b>
1. Send me a FaceCheck.ID URL (e.g., https://facecheck.id/#search-id)
2. Or send me a search ID directly
3. I'll process it and send you the results

<b>Commands:</b>
/start - Show this message
/help - Get help
/search &lt;search_id&gt; - Search by ID
/url &lt;facecheck_url&gt; - Search by URL

<b>Example:</b>
/url https://facecheck.id/#abc123xyz
"""
    await update.message.reply_text(welcome_message, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """
🔍 <b>FaceCheck Bot Help</b>

<b>Methods to search:</b>

1. <b>Send a FaceCheck.ID URL</b>
   Just paste a URL like:
   https://facecheck.id/#your-search-id

2. <b>Use /search command</b>
   /search your-search-id

3. <b>Use /url command</b>
   /url https://facecheck.id/#your-search-id

<b>What happens:</b>
- I'll fetch the search results from FaceCheck.ID
- Process the images and metadata
- Send you formatted results with images

<b>Note:</b> Large results may be split into multiple messages due to Telegram's limits.
"""
    await update.message.reply_text(help_message, parse_mode='HTML')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command with search ID"""
    if not context.args or len(context.args) == 0:
        await update.message.reply_text("❌ Please provide a search ID.\nUsage: /search <search_id>")
        return
    
    search_id = context.args[0]
    await process_facecheck_search(update, search_id)

async def url_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /url command with FaceCheck URL"""
    if not context.args or len(context.args) == 0:
        await update.message.reply_text("❌ Please provide a FaceCheck.ID URL.\nUsage: /url <facecheck_url>")
        return
    
    facecheck_url = ' '.join(context.args)
    await process_facecheck_url(update, facecheck_url)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    text = update.message.text or ''
    
    # Check if it's a FaceCheck.ID URL
    if 'facecheck.id' in text:
        await process_facecheck_url(update, text)
    # Check if it looks like a search ID (alphanumeric with dashes/underscores)
    elif re.match(r'^[a-zA-Z0-9_-]+$', text.strip()):
        await process_facecheck_search(update, text.strip())
    else:
        await update.message.reply_text(
            "❓ I didn't understand that. Please send:\n"
            "- A FaceCheck.ID URL (https://facecheck.id/#...)\n"
            "- A search ID\n"
            "- Or use /help for more info"
        )

async def process_facecheck_url(update: Update, facecheck_url: str):
    """Process a FaceCheck.ID URL"""
    try:
        # Extract search ID from URL
        search_id_match = re.search(r'#([a-zA-Z0-9_-]+)', facecheck_url)
        if not search_id_match:
            await update.message.reply_text("❌ Could not extract search ID from URL. Please check the format.")
            return
        
        search_id = search_id_match.group(1)
        await process_facecheck_search(update, search_id)
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        await update.message.reply_text(f"❌ Error processing URL: {str(e)}")

async def process_facecheck_search(update: Update, search_id: str):
    """Process a FaceCheck search by ID"""
    chat_id = update.message.chat_id
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text(f"🔄 Processing search ID: <code>{search_id}</code>", parse_mode='HTML')
        
        # Fetch data from FaceCheck API
        data = facecheck_client.search_by_id(search_id)
        
        # Process and render results
        html_output = process_and_render(data)
        
        # Extract information from the processed data
        items = find_items_in_data(data)
        if not items:
            await update.message.reply_text("❌ No results found for this search ID.")
            return
        
        # Send results summary
        summary = f"✅ Found {len(items)} result(s) for search ID: <code>{search_id}</code>\n\n"
        
        # Send each result (Telegram has limits, so we'll send key info)
        for idx, item in enumerate(items[:10], 1):  # Limit to 10 results
            result_text = f"<b>Result {idx}</b>\n"
            if item.get('score'):
                result_text += f"Score: {item.get('score')}\n"
            if item.get('url'):
                result_text += f"URL: {item.get('url')}\n"
            if item.get('guid'):
                result_text += f"GUID: <code>{item.get('guid')}</code>\n"
            
            # Send image if available
            if item.get('base64'):
                try:
                    # Extract base64 image data
                    base64_data = item['base64']
                    if base64_data.startswith('data:image/'):
                        # For Telegram, we'd need to decode and send as photo
                        # For now, send the URL if available
                        if item.get('url'):
                            await update.message.reply_text(result_text + f"🔗 {item.get('url')}", parse_mode='HTML')
                        else:
                            await update.message.reply_text(result_text, parse_mode='HTML')
                    else:
                        await update.message.reply_text(result_text, parse_mode='HTML')
                except Exception as e:
                    logger.error(f"Error sending image {idx}: {e}")
                    await update.message.reply_text(result_text, parse_mode='HTML')
            else:
                await update.message.reply_text(result_text, parse_mode='HTML')
        
        if len(items) > 10:
            await update.message.reply_text(f"📊 ... and {len(items) - 10} more results. Visit the web interface for full details.")
        
        # Delete processing message
        try:
            await processing_msg.delete()
        except:
            pass
            
    except ValueError as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing search: {e}", exc_info=True)
        await update.message.reply_text(f"❌ An error occurred: {str(e)}")

def find_items_in_data(data):
    """Helper function to find items in data (from app.py)"""
    if isinstance(data, dict) and 'items' in data and isinstance(data['items'], list):
        return data['items']
    if isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
        return data['results']
    if isinstance(data, dict) and 'output' in data:
        output = data['output']
        if isinstance(output, dict) and 'items' in output and isinstance(output['items'], list):
            return output['items']
        if isinstance(output, dict) and 'results' in output and isinstance(output['results'], list):
            return output['results']
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and 'base64' in data:
        return [data]
    return None

def run_bot():
    """Run the Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Cannot start bot: FACECHECK_BOT_TOKEN not set")
        return
    
    try:
        # Create application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("search", search_command))
        application.add_handler(CommandHandler("url", url_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Start the bot (use run_polling with proper thread handling)
        logger.info("Starting FaceCheck Telegram bot...")
        # Disable signal handlers for threading
        import signal
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            stop_signals=None  # Disable signal handling in thread
        )
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)

def run_flask():
    """Run the Flask web server"""
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    import sys
    
    # Determine mode: 'bot', 'web', or 'both'
    mode = os.getenv('FACECHECK_MODE', 'both')
    
    if mode == 'bot':
        run_bot()
    elif mode == 'web':
        run_flask()
    elif mode == 'both':
        # Run both in separate threads
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        
        if TELEGRAM_BOT_TOKEN:
            bot_thread.start()
            logger.info("Telegram bot thread started")
        else:
            logger.warning("Telegram bot not started (no token)")
        
        flask_thread.start()
        logger.info(f"Flask web server started on port {os.getenv('PORT', 5000)}")
        
        # Keep main thread alive
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
    else:
        logger.error(f"Unknown mode: {mode}. Use 'bot', 'web', or 'both'")

