from web3 import Web3
import requests
import json

def main() -> None:

    # Set wallet address, case-sensitive!
    wallet_address = "<<a_wallet_address>>"
    # Set the token contract address for the REEF token, case-sensitive!
    token_contract_address = "0xF21768cCBC73Ea5B6fd3C687208a7c2def2d966e" # REEF TOKEN
    
    # Set up the BSC network provider
    bsc_url = "https://bsc-dataseed.binance.org/"
    web3 = Web3(Web3.HTTPProvider(bsc_url))

    # Set up the BSCScan API endpoint to retrieve the ABI for the token contract
    url_eth = "https://api.bscscan.com/api"
    token_contract_address = web3.to_checksum_address(token_contract_address)
    API_ENDPOINT = url_eth+"?module=contract&action=getabi&address="+str(token_contract_address)

    # Make a request to the BSCScan API to retrieve the ABI
    r = requests.get(url = API_ENDPOINT)
    response = r.json()
    abi=json.loads(response["result"])

    # Set up the token contract using the ABI and the contract address
    token_contract = web3.eth.contract(address=token_contract_address, abi=abi)

    # Get the token decimals
    token_decimals = token_contract.functions.decimals().call()

    # Get the token balance for the specified wallet address
    token_balance = token_contract.functions.balanceOf(wallet_address).call()

    # Convert the token balance to the correct decimal place
    token_balance = token_balance / (10 ** token_decimals)

    # Get the token name and symbol
    token_name = token_contract.functions.name().call()
    token_symbol = token_contract.functions.symbol().call()

    # Print the token balance
    print(f"{token_name} ({token_symbol}) balance=>: {token_balance:.2f}")


if __name__ == '__main__':
    main()

    