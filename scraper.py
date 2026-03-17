import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import re

def scrape_magi():
    cards = []
    url = "https://magi.camp/brands/179/items"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"ステータスコード: {response.status_code}")
        print(f"HTML長さ: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 全テキストからデータを探す
        # 価格パターン: ¥ + 数字
        price_pattern = re.compile(r'¥\s*([\d,]+)')
        
        # いろんなセレクターを試す
        selectors = [
            "li a", ".item", ".product", "article",
            "[class*='item']", "[class*='product']", "[class*='card']"
        ]
        
        items = []
        for selector in selectors:
            found = soup.select(selector)
            if found:
                print(f"セレクター '{selector}' で {len(found)} 件見つかりました")
                items = found
                break
        
        print(f"合計アイテム数: {len(items)}")
        
        for item in items[:50]:
            try:
                text = item.get_text(separator=" ", strip=True)
                price_match = price_pattern.search(text)
                
                if price_match:
                    price_text = price_match.group(1).replace(",", "")
                    price = int(price_text)
                    
                    # カード名を抽出（「蟲神器」を含む行）
                    lines = [l.strip() for l in text.split() if l.strip()]
                    name = " ".join(lines[:5]) if lines else text[:50]
                    
                    # レアリティ判定
                    rarity = "C"
                    if "LR" in text: rarity = "LR"
                    elif "SR" in text: rarity = "SR"
                    elif " R " in text: rarity = "R"
                    elif "UC" in text: rarity = "UC"
                    
                    if price > 0 and len(name) > 3:
                        cards.append({
                            "name": name[:40],
                            "price": price,
                            "rarity": rarity,
                            "source": "magi"
                        })
                        print(f"取得: {name[:30]} → ¥{price}")
            except Exception as e:
                continue
        
        time.sleep(1)
    except Exception as e:
        print(f"magiエラー: {e}")
    
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
