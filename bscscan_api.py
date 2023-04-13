import requests
import json

from tqdm import tqdm


class Binance:
    
    def __init__(self):
        # Define the URL to get information about all available symbols on Binance
        _binance_exchange_info_url = "https://api.binance.com/api/v3/exchangeInfo"
        _binance_exchange_info_response = requests.get(_binance_exchange_info_url)
        _binance_exchange_info_data = _binance_exchange_info_response.json()
        # Extract a list of symbols from the response data and store it as an attribute of the Binance object
        self._symbols = [symbol['symbol'] for symbol in _binance_exchange_info_data['symbols']]

    def coin_has_dollar_ticker(self, coin):
        # Check if a given coin has a USDT ticker
        return f"{coin.upper()}USDT" in self._symbols

    def coin_usd_value(self, coin):
        # Check if a given coin has a USDT ticker
        if not self.coin_has_dollar_ticker(coin):
          return None

        # Define the URL to get the current price of a coin in USDT
        binance_coin_price_url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}USDT"
        binance_response = requests.get(binance_coin_price_url)
        binance_data = binance_response.json()

        if "price" not in binance_data:
          return None

        return float(binance_data['price'])

class BscScanWalletInfo:

    def __init__(self,wallet_address,bscscan_api_key):
        # Define the URL to get the BNB balance of a wallet
        _bnb_url = f'https://api.bscscan.com/api?module=account&action=balance&address={wallet_address}&tag=latest&apikey={bscscan_api_key}'
        _bnb_response = requests.get(_bnb_url)
        self._bnb_balance = int(_bnb_response.json()['result']) / 10**18

        # Define the URL to get information about all transactions involving tokens for a wallet
        _url = f'https://api.bscscan.com/api?module=account&action=tokentx&startblock=0&endblock=999999999&address={wallet_address}&apikey={bscscan_api_key}'
        _response = requests.get(_url)
        self._data = _response.json()

    def get_wallet_unique_token_contracts(self):
        # Create an empty list to store information about unique token contracts
        unique_token_contracts = []
        # Iterate over each transaction involving a token
        for item in self._data['result']:
            # Extract information about the token contract and add it to the unique_token_contracts list if it's not already present
            contract = {'contractAddress': item['contractAddress'],
                        'tokenDecimal': item['tokenDecimal'],
                        'tokenName': item['tokenName'],
                        'tokenSymbol': item['tokenSymbol']}
            if contract not in unique_token_contracts:
                unique_token_contracts.append(contract)
        # Return the list of unique token contracts
        return unique_token_contracts

    def get_bnb_tokens(self):
        # Return the BNB balance of the wallet
        return self._bnb_balance


class BscScanTokenContractInfo:
    
    @staticmethod
    def get_number_of_tokens(token_contract_address,wallet_address,bscscan_api_key):
        # Define the URL for retrieving the token balance
        _bscscan_url = f'https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={token_contract_address}&address={wallet_address}&tag=latest&apikey={bscscan_api_key}'
        _bscscan_response = requests.get(_bscscan_url)
        # Parse the response data to get the token balance and return it as an integer
        return int(_bscscan_response.json()['result'])



def main() -> None:

    # Retrieve wallet address and BSCScan API key from credentials
    # wallet_address = "<<a_wallet_address>>"
    wallet_address = "0x31ec56291b6318ca3c097709caf1a05ee753603a"
    bscscan_api_key = "<<your_bscscan_api_key>>"
    token_output = ""

    # Create Binance and BSCScan wallet objects
    binance_exchange = Binance()
    wallet_info = BscScanWalletInfo(wallet_address,bscscan_api_key)

    # Get unique token contracts in wallet
    unique_token_contracts = wallet_info.get_wallet_unique_token_contracts()

    # Get BNB info and add to token output string
    bnb_usd_value = wallet_info.get_bnb_tokens() * binance_exchange.coin_usd_value('BNB')
    formatted_bnb_balance = f"{wallet_info.get_bnb_tokens():.8}"
    token_output += f"\n{'COIN'[:30]:<30} {''[:20]:>20} {'TOKEN BALANCE'[:25]:<25} {'TOTAL'}\n"
    token_output += f"{'Binance Coin'[:30]:<30} {'BNB'[:20]:>20} {formatted_bnb_balance[:25]:<25} ${bnb_usd_value:.2f}\n"

    # Loop through token contracts in wallet
    for unique_contract in tqdm(unique_token_contracts):
        
        # Get number of tokens and convert to token balance
        number_of_tokens = BscScanTokenContractInfo.get_number_of_tokens(unique_contract['contractAddress'],wallet_address,bscscan_api_key)
        
        if number_of_tokens != 0:
            token_balance = number_of_tokens / (10 ** int(unique_contract['tokenDecimal']))
            token_usd_value = binance_exchange.coin_usd_value(unique_contract['tokenSymbol'])

            # Format token balance and add to token output string
            if not token_balance.is_integer():
                formatted_token_balance = f"{token_balance:.{unique_contract['tokenDecimal']}f}"
            else:
                formatted_token_balance = f"{token_balance:.0f}"

            # Calculate token USD value and add to token output string
            if token_usd_value != None:
                token_total_USD_value  = token_usd_value * token_balance
                token_output += f"{unique_contract['tokenName'][:30]:<30} {unique_contract['tokenSymbol'][:20]:>20} {formatted_token_balance[:25]:<25} ${token_total_USD_value:.2f}\n"
            else:
                token_output += f"{unique_contract['tokenName'][:30]:<30} {unique_contract['tokenSymbol'][:20]:>20} {formatted_token_balance[:25]:<25}\n"

    # Print token output string
    print(token_output)

if __name__ == '__main__':
    main()
