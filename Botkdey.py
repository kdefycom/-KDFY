#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
import aiofiles
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

# Configurações diretas (editáveis)
TOKEN = "8366867696:AAGjcPlIMQzigIoNBN-udIyklYr3Muob8RU"
SMS_ACTIVATE_API_KEY = "48ed2616A71bdA2cAb5d18812245c093"
ADMINS = [6939434522, 987654321]  # IDs dos admins
PHOTO_MENU_FILE = "menu.jpg"

# Obter diretório atual
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotData:
    def __init__(self):
        self.users = set()
        self.bans = set()
        self.vip = {}
        self.coins = {}
        self.recharges = []
        self.gastos = []
        self.config = {}
        self.maintenance_mode = False
        self.saldo = {}  # Saldo dos usuários
        self.load_data()
    
    def load_data(self):
        """Carrega dados dos arquivos"""
        try:
            # Users
            users_file = os.path.join(CURRENT_DIR, "users.txt")
            if os.path.exists(users_file):
                with open(users_file, "r") as f:
                    self.users = set(int(line.strip()) for line in f if line.strip())
            
            # Bans
            bans_file = os.path.join(CURRENT_DIR, "bans.txt")
            if os.path.exists(bans_file):
                with open(bans_file, "r") as f:
                    self.bans = set(int(line.strip()) for line in f if line.strip())
            
            # VIP
            vip_file = os.path.join(CURRENT_DIR, "vip.json")
            if os.path.exists(vip_file):
                with open(vip_file, "r") as f:
                    self.vip = json.load(f)
            
            # Coins
            coins_file = os.path.join(CURRENT_DIR, "coins.json")
            if os.path.exists(coins_file):
                with open(coins_file, "r") as f:
                    self.coins = json.load(f)
            
            # Saldo
            saldo_file = os.path.join(CURRENT_DIR, "saldo.json")
            if os.path.exists(saldo_file):
                with open(saldo_file, "r") as f:
                    self.saldo = json.load(f)
            
            # Config
            config_file = os.path.join(CURRENT_DIR, "config-all.json")
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    self.config = json.load(f)
            else:
                self.create_default_config()
                
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
    
    def create_default_config(self):
        """Cria configuração padrão"""
        self.config = {
            "countries": [
                {"code": "BR", "name": "Brasil", "flag": "🇧🇷", "base_price": 12.0, "foreign": False},
                {"code": "US", "name": "Estados Unidos", "flag": "🇺🇸", "base_price": 9.0, "foreign": True},
                {"code": "UK", "name": "Reino Unido", "flag": "🇬🇧", "base_price": 10.0, "foreign": True},
                {"code": "DE", "name": "Alemanha", "flag": "🇩🇪", "base_price": 8.5, "foreign": True},
                {"code": "FR", "name": "França", "flag": "🇫🇷", "base_price": 9.5, "foreign": True}
            ],
            "pricing_rules": {
                "min": 8.0,
                "max": 15.0,
                "update_interval_seconds": 600
            },
            "recharge_values": [10, 15, 20, 30, 50]
        }
        self.save_config()
    
    def save_config(self):
        """Salva configuração"""
        config_file = os.path.join(CURRENT_DIR, "config-all.json")
        with open(config_file, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def save_users(self):
        """Salva usuários"""
        users_file = os.path.join(CURRENT_DIR, "users.txt")
        with open(users_file, "w") as f:
            for user_id in self.users:
                f.write(f"{user_id}\n")
    
    def save_bans(self):
        """Salva banidos"""
        bans_file = os.path.join(CURRENT_DIR, "bans.txt")
        with open(bans_file, "w") as f:
            for user_id in self.bans:
                f.write(f"{user_id}\n")
    
    def save_vip(self):
        """Salva VIP"""
        vip_file = os.path.join(CURRENT_DIR, "vip.json")
        with open(vip_file, "w") as f:
            json.dump(self.vip, f, indent=2)
    
    def save_coins(self):
        """Salva coins"""
        coins_file = os.path.join(CURRENT_DIR, "coins.json")
        with open(coins_file, "w") as f:
            json.dump(self.coins, f, indent=2)
    
    def save_saldo(self):
        """Salva saldo"""
        saldo_file = os.path.join(CURRENT_DIR, "saldo.json")
        with open(saldo_file, "w") as f:
            json.dump(self.saldo, f, indent=2)
    
    def add_gasto(self, user_id, nome, valor, order_id, pais):
        """Adiciona gasto ao log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gasto_line = f"{timestamp},{user_id},{nome},{valor},{order_id},{pais}\n"
        gastos_file = os.path.join(CURRENT_DIR, "gastos.txt")
        with open(coins_file, "a") as f:
            f.write(gasto_line)
    
    def get_user_saldo(self, user_id):
        """Obtém saldo do usuário"""
        return self.saldo.get(str(user_id), 0.0)
    
    def add_saldo(self, user_id, valor):
        """Adiciona saldo ao usuário"""
        current = self.saldo.get(str(user_id), 0.0)
        self.saldo[str(user_id)] = current + valor
        self.save_saldo()
    
    def remove_saldo(self, user_id, valor):
        """Remove saldo do usuário"""
        current = self.saldo.get(str(user_id), 0.0)
        if current >= valor:
            self.saldo[str(user_id)] = current - valor
            self.save_saldo()
            return True
        return False

# Instância global dos dados
bot_data = BotData()

class SMSActivateService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://sms-activate.org/stubs/handler_api.php"
    
    async def get_balance(self):
        """Obtém saldo da conta SMS-ACTIVATE"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'api_key': self.api_key,
                    'action': 'getBalance'
                }
                async with session.get(self.base_url, params=params) as response:
                    result = await response.text()
                    if result.startswith('ACCESS_BALANCE'):
                        return float(result.split(':')[1])
                    return 0.0
        except Exception as e:
            logger.error(f"Erro ao obter saldo SMS-ACTIVATE: {e}")
            return 0.0
    
    async def rent_number(self, service: str, country: str):
        """Aluga um número"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'api_key': self.api_key,
                    'action': 'getNumber',
                    'service': service,
                    'country': country
                }
                async with session.get(self.base_url, params=params) as response:
                    result = await response.text()
                    if result.startswith('ACCESS_NUMBER'):
                        parts = result.split(':')
                        return {
                            'id': parts[1],
                            'number': parts[2],
                            'status': 'rented'
                        }
                    return None
        except Exception as e:
            logger.error(f"Erro ao alugar número: {e}")
            return None
    
    async def get_sms(self, activation_id: str):
        """Obtém SMS do número"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'api_key': self.api_key,
                    'action': 'getStatus',
                    'id': activation_id
                }
                async with session.get(self.base_url, params=params) as response:
                    result = await response.text()
                    if result.startswith('STATUS_OK'):
                        return result.split(':')[1]
                    return None
        except Exception as e:
            logger.error(f"Erro ao obter SMS: {e}")
            return None
    
    async def cancel_activation(self, activation_id: str):
        """Cancela ativação"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'api_key': self.api_key,
                    'action': 'setStatus',
                    'status': '8',  # Cancel
                    'id': activation_id
                }
                async with session.get(self.base_url, params=params) as response:
                    result = await response.text()
                    return result == 'ACCESS_CANCEL'
        except Exception as e:
            logger.error(f"Erro ao cancelar ativação: {e}")
            return False

# Instância do serviço SMS
sms_service = SMSActivateService(SMS_ACTIVATE_API_KEY)

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

def get_countries_keyboard():
    """Retorna teclado de países"""
    keyboard = []
    for country in bot_data.config.get("countries", []):
        price = country["base_price"]
        text = f"{country['flag']} {country['name']} - R$ {price:.2f}"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"buy:{country['code']}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_recharge_keyboard():
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    # Verificar se está banido
    if user_id in bot_data.bans:
        await update.message.reply_text("❌ Você foi banido deste bot.")
        return
    
    # Verificar modo manutenção
    if bot_data.maintenance_mode and user_id not in ADMINS:
        keyboard = [[InlineKeyboardButton("💬 Suporte", url="https://t.me/santsz_7")]]
        await update.message.reply_text(
            "🔧 Bot em manutenção. Entre em contato com o suporte.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Processar referral se existir
    if context.args and len(context.args) > 0:
        try:
            referrer_id = int(context.args[0])
            if referrer_id != user_id and referrer_id in bot_data.users:
                # Adicionar coins ao referrer
                current_coins = bot_data.coins.get(str(referrer_id), 0)
                bot_data.coins[str(referrer_id)] = current_coins + 1  # 1 centavo = 1 coin
                bot_data.save_coins()
                
                # Notificar referrer
                try:
                    await context.bot.send_message(
                        referrer_id,
                        f"🎉 Você ganhou R$ 0,01 por indicação!\nNovo usuário: {first_name}"
                    )
                except:
                    pass
        except:
            pass
    
    # Adicionar usuário se não existir
    if user_id not in bot_data.users:
        bot_data.users.add(user_id)
        bot_data.save_users()
    
    text = f"Olá, <b>{first_name}</b>! Bem-vindo(a). Use o menu abaixo para comprar números, recarregar saldo e mais."
    
    # Enviar com foto se existir
    photo_path = os.path.join(CURRENT_DIR, PHOTO_MENU_FILE)
    if os.path.exists(photo_path):
        try:
            with open(photo_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_main_keyboard()
                )
        except:
            await update.message.reply_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=get_main_keyboard()
            )
    else:
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard()
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manipula callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    # Verificar se está banido
    if user_id in bot_data.bans:
        await query.answer("❌ Você foi banido deste bot.")
        return
    
    await query.answer()
    
    if data == "countries":
        await query.edit_message_caption(
            caption="🌍 Escolha um país:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_countries_keyboard()
        )
    
    elif data == "profile":
        coins = bot_data.coins.get(str(user_id), 0)
        saldo = bot_data.get_user_saldo(user_id)
        vip_status = "Não"
        
        if str(user_id) in bot_data.vip:
            expire_date = bot_data.vip[str(user_id)]
            if expire_date == "permanent":
                vip_status = "Sim (Vitalício)"
            else:
                try:
                    expire_dt = datetime.fromisoformat(expire_date)
                    if expire_dt > datetime.now():
                        vip_status = f"Sim (expira em {expire_date})"
                except:
                    pass
        
        profile_text = f"""👤 <b>Meu Perfil</b>

