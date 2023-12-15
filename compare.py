import json
import requests

def fetch_bazaar_data() -> dict:
    endpoint = "https://api.hypixel.net/v2/skyblock/bazaar"
    response = requests.get(endpoint)
    response.raise_for_status()
    return response.json()

def get_user_coins() -> float or None:
    try:
        coins = input("Enter the amount of coins you have (press Enter to skip): ").replace(",", "")
        return float(coins) if coins.strip() else None
    except ValueError:
        return None
    
def get_upper_limit() -> int or None:
    try:
        lim = input("Enter the upper limit of items to buy (press Enter to skip): ")
        return int(lim) if lim.strip() else None
    except ValueError:
        return None

def main() -> None:
    user_coins = get_user_coins()
    upper_limit = get_upper_limit() if user_coins is not None else None

    try:
        api_data = fetch_bazaar_data()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return

    try:
        with open("./npc_prices.json", "r") as file:
            npc_prices = json.load(file)
    except IOError as e:
        print(f"Error reading NPC prices: {e}")
        return

    filtered_for_limit = 0
    undercut_items = []
    for id, product in api_data['products'].items():
        npc_price = npc_prices.get(id, -1)
        quick_buy = product['quick_status']['buyPrice']

        if quick_buy <= 0 or quick_buy >= npc_price:
            continue

        item_data = {
            'ID': id,
            'Diff': npc_price - quick_buy,
            'QuickBuy': quick_buy,
            'NPCPrice': npc_price
        }

        if user_coins is not None:
            item_data['AffordableQuantity'] = int(user_coins // quick_buy)
            item_data['PotentialProfit'] = item_data['Diff'] * item_data['AffordableQuantity']

        if upper_limit is not None and item_data['AffordableQuantity'] > upper_limit:
            filtered_for_limit += 1
            continue

        undercut_items.append(item_data)

    if user_coins is not None:
        undercut_items.sort(key=lambda item: item.get('PotentialProfit', 0), reverse=True)
    else:
        undercut_items.sort(key=lambda item: item['Diff'], reverse=True)

    print("\nPotential Undercut Items:")
    for item in undercut_items:
        print(f"ID: {item['ID']}, Quick Buy: {item['QuickBuy']:.2f}, NPC Price: {item['NPCPrice']:.2f}, Diff: {item['Diff']:.2f}", end='')
        if user_coins is not None:
            print(f", Affordable Quantity: {item['AffordableQuantity']}, Potential Profit: {item['PotentialProfit']:.2f}")
        else:
            print()
    print(f"\n{len(undercut_items)} items found")
    if filtered_for_limit > 0:
        print(f"{filtered_for_limit} items were omitted due to the upper limit")

if __name__ == "__main__":
    main()
