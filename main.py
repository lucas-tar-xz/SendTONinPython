import monkeypatch_typing
import requests
from pytoniq_core.crypto.keys import mnemonic_to_private_key
from tonutils.client import ToncenterV2Client
from tonutils.wallet import WalletV5R1
import asyncio

TONCENTER_API_KEY = "" # api key from https://t.me/tonapibot

def get_toncenter_client() -> ToncenterV2Client:
    return ToncenterV2Client(
        base_url=f"https://toncenter.com",
        api_key=TONCENTER_API_KEY
    )

def get_balance(address):
    url = f"https://toncenter.com/api/v2/getAddressInformation"
    params = {"address": address}
    headers = {"X-API-Key": TONCENTER_API_KEY}

    with requests.session() as session:
        with session.get(url, params=params, headers=headers) as response:
            data = response.json()
            if data.get("ok"):
                return int(data["result"]["balance"])
            else:
                return 0


def send_transaction(wallet, destination, amount_ton):
    try:
        address = wallet.address.to_str()
        comment = "LucasBuyerBot"

        balance = get_balance(address)

        if amount_ton + 0.01 > balance / 1e9:
            print("Balance so low")
            return 0

        tx_hash = wallet.transfer(
            destination=destination,
            amount=amount_ton,
            body=comment
        )
        return tx_hash
    except:
        return 0

def create_wallets(client, private_key):
    return WalletV5R1.from_private_key(client, private_key)

def parse_words():
    with open("seeds.txt", "r") as file:
        words = file.read().splitlines()
    return [words[i:i + 24] for i in range(0, len(words), 24)]

async def main(amount, address):
    try:
        word_lists = parse_words()

        for i, words in enumerate(word_lists[:2048]):
            mnemonic = " ".join(words)

            private_key = mnemonic_to_private_key(mnemonic.split(" "))[1]

            client = get_toncenter_client()
            wallet = create_wallets(client, private_key)
            transaction = await send_transaction(wallet, address, amount)
            if transaction:
                print(transaction)
        return 1
    except:
        return 0

def send_ton(amount: int | float, address: str):
    return asyncio.run(main(amount, address))

if __name__ == "__main__":
    amnt = float(input("Count: "))
    addrs = str(input("Address to send: "))
    print(send_ton(amnt, addrs))