<b>Nome:</b> {query.from_user.first_name}
<b>ID:</b> {user_id}
<b>Saldo:</b> R$ {saldo:.2f}
<b>Coins:</b> {coins}
<b>Números usados:</b> 0
<b>Status VIP:</b> {vip_status}"""
        
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="back_to_menu")]]
        await query.edit_message_caption(
            caption=profile_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "commands":
        commands_text = """📋 <b>Comandos Disponíveis</b>

<blockquote>
/start - Iniciar o bot
/meuperfil - Ver seu perfil
/converte &lt;valor&gt; - Converter coins em saldo
/status - Status do bot
/fotomenu - Definir foto do menu (admin)
</blockquote>"""
        
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="back_to_menu")]]
        await query.edit_message_caption(
            caption=commands_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "referral":
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start={user_id}"
        referral_text = f"""👥 <b>Sistema de Referência</b>

Seu link de referência:
<code>{referral_link}</code>

Você ganha R$ 0,01 por cada pessoa que iniciar usando esse link."""
        
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="back_to_menu")]]
        await query.edit_message_caption(
            caption=referral_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "support":
        support_text = """💬 <b>Suporte</b>

Para suporte técnico, entre em contato:
@santsz_7 

Horário de atendimento: 24h"""
        
        keyboard = [
            [InlineKeyboardButton("💬 Abrir Chat", url="https://t.me/santsz_7")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="back_to_menu")]
        ]
        await query.edit_message_caption(
            caption=support_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "terms":
        terms_text = """📄 <b>Termos de Serviço</b>

