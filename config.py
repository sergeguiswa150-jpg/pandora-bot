import os

# Ton Token sera récupéré depuis les variables d'environnement sur Render
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Ton ID numérique (récupéré via @userinfobot)
ADMIN_ID = 6269793768

BOT_NAME = "MrTech237"

# Moyens de paiement affichés après le choix du pack
PAYMENT_DETAILS = """
💳 *Moyens de paiement acceptés :*

• *MTN Mobile Money* : +237XXXXXXXXX
• *Orange Money* : +237XXXXXXXXX
• *Crypto (USDT TRC20)* : `TON_ADRESSE_ICI`
• *PayPal* : ton@email.com

_Veuillez envoyer une capture d'écran du paiement une fois terminé._
"""