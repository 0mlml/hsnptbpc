import requests
import json
import os
from bs4 import BeautifulSoup

def fetch_item_ids() -> list[str]:
    response = requests.get("https://api.hypixel.net/v2/skyblock/bazaar")
    response.raise_for_status()
    data = response.json()
    return list(data['products'].keys())

def fetch_npc_price_for_item(item_id: str) -> float or None:
    url = f"https://wiki.hypixel.net/Special:Search/{item_id}"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    for tr in soup.find_all("tr"):
        td = tr.find_all("td")
        if td and "NPC Sell Price" in td[0].text:
            price_text = td[1].text.strip().split(" ")[0].replace(",", "")
            try:
                print(f"{item_id}: Found price of {price_text} Coins")
                return float(price_text)
            except ValueError:
                pass
    print(f"{item_id}: No price found")
    return -1

def read_npc_prices(file_path: str) -> dict[str, float] or None:
    if not os.path.exists(file_path):
        return {}

    with open(file_path, 'r') as file:
        return json.load(file)

def update_npc_prices(file_path: str, item_ids: list[str]) -> None:
    npc_prices = read_npc_prices(file_path)

    count = 0
    for id in item_ids:
        if id not in npc_prices:
            price = fetch_npc_price_for_item(id)
            if price is not None:
                npc_prices[id] = price
        print(f"{count}/{len(item_ids)}")
        if count % 30 == 29:
            print("Saving...")
            with open(file_path, 'w') as file:
                json.dump(npc_prices, file)
        count += 1

    with open(file_path, 'w') as file:
        json.dump(npc_prices, file)
def main() -> None: 
    file_path = "./npc_prices.json"

    try:
        item_ids = fetch_item_ids()
        print(f"Found {len(item_ids)} items")
        update_npc_prices(file_path, item_ids)
        print("NPC prices updated successfully")
    except requests.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()