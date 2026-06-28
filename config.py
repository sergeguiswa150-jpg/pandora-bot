import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError(
        "La variable d'environnement TELEGRAM_TOKEN est absente."
    )

ADMIN_ID = 6269793768

BOT_NAME = "MrTech237"

PAYMENT_METHODS = """
💳 Moyens de paiement acceptés :

• MTN Mobile Money
• Orange Money
• PayPal
• USDT
• Bitcoin
• Virement bancaire
"""
