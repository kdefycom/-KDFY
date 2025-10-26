
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class BotData:
    def __init__(self, config):
        self.users = set()
        self.bans = set()
        self.vip = {}
        self.coins = {}
        self.recharges = []
        self.gastos = []
        self.config = config
        self.maintenance_mode = False
        self.saldo = {}  # Saldo dos usuários
        self.load_data()

    def load_data(self):
        """Carrega dados dos arquivos"""
        try:
            # Users
            users_file = os.path.join(self.config['data_dir'], "users.txt")
            if os.path.exists(users_file):
                with open(users_file, "r") as f:
                    self.users = set(int(line.strip()) for line in f if line.strip())
            
            # Bans
            bans_file = os.path.join(self.config['data_dir'], "bans.txt")
            if os.path.exists(bans_file):
                with open(bans_file, "r") as f:
                    self.bans = set(int(line.strip()) for line in f if line.strip())
            
            # VIP
            vip_file = os.path.join(self.config['data_dir'], "vip.json")
            if os.path.exists(vip_file):
                with open(vip_file, "r") as f:
                    self.vip = json.load(f)
            
            # Coins
            coins_file = os.path.join(self.config['data_dir'], "coins.json")
            if os.path.exists(coins_file):
                with open(coins_file, "r") as f:
                    self.coins = json.load(f)
            
            # Saldo
            saldo_file = os.path.join(self.config['data_dir'], "saldo.json")
            if os.path.exists(saldo_file):
                with open(saldo_file, "r") as f:
                    self.saldo = json.load(f)
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")

    def save_users(self):
        """Salva usuários"""
        users_file = os.path.join(self.config['data_dir'], "users.txt")
        with open(users_file, "w") as f:
            for user_id in self.users:
                f.write(f"{user_id}\n")
    
    def save_bans(self):
        """Salva banidos"""
        bans_file = os.path.join(self.config['data_dir'], "bans.txt")
        with open(bans_file, "w") as f:
            for user_id in self.bans:
                f.write(f"{user_id}\n")
    
    def save_vip(self):
        """Salva VIP"""
        vip_file = os.path.join(self.config['data_dir'], "vip.json")
        with open(vip_file, "w") as f:
            json.dump(self.vip, f, indent=2)
    
    def save_coins(self):
        """Salva coins"""
        coins_file = os.path.join(self.config['data_dir'], "coins.json")
        with open(coins_file, "w") as f:
            json.dump(self.coins, f, indent=2)
    
    def save_saldo(self):
        """Salva saldo"""
        saldo_file = os.path.join(self.config['data_dir'], "saldo.json")
        with open(saldo_file, "w") as f:
            json.dump(self.saldo, f, indent=2)
    
    def add_gasto(self, user_id, nome, valor, order_id, pais):
        """Adiciona gasto ao log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gasto_line = f"{timestamp},{user_id},{nome},{valor},{order_id},{pais}\n"
        gastos_file = os.path.join(self.config['data_dir'], "gastos.txt")
        with open(gastos_file, "a") as f:
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
