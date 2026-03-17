import requests
import json
import time
from datetime import datetime

def scrape_magi():
    cards = []
    url = "https://magi.camp/api/v1/search?q=蟲神器&category=card"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        items = data.get("items", data.get("products", data.get("results", [])))
        for item in items[:30]:
            try:
                name = item.get("name") or item.get("title", "")
                price = item.get("price") or item.get("sell_price", 0)
                if name and price:
                    rarity = "SR"
                    if "LR" in name: rarity = "LR"
                    elif "SR" in name: rarity = "SR"
                    elif " R " in name or name.endswith(" R"): rarity = "R"
                    elif "UC" in name: rarity = "UC"
                    elif " C " in name or name.endswith(" C"): rarity = "C"
                    cards.append({
                        "name": name.strip(),
                        "price": int(price),
                        "rarity": rarity,
                        "source": "magi"
                    })
            except:
                continue
        time.sleep(1)
    except Exception as e:
        print(f"magiエラー: {e}")
    
    # APIが取れない場合はHTMLから取得
    if not cards:
        try:
            from bs4 import BeautifulSoup
            url2 = "https://magi.camp/brands/179/items"
            response2 = requests.get(url2, headers=headers, timeout=15)
            soup = BeautifulSoup(response2.text, "html.parser")
            items2 = soup.select(".item-box") or soup.select(".product-item") or soup.select("article")
            for item in items2[:30]:
                try:
                    name_el = item.select_one(".item-name") or item.select_one("h3") or item.select_one("p")
                    price_el = item.select_one(".price") or item.select_one("span")
                    if name_el and price_el:
                        price_text = price_el.text.replace("¥","").replace(",","").strip()
                        if price_text.isdigit():
                            name = name_el.text.strip()
                            rarity = "SR"
                            if "LR" in name: rarity = "LR"
                            elif "SR" in name: rarity = "SR"
                            cards.append({
                                "name": name,
                                "price": int(price_text),
                                "rarity": rarity,
                                "source": "magi"
                            })
                except:
                    continue
        except Exception as e:
            print(f"magi HTMLエラー: {e}")
    
    return cards

def main():
    print("蟲神器価格データ取得開始...")
    all_cards = scrape_magi()
    print(f"取得件数: {len(all_cards)}")

    card_map = {}
    for card in all_cards:
        name = card["name"]
        if name not in card_map:
            card_map[name] = {
                "name": name,
                "prices": [],
                "sources": [],
                "rarity": card.get("rarity", "C")
            }
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

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"完了！{len(result)}件保存しました。")

if __name__ == "__main__":
    main()
