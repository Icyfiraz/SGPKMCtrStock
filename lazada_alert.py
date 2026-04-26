import requests
import json
import re
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PRODUCTS = [
    {
        "name": "Ascended Heroes ETB",
        "url": "https://www.lazada.sg/products/pdp-i13686883411-s124548114668.html",
        "last_stock": 0,
        "last_alert": 0
    }
]

COOLDOWN = 30

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

def send_alert(msg):
    try:
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": msg},
            timeout=5
        )
    except:
        pass

def extract_json(html):
    match = re.search(r'window\.__NEXT_DATA__\s*=\s*(\{.*?\});', html)
    if match:
        return json.loads(match.group(1))
    return None

def check_stock(product):
    try:
        r = session.get(product["url"], timeout=5)
        data = extract_json(r.text)

        if not data:
            return 0

        product_data = data["props"]["pageProps"]["initialData"]["data"]
        skus = product_data["root"]["fields"]["skuInfos"]

        total_stock = 0
        buyable = False

        for sku in skus.values():
            stock = sku.get("stock", 0)
            purchasable = sku.get("purchasable", False)

            total_stock += stock

            if stock > 0 and purchasable:
                buyable = True

        if buyable:
            return total_stock

    except Exception as e:
        print("Error:", e)

    return 0

print("🚀 Sniper monitor started...")

while True:
    for product in PRODUCTS:
        stock = check_stock(product)
        now = time.time()

        if stock > 0 and product["last_stock"] == 0:
            send_alert(f"🚨 {product['name']} JUST RESTOCKED!\n{product['url']}")
            product["last_alert"] = now
            print(f"{product['name']} RESTOCK!")

        elif stock > 0 and now - product["last_alert"] > COOLDOWN:
            send_alert(f"⚡ {product['name']} STILL AVAILABLE!\n{product['url']}")
            product["last_alert"] = now

        else:
            send_alert(f"⚡ {product['name']} STILL AVAILABLE!\n{product['url']}")
            product["last_alert"] = now
            #print(f"{product['name']} OOS")

        product["last_stock"] = stock

        time.sleep(0.8)

    time.sleep(0.5)
