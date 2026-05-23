import logging
import json
import os
import asyncio
from telegram import (
   Update,
   InlineKeyboardButton,
   InlineKeyboardMarkup,
   WebAppInfo
)
from telegram.ext import (
   ApplicationBuilder,
   CommandHandler,
   CallbackQueryHandler,
   ContextTypes
)

# =============================================================
# CONFIGURATION
# =============================================================

TOKEN = "8744963419:AAFcngIdV_pF3pITHbAOiydfFRlO5Tl0qCc"

CHANNEL_LINK = "https://t.me/+xkLrkV6xQBQ2OTQ0"

MINI_APP_URL = "https://leroimerlin1.github.io/Dry76/"

IMAGE_WELCOME = "chat.jpg"

ADMIN_ID = 8313494819

USERS_FILE = "users.json"

INFO_TEXT = """Information de Dry.Coffee76

Pour toutes commande, une carte d'identité 🪪 est nécessaire et une photo 📸 de vous.

Contact secrétaire : @sav_Bart76

Info Livraison 🚚

Zone de livraison
76 / 27 / 14

• Sur Rouen : 70€
• Moins de 10 km de Rouen : 100€
• Supérieur à 10 km : 150€
• Supérieur à 25 km : 270€

Frais de livraison obligatoire s'il n'y a pas de tournée !

Info Meet-up 📍

Nous sommes situé sur Rouen Rive Gauche 📍

50€ de commande minimum pour venir sur place"""

BROADCAST_TEXT = """Salut 👋 l'équipe

Nouvelle mise à jour sur la mini-app, vous pouvez désormais mettre votre avis ⭐️ sur le canal en général et il y a un nouveau chat 📝 pour la communauté"""

# =============================================================
# LOGGING
# =============================================================

logging.basicConfig(
   format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
   level=logging.INFO
)

logger = logging.getLogger(__name__)

# =============================================================
# GESTION DES UTILISATEURS (stockage JSON)
# =============================================================

def load_users() -> set:
   if os.path.exists(USERS_FILE):
       try:
           with open(USERS_FILE, "r") as f:
               return set(json.load(f))
       except Exception:
           return set()
   return set()


def save_user(user_id: int):
   users = load_users()
   users.add(user_id)
   with open(USERS_FILE, "w") as f:
       json.dump(list(users), f)


# =============================================================
# FONCTIONS UTILITAIRES
# =============================================================

def get_main_menu_keyboard():
   keyboard = [
       [
           InlineKeyboardButton("📩 Contact", callback_data="contact"),
           InlineKeyboardButton("ℹ️ Informations", callback_data="info"),
       ],
       [
           InlineKeyboardButton("🛍 Ouvrir la boutique", web_app=WebAppInfo(url=MINI_APP_URL))
       ]
   ]
   return InlineKeyboardMarkup(keyboard)


async def send_welcome_menu(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
   try:
       with open(IMAGE_WELCOME, "rb") as photo_file:
           await context.bot.send_photo(
               chat_id=chat_id,
               photo=photo_file,
               caption=(
                   "Bienvenue chez Bart Coffee76 🔥\n\n"
                   "Choisis une option ci-dessous :"
               ),
               reply_markup=get_main_menu_keyboard()
           )
   except FileNotFoundError:
       logger.warning(f"Image introuvable : {IMAGE_WELCOME}")
       await context.bot.send_message(
           chat_id=chat_id,
           text=(
               "Bienvenue chez Bart Coffee76 🔥\n\n"
               f"(image '{IMAGE_WELCOME}' introuvable dans le dossier)\n\n"
               "Choisis une option :"
           ),
           reply_markup=get_main_menu_keyboard()
       )
   except Exception as e:
       logger.error(f"Erreur envoi photo : {e}")
       await context.bot.send_message(
           chat_id=chat_id,
           text="Bienvenue chez Bart Coffee76 🔥\n\nChoisis une option :",
           reply_markup=get_main_menu_keyboard()
       )


# =============================================================
# HANDLERS
# =============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
   user = update.effective_user
   if not user:
       return

   save_user(user.id)
   await send_welcome_menu(update.effective_chat.id, context)


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
   user = update.effective_user
   if not user or user.id != ADMIN_ID:
       await update.message.reply_text("❌ Tu n'as pas la permission d'utiliser cette commande.")
       return

   users = load_users()
   if not users:
       await update.message.reply_text("⚠️ Aucun utilisateur enregistré pour l'instant.")
       return

   sent = 0
   failed = 0

   await update.message.reply_text(f"📤 Envoi en cours à {len(users)} utilisateurs...")

   for chat_id in users:
       try:
           await context.bot.send_message(chat_id=chat_id, text=BROADCAST_TEXT)
           sent += 1
       except Exception as e:
           logger.warning(f"Impossible d'envoyer à {chat_id} : {e}")
           failed += 1
       await asyncio.sleep(0.05)

   await update.message.reply_text(
       f"✅ Broadcast terminé !\n\n"
       f"• Envoyés : {sent}\n"
       f"• Échecs : {failed}"
   )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
   query = update.callback_query
   await query.answer()

   data = query.data

   # ──────────────── RETOUR ────────────────
   if data == "back":
       try:
           await query.message.delete()
       except Exception:
           pass
       await send_welcome_menu(query.message.chat_id, context)
       return

   # ──────────────── Contact ────────────────
   if data == "contact":
       try:
           await query.message.delete()
       except Exception:
           pass

       keyboard = [
           [InlineKeyboardButton("💬 Contacter le support", url="https://t.me/sav_Bart76")],
           [InlineKeyboardButton("← Retour", callback_data="back")]
       ]

       await context.bot.send_message(
           chat_id=query.message.chat_id,
           text="Tu veux parler à l'équipe ?\n\nClique ci-dessous pour ouvrir le chat privé :",
           reply_markup=InlineKeyboardMarkup(keyboard)
       )
       return

   # ──────────────── Informations ────────────────
   if data == "info":
       try:
           await query.message.delete()
       except Exception:
           pass

       keyboard = [[InlineKeyboardButton("← Retour", callback_data="back")]]

       await context.bot.send_message(
           chat_id=query.message.chat_id,
           text=INFO_TEXT,
           reply_markup=InlineKeyboardMarkup(keyboard)
       )
       return


# =============================================================
# LANCEMENT
# =============================================================

def main():
   app = ApplicationBuilder() \
       .token(TOKEN) \
       .build()

   app.add_handler(CommandHandler("start", start))
   app.add_handler(CommandHandler("broadcast", broadcast))
   app.add_handler(CallbackQueryHandler(button_handler))

   print("Bot démarré → Bart Coffee76  |  Image : chat.jpg")
   app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
   main()
