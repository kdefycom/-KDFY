
import logging
import aiohttp

logger = logging.getLogger(__name__)

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
