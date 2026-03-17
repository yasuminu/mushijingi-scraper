import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

def scrape_magi():
    cards = []
    url = "https://magi.camp/brands/179/items"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "ja,en-US;q=0.9",
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"ステータス: {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")

        # aタグの中にカード名と価格がある
        links = soup.select("a")
        for link in links:
            try:
                text = link.get_text(separator="\n", strip=True)
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                
                # 価格を探す（¥ を含む行）
                price = None
                name = None
                for line in lines:
                    if "¥" in line:
                        price_text = line.replace("¥","").replace(",","").replace(" ","").strip()
                        if price_text.isdigit():
                            price = int(price_text)
                    elif len(line) > 5 and "蟲神器" in line or "虫神器" in line:
                        name = line

                if name and price and price > 0:
                    # レアリティ判定
                    rarity = "C"
                    if "LR" in name: rarity = "LR"
                    elif "SR" in name: rarity = "SR"
                    elif " R " in name: rarity = "R"
                    elif "UC" in name: rarity = "UC"

                    cards.append({
                        "name": name[:40].strip(),
                        "price": price,
                        "rarity": rarity,
                        "source": "magi"
                    })
                    print(f"✓ {name[:30]} → ¥{price:,}")
            except:
                continue

        time.sleep(1)
    except Exception as e:
        print(f"エラー: {e}")
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
