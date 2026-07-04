import requests
from bs4 import BeautifulSoup
import json

def main():
    url = "https://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88"
    print("正在获取网页数据...")
    
    # 也可以加上 headers 伪装成浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # PRTS 的干员数据存储在 id 为 filter-data 的 div 内部
    filter_data = soup.find(id="filter-data")
    if not filter_data:
        print("未能找到干员数据，网页结构可能已更改。")
        return
        
    operators = filter_data.find_all("div")
    
    results = []
    for op in operators:
        # 在 PRTS 中，data-rarity 属性是实际星级减 1，因此 5 代表六星
        if op.get("data-rarity") == "5":
            zh_name = op.get("data-zh")
            en_name = op.get("data-en")
            if zh_name:
                results.append({"中文名": zh_name, "英文名": en_name})
            
    print(f"共找到 {len(results)} 位六星干员。")
    
    # 写入 JSON 文件
    output_file = "6star_operators_names.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    print(f"结果已保存到 {output_file}")

if __name__ == "__main__":
    main()
