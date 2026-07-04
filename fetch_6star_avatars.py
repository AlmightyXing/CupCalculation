import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import unquote

def main():
    url = "https://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88"
    print("正在获取网页数据以提取干员列表...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    filter_data = soup.find(id="filter-data")
    if not filter_data:
        print("未能找到干员数据，网页结构可能已更改。")
        return
        
    operators = filter_data.find_all("div")
    
    # 提取六星干员的中文名
    op_names = [op.get("data-zh") for op in operators if op.get("data-rarity") == "5" and op.get("data-zh")]
    print(f"共找到 {len(op_names)} 位六星干员，准备获取头像。")
    
    save_dir = "6star_avatars"
    os.makedirs(save_dir, exist_ok=True)
    
    session = requests.Session()
    session.headers.update(headers)
    
    batch_size = 50
    downloaded_count = 0
    
    # 由于 MediaWiki 的图像 URL 难以直接由名称拼接（包含 md5 散列），这里使用 PRTS 的 MediaWiki API 来批量获取真实图像直链
    for i in range(0, len(op_names), batch_size):
        batch_names = op_names[i:i+batch_size]
        # 拼接批量查询的文件名，PRTS 头像文件标准命名规则为: 文件:头像_{干员名}.png
        titles = "|".join([f"File:头像_{name}.png" for name in batch_names])
        api_url = f"https://prts.wiki/api.php?action=query&prop=imageinfo&iiprop=url&titles={titles}&format=json"
        
        print(f"正在查询图片 URL (第 {i//batch_size + 1} 批)...")
        try:
            api_resp = session.get(api_url).json()
            pages = api_resp.get("query", {}).get("pages", {})
            
            for page_id, page_data in pages.items():
                if "imageinfo" in page_data:
                    img_url = page_data["imageinfo"][0]["url"]
                    # 提取文件名并处理 URL 编码
                    filename = unquote(img_url.split("/")[-1])
                    
                    print(f"正在下载 {filename}...")
                    img_data = session.get(img_url).content
                    with open(os.path.join(save_dir, filename), "wb") as f:
                        f.write(img_data)
                    downloaded_count += 1
                else:
                    print(f"未找到图片信息: {page_data.get('title')}")
                    
        except Exception as e:
            print(f"查询或下载时发生错误: {e}")
            
        time.sleep(1) # 遵守请求礼仪
        
    print(f"下载完成，共保存了 {downloaded_count} 个头像至 '{save_dir}' 文件夹。")

if __name__ == "__main__":
    main()
