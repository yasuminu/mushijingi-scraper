import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

def scrape_yuyu():
    cards = []
    url = "https://yuyu-tei.jp/sell/mushi/s/sr"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".card-product-box")
        for item in items[:30]:
            try:
                name = item.select_one(".card-name") or item.select_one("h4") or item.select_one(".name")
                price = item.select_one(".price") or item.select_one(".sell-price") or item.select_one("span.price")
                if name and price:
                    price_text = price.text.replace("円","").replace(",","").replace("￥","").strip()
                    if price_text.isdigit():
                        cards.append({
                            "name": name.text.strip(),
                            "price": int(price_text),
                            "rarity": "SR",
                            "source": "遊々亭"
                        })
            except:
                continue
        time.sleep(2)
    except Exception as e:
        print(f"遊々亭エラー: {e}")
    return cards

def scrape_cardrush():
    cards = []
    url = "https://www.cardrush.jp/product-list?game_id=57"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".product-item") or soup.select(".item") or soup.select("li.product")
        for item in items[:30]:
            try:
                name = item.select_one(".product-name") or item.select_one(".name") or item.select_one("h3")
                price = item.select_one(".price") or item.select_one(".selling-price")
                if name and price:
                    price_text = price.text.replace("円","").replace(",","").replace("￥","").strip()
                    if price_text.isdigit():
                        cards.append({
                            "name": name.text.strip(),
                            "price": int(price_text),
                            "rarity": "SR",
                            "source": "カードラッシュ"
                        })
            except:
                continue
        time.sleep(2)
    except Exception as e:
        print(f"カードラッシュエラー: {e}")
    return cards

def main():
    print("蟲神器価格データ取得開始...")
    all_cards = []
    all_cards.extend(scrape_yuyu())
    all_cards.extend(scrape_cardrush())

    print(f"取得件数: {len(all_cards)}")

    card_map = {}
    for card in all_cards:
        name = card["name"]
        if name not in card_map:
            card_map[name] = {"name": name, "prices": [], "sources": [], "rarity": card.get("rarity","C")}
        card_map[name]["prices"].append(card["price"])
        card_map[name]["sources"].append(card["source"])

    result = []
    for name, data in card_map.items():
        prices = data["prices"]
        result.append({
            "name": name,
            "rarity": data["rarity"],
            "currentPrice": int(sum(prices)/len(prices)),
            "minPrice": min(prices),
            "maxPrice": max(prices),
            "sources": list(set(data["sources"])),
            "updatedAt": datetime.now().isoformat()
        })

    output = {
        "cards": result,
        "updatedAt": datetime.now().isoformat(),
        "totalCards": len(result)
    }

    with open("prices.json","w",encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"完了！{len(result)}件保存しました。")

if __name__ == "__main__":
    main()
