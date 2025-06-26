from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
import logging

from database import SessionLocal, Watchlist, SeenAd
from scraper import MELI_REGEX, ensure_published_today_filter, get_title_from_url

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hola! Mandame un link de MercadoLibre para seguirlo. Usa /help para más comandos.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    "🤖 MercadoLibre Watcher Bot\n\n"
    "Enviá un link de búsqueda de MercadoLibre para seguirlo.\n\n"
    "Comandos:\n"
    "/start - Bienvenida\n"
    "/help - Ayuda\n"
    "/list - Ver links seguidos\n"
    "/remove <url> - Eliminar link seguido\n"
    "/clear_seen - Borrar avisos vistos"
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ensure_published_today_filter(update.message.text.strip())
    chat_id = str(update.message.chat_id)
    if not MELI_REGEX.match(text):
        await update.message.reply_text("❌ Ese no parece un link válido de MercadoLibre.")
        return
    session: Session = SessionLocal()
    exists = session.query(Watchlist).filter_by(chat_id=chat_id, url=text).first()
    if exists:
        await update.message.reply_text("✅ Ya estabas siguiendo ese link.")
    else:
        session.add(Watchlist(chat_id=chat_id, url=text))
        session.commit()
        await update.message.reply_text("🔔 ¡Empezaré a monitorear ese link!")
    session.close()

async def remove_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    if not context.args:
        await update.message.reply_text("❌ Usá: /remove <url>")
        return
    url = context.args[0].strip()
    session: Session = SessionLocal()
    entry = session.query(Watchlist).filter_by(chat_id=chat_id, url=url).first()
    if entry:
        session.query(SeenAd).filter_by(url=entry.url).delete()
        session.delete(entry)
        session.commit()
        await update.message.reply_text("✅ Link eliminado de tu lista.")
    else:
        await update.message.reply_text("⚠️ No estabas siguiendo ese link.")
    session.close()

async def clear_seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    session: Session = SessionLocal()
    watchlist = session.query(Watchlist).filter_by(chat_id=chat_id).all()
    for entry in watchlist:
        session.query(SeenAd).filter_by(url=entry.url).delete()
    session.commit()
    session.close()
    await update.message.reply_text("🧹 Se borraron todos los avisos vistos.")

async def list_urls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    session: Session = SessionLocal()
    urls = session.query(Watchlist).filter_by(chat_id=chat_id).all()
    session.close()
    if not urls:
        await update.message.reply_text("📭 No estás siguiendo ningún link.")
        return
    keyboard = [[InlineKeyboardButton(get_title_from_url(u.url), callback_data=f"remove::{u.id}")] for u in urls]
    await update.message.reply_text(
        "📋 Tus links actuales (toca uno para eliminar):",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("remove::"):
        id = int(query.data.split("::")[1])
        session: Session = SessionLocal()
        entry = session.query(Watchlist).filter_by(id=id).first()
        chat_id = str(query.message.chat_id)
        if entry:
            session.delete(entry)
            session.commit()
        urls = session.query(Watchlist).filter_by(chat_id=chat_id).all()
        session.close()
        if urls:
            keyboard = [[InlineKeyboardButton(u.url, callback_data=f"remove::{u.id}")] for u in urls]
            await query.edit_message_text(
                text="📋 Tus links actuales (toca uno para eliminar):",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await query.edit_message_text("📭 No estás siguiendo ningún link.")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Comando no reconocido. Usá /help para ver los disponibles.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("[ERROR] Unhandled exception:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ Ocurrió un error inesperado. Intentá nuevamente.")