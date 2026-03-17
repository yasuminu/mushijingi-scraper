import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

def scrape_cardrush():
    """カードラッシュから蟲神器の価格を取得"""
    cards = []
    url = "https://www.cardrush.jp/product-list?game=mushijingi"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        items = soup.select(".product-item")
        for item in items[:20]:
            try:
                name = item.select_one(".product-name")
                price = item.select_one(".price")
                if name and price:
                    price_text = price.text.replace("円","").replace(",","").strip()
                    cards.append({
                        "name": name.text.strip(),
                        "price": int(price_text),
                        "source": "カードラッシュ",
                        "url": url
                    })
            except:
                continue
        time.sleep(2)
    except Exception as e:
        print(f"カードラッシュエラー: {e}")
    
    return cards

def scrape_yuyu():
    """遊々亭から蟲神器の価格を取得"""
    cards = []
    url = "https://yuyu-tei.jp/top/mushi"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        items = soup.select(".card-list-item")
        for item in items[:20]:
            try:
                name = item.select_one(".card-name")
                price = item.select_one(".sell-price")
                if name and price:
                    price_text = price.text.replace("円","").replace(",","").strip()
                    cards.append({
                        "name": name.text.strip(),
                        "price": int(price_text),
                        "source": "遊々亭",
                        "url": url
                    })
            except:
                continue
        time.sleep(2)
    except Exception as e:
        print(f"遊々亭エラー: {e}")
    
    return cards

def main():
    print("蟲神器価格データ取得開始...")
    
    all_cards = []
    all_cards.extend(scrape_cardrush())
    all_cards.extend(scrape_yuyu())
    
    # カード名でまとめて平均価格を計算
    card_map = {}
    for card in all_cards:
        name = card["name"]
        if name not in card_map:
            card_map[name] = {
                "name": name,
                "prices": [],
                "sources": []
            }
        card_map[name]["prices"].append(card["price"])
        card_map[name]["sources"].append(card["source"])
    
    result = []
    for name, data in card_map.items():
        prices = data["prices"]
        result.append({
            "name": name,
            "currentPrice": int(sum(prices) / len(prices)),
            "minPrice": min(prices),
            "maxPrice": max(prices),
            "sources": data["sources"],
            "updatedAt": datetime.now().isoformat()
        })
    
    # JSONファイルに保存
    output = {
        "cards": result,
        "updatedAt": datetime.now().isoformat(),
        "totalCards": len(result)
    }
    
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"完了！{len(result)}件のカードデータを保存しました。")

if __name__ == "__main__":
    main()
  