1. Este bot fornece números virtuais para verificação
2. Não garantimos recebimento de SMS
3. Reembolsos apenas em caso de falha técnica
4. Proibido uso para atividades ilegais
5. Nos reservamos o direito de banir usuários

Ao usar este bot, você concorda com os termos."""
        
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="back_to_menu")]]
        await query.edit_message_caption(
            caption=terms_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "recharge":
        recharge_text = """💰 <b>Recarga de Saldo</b>

Escolha o valor para recarregar:"""
        
        await query.edit_message_caption(
            caption=recharge_text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_recharge_keyboard()
        )
    
    elif data == "delete_menu":
        try:
            await query.delete_message()
        except:
            await query.edit_message_caption(caption="✅️ Menu deletado.")
    
    elif data == "back_to_menu":
        text = f"Olá, <b>{query.from_user.first_name}</b>! Bem-vindo(a). Use o menu abaixo para comprar números, recarregar saldo e mais."
        await query.edit_message_caption(
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard()
        )
    
    elif data.startswith("buy:"):
        country_code = data.split(":")[1]
        # Encontrar país
        country = None
        for c in bot_data.config.get("countries", []):
            if c["code"] == country_code:
                country = c
                break
        
        if not country:
            await query.edit_message_caption(caption="❌ País não encontrado.")
            return
        
        price = country["base_price"]
        user_saldo = bot_data.get_user_saldo(user_id)
        
        if user_saldo < price:
            await query.edit_message_caption(
                caption=f"❌ Saldo insuficiente!\n\nPreço: R$ {price:.2f}\nSeu saldo: R$ {user_saldo:.2f}\n\nFaça uma recarga primeiro.",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 Recarga", callback_data="recharge")]])
            )
            return
        
        # Processar compra (simulação)
        if bot_data.remove_saldo(user_id, price):
            order_id = f"ORD{user_id}{int(datetime.now().timestamp())}"
            numero_fake = f"+{country_code}11999887766"  # Número fake para demonstração
            
            # Salvar gasto
            bot_data.add_gasto(user_id, query.from_user.first_name, price, order_id, country["name"])
            
            success_text = f"""✅ <b>Pedido Concluído!</b>

