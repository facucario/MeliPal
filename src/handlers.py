from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
import logging

from database import SessionLocal, Watchlist, SeenAd, BotState
from scraper import MELI_REGEX, ensure_published_today_filter, get_title_from_url, transform_listado_to_autos

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hola! Mandame un link de MercadoLibre para seguirlo. Usa /help para más comandos.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    "🤖 MercadoLibre Watcher Bot\n\n"
    "Enviá un link de búsqueda de MercadoLibre para seguirlo.\n"
    "Acepta URLs de listado.mercadolibre.com.ar y autos.mercadolibre.com.ar\n"
    "Podés enviar múltiples URLs en un solo mensaje (uno por línea).\n\n"
    "Comandos:\n"
    "/start - Bienvenida\n"
    "/help - Ayuda\n"
    "/list - Ver links seguidos\n"
    "/remove <url> - Eliminar link seguido\n"
    "/clear_seen - Borrar avisos vistos\n"
    "/stop - Pausar monitoreo\n"
    "/resume - Reanudar monitoreo"
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    chat_id = str(update.message.chat_id)
    
    # Split message by newlines to get multiple URLs
    urls = [url.strip() for url in message_text.split('\n') if url.strip()]
    
    if not urls:
        await update.message.reply_text("❌ No se encontraron URLs válidas en el mensaje.")
        return
    
    session: Session = SessionLocal()
    results = []
    
    # Check if this is the user's first URL (to set bot state to running)
    existing_urls = session.query(Watchlist).filter_by(chat_id=chat_id).count()
    is_first_url = existing_urls == 0
    
    for original_url in urls:
        if not MELI_REGEX.match(original_url):
            results.append(f"❌ {original_url} - No es un link válido de MercadoLibre")
            continue
        
        # Transform the URL for processing and storage
        transformed_url = ensure_published_today_filter(original_url)
        
        exists = session.query(Watchlist).filter_by(chat_id=chat_id, url=transformed_url).first()
        if exists:
            results.append(f"✅ {original_url} - Ya estabas siguiendo ese link")
        else:
            # Extract title for the URL
            title = get_title_from_url(transformed_url)
            
            # Add to watchlist with title
            watchlist_entry = Watchlist(chat_id=chat_id, url=transformed_url, title=title)
            session.add(watchlist_entry)
            results.append(f"🔔 {original_url} - ¡Empezaré a monitorear ese link!")
    
    # If this is the user's first URL, set bot state to running
    if is_first_url:
        bot_state = session.query(BotState).filter_by(chat_id=chat_id).first()
        if not bot_state:
            bot_state = BotState(chat_id=chat_id, is_running=True)
            session.add(bot_state)
        else:
            bot_state.is_running = True
    
    session.commit()
    session.close()
    
    # Send results as a single message
    response_text = "\n".join(results)
    await update.message.reply_text(response_text)

async def remove_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    if not context.args:
        await update.message.reply_text("❌ Usá: /remove <url>")
        return
    original_url = context.args[0].strip()
    # Transform the URL to match what's stored in the database
    transformed_url = ensure_published_today_filter(original_url)
    
    session: Session = SessionLocal()
    entry = session.query(Watchlist).filter_by(chat_id=chat_id, url=transformed_url).first()
    if entry:
        # Delete all seen ads for this user and this url
        session.query(SeenAd).filter_by(chat_id=chat_id, url=entry.url).delete()
        session.delete(entry)
        session.commit()
        await update.message.reply_text("✅ Link eliminado de tu lista.")
    else:
        await update.message.reply_text("⚠️ No estabas siguiendo ese link.")
    session.close()

async def clear_seen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    session: Session = SessionLocal()
    # Delete all seen ads for this user
    session.query(SeenAd).filter_by(chat_id=chat_id).delete()
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
    
    # Use cached titles from database
    keyboard = [[InlineKeyboardButton(u.title or u.url, callback_data=f"remove::{u.id}")] for u in urls]
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
            # Use cached titles from database
            keyboard = [[InlineKeyboardButton(u.title or u.url, callback_data=f"remove::{u.id}")] for u in urls]
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

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop the bot monitoring for this user."""
    chat_id = str(update.message.chat_id)
    session: Session = SessionLocal()
    
    try:
        # Get or create bot state for this user
        bot_state = session.query(BotState).filter_by(chat_id=chat_id).first()
        if not bot_state:
            bot_state = BotState(chat_id=chat_id, is_running=False)
            session.add(bot_state)
        else:
            bot_state.is_running = False
        
        session.commit()
        await update.message.reply_text("⏸️ Bot pausado. No recibirás más notificaciones hasta que uses /resume.")
        
    except Exception as e:
        logger.error(f"Error stopping bot for {chat_id}: {e}")
        await update.message.reply_text("❌ Error al pausar el bot.")
    finally:
        session.close()

async def resume_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resume the bot monitoring for this user."""
    chat_id = str(update.message.chat_id)
    session: Session = SessionLocal()
    
    try:
        # Get or create bot state for this user
        bot_state = session.query(BotState).filter_by(chat_id=chat_id).first()
        if not bot_state:
            bot_state = BotState(chat_id=chat_id, is_running=True)
            session.add(bot_state)
        else:
            bot_state.is_running = True
        
        session.commit()
        await update.message.reply_text("▶️ Bot reanudado. Volverás a recibir notificaciones de nuevos avisos.")
        
    except Exception as e:
        logger.error(f"Error resuming bot for {chat_id}: {e}")
        await update.message.reply_text("❌ Error al reanudar el bot.")
    finally:
        session.close()