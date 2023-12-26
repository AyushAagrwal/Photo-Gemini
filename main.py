from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, InlineQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
import os
from PIL import Image
import google.generativeai as genai
from telegram import ChatAction

from dotenv import load_dotenv
load_dotenv()

# Configure Google API key
genai.configure(api_key=os.getenv("G_KEY"))

# Function to load OpenAI model and get responses
def get_gemini_response(image):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(image)
    return response.text

# Command handlers
def start(update, context):
    update.message.reply_text("Welcome habbibi!!...", reply_markup=get_main_keyboard())

def help_command(update, context):
    help_text = (
        "Welcome to the Image Bot!\n"
        "Send an image to get a response based on OpenAI Gemini.\n"
        "Use /help to display this message."
    )
    update.message.reply_text(help_text)

def text_message(update, context):
    update.message.reply_text("Send an image to get a response based on OpenAI Gemini.", reply_markup=get_main_keyboard())

# Image handler
def image(update, context):
    try:
        # Check if photo exists and is not empty
        # if not update.message.photo:
        #     raise ValueError("No photo found in the message.")

        photo = update.message.photo[-1].get_file()
        photo.download("img.jpg")

        # Send typing action to indicate processing
        context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

        # Get response from OpenAI Gemini
        response = get_gemini_response(Image.open("img.jpg"))

        # Send the response as a new message
        update.message.reply_text(f"The Response is:\n{response}", reply_markup=get_main_keyboard())
    except Exception as e:
        update.message.reply_text(f"Error processing image: {str(e)}", reply_markup=get_main_keyboard())

# Inline mode handler
def inline_query(update, context):
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id='1',
            title='Response based on OpenAI Gemini',
            input_message_content=InputTextMessageContent(get_gemini_response_text(query)),
        ),
    ]
    update.inline_query.answer(results)

def get_gemini_response_text(input_text):
    # Add your logic to get a response based on the input text
    return f"The Response is:\n{input_text}"

# Keyboard markup
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("/help"), KeyboardButton("Send an Image")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Error handler
def error(update, context):
    context.error(f"Update {update} caused error {context.error}")

# Telegram bot setup
updater = Updater(os.getenv("T_KEY"))
dispatcher = updater.dispatcher

# Add command handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_command))

# Add message handlers
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message))
dispatcher.add_handler(MessageHandler(Filters.photo, image))

# Add inline query handler
dispatcher.add_handler(InlineQueryHandler(inline_query))

# Add error handler
dispatcher.add_error_handler(error)

updater.start_polling()
updater.idle()
