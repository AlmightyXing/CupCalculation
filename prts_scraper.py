import requests
from bs4 import BeautifulSoup
import json
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_operator_list():
    """
    Since PRTS wiki API (cargoquery) currently throws MWException,
    we fetch the list of operators from ArknightsGameData (which is the source PRTS uses).
    """
    url = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/excel/character_table.json"
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        
        operators = []
        for char_id, char_info in data.items():
            # 筛选 6星干员 (TIER_6) 且是正规干员 (itemDesc 不为空，排除 token 等)
            if char_info.get('rarity') == 'TIER_6' and char_info.get('itemDesc') and not char_info.get('isNotObtainable'):
                # 排除一些特殊占位符比如阿米娅等如果有问题，但这里主要是 6 星
                operators.append(char_info['name'])
                
        return operators
    except Exception as e:
        print(f"Error fetching from ArknightsGameData: {e}")
        # fallback to a predefined list for testing if API fails
        return ["玛恩纳", "史尔特尔", "纯烬艾雅法拉", "银灰", "能天使", "伊芙利特"]

def fetch_operator_html(name):
    url = f"https://prts.wiki/w/{name}"
    response = requests.get(url, headers=HEADERS)
    response.encoding = 'utf-8'
    return response.text

def parse_operator_data(html, name):
    """
    Extracts skill descriptions, talents, and stats.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Extract Stats (Base stats at E2 Max)
    # PRTS wiki has stats in tables, often inside div class="char-attr"
    # 2. Extract Skills
    # 3. Extract Talents
    # Since PRTS HTML structure is very complex, we'll extract all raw text
    # from relevant sections and let DeepSeek-R1 structure it.
    
    # For now, we'll extract the main content text to pass to LLM
    content_div = soup.find('div', id='mw-content-text')
    
    # Extract text and clean it up (limit length to avoid context overflow)
    raw_text = content_div.text if content_div else ""
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    cleaned_text = '\n'.join(lines)
    
    return {
        "name": name,
        "raw_text": cleaned_text[:10000] # Pass first 10000 chars to LLM
    }

if __name__ == "__main__":
    ops = get_operator_list()
    print(f"Fetched {len(ops)} operators.")
    if ops:
        test_op = ops[0]
        print(f"Fetching data for {test_op}...")
        html = fetch_operator_html(test_op)
        data = parse_operator_data(html, test_op)
        
        with open('test_operator.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Done. Saved to test_operator.json")
