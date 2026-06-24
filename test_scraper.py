import requests
from bs4 import BeautifulSoup

def get_6_star_operators():
    url = "https://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # We need to find the operators. They are usually in a table or a specific div class.
    # Let's just print a portion of the response or find all links with title.
    print(f"Status Code: {response.status_code}")
    print(f"Page Title: {soup.title.string}")
    
    # Find operators with rarity 5 (which means 6 star in Arknights terms, but on wiki they might use 6)
    # Often PRTS has elements like `data-rarity="5"` (0-indexed)
    operators = []
    for div in soup.find_all('div', attrs={'data-rarity': '5'}):
        name_elem = div.find('div', class_='char-name')
        if name_elem:
            operators.append(name_elem.text.strip())
            
    print(f"Found {len(operators)} 6-star operators.")
    print("Sample:", operators[:5])

if __name__ == "__main__":
    get_6_star_operators()
