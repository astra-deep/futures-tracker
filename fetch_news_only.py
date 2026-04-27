# -*- coding: utf-8 -*-
"""
PythonAnywhere专用 - 新闻定时抓取
每天8:00-18:00每2小时运行一次
"""
import re, json, requests

def fetch_news():
    url = 'https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_20_1_.html'
    r = requests.get(url, timeout=15,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                 'Referer': 'https://finance.eastmoney.com/'})
    r.encoding = 'utf-8'
    m = re.search(r'ajaxResult=(\{.*\})', r.text, re.DOTALL)
    if not m:
        return []
    data = json.loads(m.group(1))
    news = []
    seen = set()
    for item in data.get('LivesList', []):
        title = re.sub(r'<[^>]+>', '', item.get('title', ''))
        time_str = item.get('showtime', '')[11:16]
        source = item.get('source', '东方财富')
        if len(title) > 8 and title[:25] not in seen:
            seen.add(title[:25])
            news.append({'title': title, 'time': time_str, 'source': source, 'hot': False})
    return news

if __name__ == '__main__':
    news = fetch_news()
    print(f'获取到 {len(news)} 条')

    out = '/home/dh1204/demo_site/news.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    print(f'已保存到 {out}')