📱 <b>Número:</b> <code>{numero_fake}</code>
🌍 <b>País:</b> {country['flag']} {country['name']}
💰 <b>Valor:</b> R$ {price:.2f}
📋 <b>Pedido ID:</b> {order_id}

Aguarde o SMS chegar..."""
            
            await query.edit_message_caption(
                caption=success_text,
                parse_mode=ParseMode.HTML
            )
            
            # Simular chegada de SMS após 10 segundos
            await asyncio.sleep(10)
            sms_code = "123456"  # Código fake
            await context.bot.send_message(
                user_id,
                f"📩 <b>Código recebido:</b>\n\n<code>{sms_code}</code>\n\nPedido: {order_id}",
                parse_mode=ParseMode.HTML
            )
    
    elif data.startswith("recharge:"):
        value = float(data.split(":")[1])
        
        # Simular processo de pagamento
        await query.edit_message_caption(
            caption=f"💳 <b>Processando pagamento...</b>\n\nValor: R$ {value:.2f}\n\nAguarde...",
            parse_mode=ParseMode.HTML
        )
        
        # Simular delay do pagamento
        await asyncio.sleep(3)
        
        # Adicionar saldo
        bot_data.add_saldo(user_id, value)
        bot_data.recharges.append(value)
        
        await query.edit_message_caption(
            caption=f"✅ <b>Recarga realizada!</b>\n\nValor: R$ {value:.2f}\nNovo saldo: R$ {bot_data.get_user_saldo(user_id):.2f}",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Menu Principal", callback_data="back_to_menu")]])
        )

# Comandos públicos
async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /meuperfil"""
    user_id = update.effective_user.id
    coins = bot_data.coins.get(str(user_id), 0)
    saldo = bot_data.get_user_saldo(user_id)
    
    profile_text = f"""👤 <b>Meu Perfil</b>

<b>Nome:</b> {update.effective_user.first_name}
<b>ID:</b> {user_id}
<b>Saldo:</b> R$ {saldo:.2f}
<b>Coins:</b> {coins}"""
    
    await update.message.reply_text(profile_text, parse_mode=ParseMode.HTML)

async def convert_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /converte"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("❌ Use: /converte <valor_em_coins>")
        return
    
    try:
        coins_to_convert = int(context.args[0])
        current_coins = bot_data.coins.get(str(user_id), 0)
        
        if coins_to_convert > current_coins:
            await update.message.reply_text("❌ Você não tem coins suficientes.")
            return
        
        if coins_to_convert <= 0:
            await update.message.reply_text("❌ Valor deve ser maior que zero.")
            return
        
        # 100 coins = R$ 1,00
        saldo_value = coins_to_convert / 100
        
        # Atualizar coins e saldo
        bot_data.coins[str(user_id)] = current_coins - coins_to_convert
        bot_data.save_coins()
        bot_data.add_saldo(user_id, saldo_value)
        
        await update.message.reply_text(
            f"✅ Convertido {coins_to_convert} coins para R$ {saldo_value:.2f}\n"
            f"Coins restantes: {bot_data.coins[str(user_id)]}\n"
            f"Novo saldo: R$ {bot_data.get_user_saldo(user_id):.2f}",
            parse_mode=ParseMode.HTML
        )
        
    except ValueError:
        await update.message.reply_text("❌ Valor inválido.")

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    total_users = len(bot_data.users)
    total_recharges = sum(bot_data.recharges)
    
    status_text = f"""📊 <b>Status do Bot</b>

👥 Total de usuários: {total_users}
💰 Total recargas: R$ {total_recharges:.2f}
🔧 Manutenção: {"Sim" if bot_data.maintenance_mode else "Não"}
⏱️ Latência: ~50ms"""
    
    await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)

