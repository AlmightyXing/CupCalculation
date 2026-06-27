"""
PRTS Wiki 网页爬虫
通过请求干员页面，提取关键的数据文本，以供大模型解析
"""

import requests
from bs4 import BeautifulSoup
import re

PRTS_BASE_URL = "https://prts.wiki/w/{}"

def fetch_operator_page(operator_name: str) -> str:
    """
    请求干员页面，返回 HTML 源码。
    """
    url = PRTS_BASE_URL.format(operator_name)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"无法获取干员页面: {operator_name}, 状态码: {response.status_code}")
    
    response.encoding = 'utf-8'
    return response.text

def extract_relevant_text(html_content: str) -> str:
    """
    从 HTML 中提取有用的文本。
    为保证涵盖基础面板、信赖、天赋、技能等，我们提取主要内容区域 (mw-parser-output) 的文本。
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 移除不需要的标签，减少干扰文本
    for tag in soup(["script", "style", "nav", "footer", "meta", "link"]):
        tag.decompose()
        
    # 尝试寻找页面的主要内容容器
    content_div = soup.find("div", class_="mw-parser-output")
    if not content_div:
        # 降级处理，使用 body
        content_div = soup.body
        
    # 如果找不到内容容器，则返回空
    if not content_div:
        return ""
        
    # 提取多行纯文本，按行去重叠及空行
    text = content_div.get_text(separator="\n", strip=True)
    
    # 简单的文本清理
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # 跳过空行或者过短的可能无意义的行
        if line:
            cleaned_lines.append(line)
            
    # 将列表拼接，作为最终给大模型的语料。
    # 考虑到文本长度可能较大，我们保留全量供 LLM 自行提取。
    return "\n".join(cleaned_lines)

def crawl_operator(operator_name: str) -> str:
    """
    一键爬取并提取干员相关文本
    """
    html = fetch_operator_page(operator_name)
    text = extract_relevant_text(html)
    return text
