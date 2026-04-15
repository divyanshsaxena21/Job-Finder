from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from app.config import settings
from app.services.auth_service import AuthService
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token)
        self.app: Optional[Application] = None

    async def send_approval_request(
        self,
        chat_id: str,
        job_title: str,
        company: str,
        match_score: float,
        app_id: str
    ):
        """Send approval request to user via Telegram"""
        
        try:
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{app_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{app_id}"),
                ]
            ])
            
            message = f"""🎯 <b>Job Application Ready</b>

<b>Position:</b> {job_title}
<b>Company:</b> {company}
<b>Match Score:</b> {match_score:.0f}%

👉 <i>Review the resume and cover letter, then approve or reject.</i>"""
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            print(f"✓ Sent approval request for {job_title} to {chat_id}")
        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")

    async def send_notification(self, chat_id: str, message: str):
        """Send generic notification to user"""
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")

    async def setup_handlers(self, app: Application):
        """Setup Telegram handlers"""
        
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CallbackQueryHandler(self.approval_button_handler))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        message = f"""👋 <b>Welcome to Job Finder Bot!</b>

Your Chat ID: <code>{chat_id}</code>

📋 <b>How it works:</b>
1. Add your profile and preferences in the web app
2. We'll fetch and match job postings
3. Generated resume and cover letter will be reviewed
4. You'll get notifications here to approve submissions

📝 Use /help for more info."""
        
        await update.message.reply_text(message, parse_mode="HTML")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = """📚 <b>Commands:</b>
/start - Show welcome message
/help - Show this help message

<b>Setup:</b>
1. Go to JobFinder web app
2. Enter your chat ID in preferences: <code>{}</code>
3. Save preferences
4. You're all set!""".format(update.effective_chat.id)
        
        await update.message.reply_text(message, parse_mode="HTML")

    async def approval_button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle approve/reject buttons"""
        query = update.callback_query
        data = query.data
        
        # Parse callback data: approve_<app_id> or reject_<app_id>
        action, app_id = data.rsplit("_", 1)
        
        # Send to backend to process
        # This would be called from the API endpoint
        await query.answer()
        await query.edit_message_text(
            text=f"✓ Application {action}ed. Processing..."
        )
        
        print(f"Telegram approval: {action} for app {app_id}")

    async def start_polling(self):
        """Start polling for Telegram updates"""
        try:
            print("🤖 Starting Telegram bot polling...")
            await self.app.run_polling()
        except Exception as e:
            logger.error(f"Error in Telegram polling: {e}")


# Singleton instance
telegram_bot = TelegramBot()
