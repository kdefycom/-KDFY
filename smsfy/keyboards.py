
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    """Retorna o teclado principal"""
    keyboard = [
        [
            InlineKeyboardButton("🔗 Canal", url="https://t.me/seu_canal"),
            InlineKeyboardButton("🌍 Países", callback_data="countries")
        ],
        [
            InlineKeyboardButton("👤 Meu Perfil", callback_data="profile"),
            InlineKeyboardButton("📋 Comandos", callback_data="commands")
        ],
        [
            InlineKeyboardButton("👥 Referente", callback_data="referral"),
            InlineKeyboardButton("🆘 Suporte", callback_data="support")
        ],
        [
            InlineKeyboardButton("📄 Termos", callback_data="terms"),
            InlineKeyboardButton("💰 Recarga", callback_data="recharge")
        ],
        [
            InlineKeyboardButton("🗑️ Deletar", callback_data="delete_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_countries_keyboard(bot_data):
    """Retorna teclado de países"""
    keyboard = []
    for country in bot_data.config.get("countries", []):
        price = country["base_price"]
        text = f"{country['flag']} {country['name']} - R$ {price:.2f}"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"buy:{country['code']}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_recharge_keyboard(bot_data):
    """Retorna teclado de recarga"""
    keyboard = []
    values = bot_data.config.get("recharge_values", [10, 15, 20, 30, 50])
    
    for i in range(0, len(values), 2):
        row = []
        row.append(InlineKeyboardButton(f"R$ {values[i]}", callback_data=f"recharge:{values[i]}"))
        if i + 1 < len(values):
            row.append(InlineKeyboardButton(f"R$ {values[i+1]}", callback_data=f"recharge:{values[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)