async def photo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /fotomenu"""
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ Comando apenas para administradores.")
        return
    
    if update.message.photo:
        # Salvar foto
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        photo_path = os.path.join(CURRENT_DIR, PHOTO_MENU_FILE)
        await file.download_to_drive(photo_path)
        await update.message.reply_text("✅ Foto do menu atualizada!")
    else:
        await update.message.reply_text("📸 Envie uma foto junto com o comando /fotomenu")

# Comandos administrativos
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ban"""
    if update.effective_user.id not in ADMINS:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Use: /ban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
        bot_data.bans.add(user_id)
        bot_data.save_bans()
        
        # Notificar usuário
        try:
            await context.bot.send_message(user_id, "❌ Você foi banido deste bot.")
        except:
            pass
        
        await update.message.reply_text(f"✅ Usuário {user_id} banido.")
    except ValueError:
        await update.message.reply_text("❌ ID inválido.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /unban"""
    if update.effective_user.id not in ADMINS:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Use: /unban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
        if user_id in bot_data.bans:
            bot_data.bans.remove(user_id)
            bot_data.save_bans()
            
            # Notificar usuário
            try:
                await context.bot.send_message(user_id, "✅ Você foi desbanido. Pode usar o bot novamente.")
            except:
                pass
            
            await update.message.reply_text(f"✅ Usuário {user_id} desbanido.")
        else:
            await update.message.reply_text("❌ Usuário não está banido.")
    except ValueError:
        await update.message.reply_text("❌ ID inválido.")

async def vip_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /vip"""
    if update.effective_user.id not in ADMINS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Use: /vip <user_id> <tempo>\nTempo: minuto|hora|dia|perm")
        return
    
    try:
        user_id = int(context.args[0])
        time_type = context.args[1].lower()
        
        if time_type == "perm":
            bot_data.vip[str(user_id)] = "permanent"
            time_text = "vitalício"
        else:
            if time_type == "minuto":
                expire_time = datetime.now() + timedelta(minutes=1)
            elif time_type == "hora":
                expire_time = datetime.now() + timedelta(hours=1)
            elif time_type == "dia":
                expire_time = datetime.now() + timedelta(days=1)
            else:
                await update.message.reply_text("❌ Tempo inválido. Use: minuto|hora|dia|perm")
                return
            
            bot_data.vip[str(user_id)] = expire_time.isoformat()
            time_text = expire_time.strftime("%d/%m/%Y %H:%M")
        
        bot_data.save_vip()
        
        # Notificar usuário
        try:
            await context.bot.send_message(
                user_id,
                f"🎉 Você recebeu vip por tempo: {time_text}!"
            )
        except:
            pass
        
        await update.message.reply_text(f"✅ VIP concedido para {user_id} até {time_text}")
        
    except ValueError:
        await update.message.reply_text("❌ ID inválido.")

async def transmit_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /transmitir"""
    if update.effective_user.id not in ADMINS:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Use: /transmitir <mensagem>")
        return
    
    message_text = " ".join(context.args)
    sent_count = 0
    
    for user_id in bot_data.users:
        try:
            await context.bot.send_message(
                user_id,
                message_text,
                parse_mode=ParseMode.HTML
            )
            sent_count += 1
            await asyncio.sleep(0.1)  # Rate limit
        except:
            continue
    
    await update.message.reply_text(f"✅ Mensagem enviada para {sent_count} usuários.")

async def bot_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /botoff"""
    if update.effective_user.id not in ADMINS:
        return
    
    bot_data.maintenance_mode = True
    await update.message.reply_text("🔧 Bot em modo manutenção.")

async def bot_online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /boton"""
    if update.effective_user.id not in ADMINS:
        return
    
    bot_data.maintenance_mode = False
    await update.message.reply_text("✅ Bot reativado.")

async def get_gastos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /gastos"""
    if update.effective_user.id not in ADMINS:
        return
    
    gastos_file = os.path.join(CURRENT_DIR, "gastos.txt")
    if os.path.exists(gastos_file):
        await update.message.reply_document(document=open(gastos_file, 'rb'))
    else:
        await update.message.reply_text("📄 Nenhum gasto registrado ainda.")

def main():
    """Função principal"""
    # Criar aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Handlers públicos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("meuperfil", my_profile))
    application.add_handler(CommandHandler("converte", convert_coins))
    application.add_handler(CommandHandler("status", bot_status))
    application.add_handler(CommandHandler("fotomenu", photo_menu))
    
    # Handlers admin
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("vip", vip_user))
    application.add_handler(CommandHandler("transmitir", transmit_message))
    application.add_handler(CommandHandler("botoff", bot_maintenance))
    application.add_handler(CommandHandler("boton", bot_online))
    application.add_handler(CommandHandler("gastos", get_gastos))
    
    # Callback handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Iniciar bot
    logger.info("Bot iniciado!")
    application.run_polling()

if __name__ == "__main__":
    main()
