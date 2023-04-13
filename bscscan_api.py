import credentials

import requests
import json

from tqdm import tqdm


class Binance:
    
    def __init__(self):
        # Binance Exchange binance_exchange_info_url
        _binance_exchange_info_url = "https://api.binance.com/api/v3/exchangeInfo"
        _binance_exchange_info_response = requests.get(_binance_exchange_info_url)
        _binance_exchange_info_data = _binance_exchange_info_response.json()
        self._symbols = [symbol['symbol'] for symbol in _binance_exchange_info_data['symbols']]

    def coin_has_dollar_ticker(self, coin):
        return f"{coin.upper()}USDT" in self._symbols

    def coin_usd_value(self, coin):
        if not self.coin_has_dollar_ticker(coin):
          return None

        binance_coin_price_url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}USDT"
        binance_response = requests.get(binance_coin_price_url)
        binance_data = binance_response.json()

        if "price" not in binance_data:
          return None

        return float(binance_data['price'])

class BscScanWalletInfo:

    def __init__(self,wallet_address,bscscan_api_key):
        _bnb_url = f'https://api.bscscan.com/api?module=account&action=balance&address={wallet_address}&tag=latest&apikey={bscscan_api_key}'
        _bnb_response = requests.get(_bnb_url)
        self._bnb_balance = int(_bnb_response.json()['result']) / 10**18

        _url = f'https://api.bscscan.com/api?module=account&action=tokentx&startblock=0&endblock=999999999&address={wallet_address}&apikey={bscscan_api_key}'
        _response = requests.get(_url)
        self._data = _response.json()

    def get_wallet_unique_token_contracts(self):
        unique_token_contracts = []
        for item in self._data['result']:
            #print(contract['tokenDecimal'], contract['unique_contractAddress'], contract['tokenName'], contract['tokenSymbol'])
            contract = {'contractAddress': item['contractAddress'],
                        'tokenDecimal': item['tokenDecimal'],
                        'tokenName': item['tokenName'],
                        'tokenSymbol': item['tokenSymbol']}
            if contract not in unique_token_contracts:
                unique_token_contracts.append(contract)
        return unique_token_contracts

    def get_bnb_tokens(self):
        return self._bnb_balance


class BscScanTokenContractInfo:
    
    @staticmethod
    def get_number_of_tokens(token_contract_address,wallet_address,bscscan_api_key):
        # URL for retrieving token balance
        _bscscan_url = f'https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={token_contract_address}&address={wallet_address}&tag=latest&apikey={bscscan_api_key}'
        # Make bscscan API request and get response
        _bscscan_response = requests.get(_bscscan_url)
        # Parse response to get token balance
        return int(_bscscan_response.json()['result'])



def main() -> None:

    wallet_address = credentials.wallet_address
    bscscan_api_key = credentials.bscscan_api_key
    token_output = ""

    binance_exchange = Binance()
    wallet_info = BscScanWalletInfo(wallet_address,bscscan_api_key)

    unique_token_contracts = wallet_info.get_wallet_unique_token_contracts()

    # GET BNB INFO
    bnb_usd_value = wallet_info.get_bnb_tokens() * binance_exchange.coin_usd_value('BNB')
    formatted_bnb_balance = f"{wallet_info.get_bnb_tokens():.8}"
    token_output += f"\n{'COIN'[:30]:<30} {''[:20]:>20} {'TOKEN BALANCE'[:25]:<25} {'TOTAL'}\n"
    token_output += f"{'Binance Coin'[:30]:<30} {'BNB'[:20]:>20} {formatted_bnb_balance[:25]:<25} ${bnb_usd_value:.2f}\n"

    # LOOP token contracts in wallet
    for unique_contract in tqdm(unique_token_contracts):
        
        number_of_tokens = BscScanTokenContractInfo.get_number_of_tokens(unique_contract['contractAddress'],wallet_address,bscscan_api_key)
        
        if number_of_tokens != 0:
            token_balance = number_of_tokens / (10 ** int(unique_contract['tokenDecimal']))
            token_usd_value = binance_exchange.coin_usd_value(unique_contract['tokenSymbol'])

            if not token_balance.is_integer():
                formatted_token_balance = f"{token_balance:.{unique_contract['tokenDecimal']}f}"
            else:
                formatted_token_balance = f"{token_balance:.0f}"

            if token_usd_value != None:
                token_total_USD_value  = token_usd_value * token_balance
                token_output += f"{unique_contract['tokenName'][:30]:<30} {unique_contract['tokenSymbol'][:20]:>20} {formatted_token_balance[:25]:<25} ${token_total_USD_value:.2f}\n"
            else:
                token_output += f"{unique_contract['tokenName'][:30]:<30} {unique_contract['tokenSymbol'][:20]:>20} {formatted_token_balance[:25]:<25}\n"
       
    print(token_output)

if __name__ == '__main__':
    main()
