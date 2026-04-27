# -*- coding: utf-8 -*-
"""
每日收盘自动更新脚本 v5.0
==========================
- AkShare本地获取：美股/港股/期货真实数据
- Tushare Pro 订阅：期货收盘价 + 持仓量 + 增减持变化率
- 保存 prices.json（含全球市场数据）
- 上传到 PythonAnywhere
"""

import os, sys, json, time, re, argparse
import requests
from datetime import datetime, timedelta

TUSHARE_TOKEN = '5a65cd0f20e940bc31171029df7350412e6e3518ec79531962fc7bf5'
LOCAL_PRICES_FILE = r'C:\Users\stoneridge\OneDrive\Desktop\外资研报\demo_site\prices.json'
GLOBAL_FILE = r'C:\Users\stoneridge\OneDrive\Desktop\外资研报\demo_site\global.json'
NEWS_FILE = r'C:\Users\stoneridge\OneDrive\Desktop\外资研报\demo_site\news.json'

FUTURES_MAP = {
    'CU': {'name': '沪铜',    'ts_code': 'CU.SHF'},
    'AL': {'name': '沪铝',    'ts_code': 'AL.SHF'},
    'NI': {'name': '沪镍',    'ts_code': 'NI.SHF'},
    'AU': {'name': '沪金',    'ts_code': 'AU.SHF'},
    'AG': {'name': '沪银',    'ts_code': 'AG.SHF'},
    'AO': {'name': '氧化铝',  'ts_code': 'AO.SHF'},
    'LC': {'name': '碳酸锂',  'ts_code': 'LC.ZCE'},
    'I':  {'name': '铁矿石',  'ts_code': 'I.DCE'},
    'RB': {'name': '螺纹钢',  'ts_code': 'RB.SHF'},
    'HC': {'name': '热卷',    'ts_code': 'HC.SHF'},
    'JM': {'name': '焦煤',    'ts_code': 'JM.DCE'},
    'SM': {'name': '锰硅',    'ts_code': 'SM.ZCE'},
    'SC': {'name': '原油',    'ts_code': 'SC.INE'},
    'MA': {'name': '甲醇',    'ts_code': 'MA.ZCE'},
    'TA': {'name': 'PTA',     'ts_code': 'TA.ZCE'},
    'EB': {'name': '苯乙烯',  'ts_code': 'EB.DCE'},
    'RU': {'name': '天然橡胶', 'ts_code': 'RU.SHF'},
    'P':  {'name': '棕榈油',  'ts_code': 'P.DCE'},
    'M':  {'name': '豆粕',    'ts_code': 'M.DCE'},
    'LH': {'name': '生猪',    'ts_code': 'LH.DCE'},
    'CF': {'name': '棉花',    'ts_code': 'CF.ZCE'},
    'SR': {'name': '白糖',    'ts_code': 'SR.ZCE'},
    'SA': {'name': '纯碱',    'ts_code': 'SA.ZCE'},
    'FG': {'name': '玻璃',    'ts_code': 'FG.ZCE'},
    'IF': {'name': '沪深300', 'ts_code': 'IF.CFX'},
    'IM': {'name': '中证1000','ts_code': 'IM.CFX'},
    'ZN': {'name': '沪锌',    'ts_code': 'ZN.SHF'},
    'Y':  {'name': '豆油',    'ts_code': 'Y.DCE'},
    'PX': {'name': '对二甲苯','ts_code': 'PX.DCE'},
}

# 全球市场：代码 -> {name, yahoo_code, type}
GLOBAL_SYMBOLS = {
    'SPX':  {'name': '标普500',   'yahoo': '^GSPC',  'type': 'index'},
    'NDX':  {'name': '纳斯达克',   'yahoo': '^NDX',   'type': 'index'},
    'DJI':  {'name': '道琼斯',     'yahoo': '^DJI',   'type': 'index'},
    'VIX':  {'name': '恐慌指数VIX','yahoo': '^VIX',   'type': 'index'},
    'DXY':  {'name': '美元指数',  'yahoo': 'DX-Y.NYB','type': 'fx'},
    'CNH':  {'name': '离岸人民币', 'yahoo': 'CNHX=X', 'type': 'fx'},
    'XAU':  {'name': '黄金现货',   'yahoo': 'GC=F',   'type': 'commodity'},
    'XAG':  {'name': '白银现货',   'yahoo': 'SI=F',   'type': 'commodity'},
    'CL':   {'name': 'WTI原油',   'yahoo': 'CL=F',   'type': 'commodity'},
    'BTC':  {'name': '比特币',     'yahoo': 'BTC-USD','type': 'crypto'},
    'HSI':  {'name': '恒生指数',   'yahoo': '^HSI',   'type': 'index'},
    'NKY':  {'name': '日经225',   'yahoo': '^N225',  'type': 'index'},
}


def get_tushare():
    import tushare as ts
    ts.set_token(TUSHARE_TOKEN)
    return ts.pro_api()


def get_trade_date(pro, days_ago=1):
    # 查询范围往前扩，确保包含最近交易日；end_date用昨天避免取到还没收盘的今天
    end = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')
    df = pro.trade_cal(start_date=start, end_date=end)
    df = df[df['is_open'] == 1]
    # 按日期升序，取倒数第days_ago个（即最近第days_ago个交易日）
    df = df.sort_values('cal_date')
    return df.iloc[-days_ago]['cal_date']


def fetch_yahoo_quotes(symbols):
    """用Yahoo Finance API获取全球市场数据（服务器端可用）"""
    results = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    # Yahoo Finance symbol mapping
    yahoo_map = {
        'SPX': ('^GSPC', '标普500'),
        'NDX': ('^NDX', '纳斯达克'),
        'DJI': ('^DJI', '道琼斯'),
        'VIX': ('^VIX', '恐慌指数VIX'),
        'DXY': ('DX-Y.NYB', '美元指数'),
        'CNH': ('CNHX=X', '离岸人民币'),
        'XAU': ('GC=F', '黄金现货'),
        'XAG': ('SI=F', '白银现货'),
        'CL': ('CL=F', 'WTI原油'),
        'HSI': ('^HSI', '恒生指数'),
        'NKY': ('^N225', '日经225'),
    }
    for code, (sym, name) in yahoo_map.items():
        if code in symbols:
            try:
                url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=3d'
                resp = requests.get(url, headers=headers, timeout=8)
                data = resp.json()
                chart = data.get('result', [{}])[0]
                timestamps = chart.get('timestamp', [])
                quotes = chart.get('indicators', {}).get('quote', [{}])[0]
                if len(timestamps) >= 2:
                    prev_close = quotes['close'][-2]
                    curr_close = quotes['close'][-1]
                    pct = round((curr_close - prev_close) / prev_close * 100, 2)
                    results[code] = {'name': name, 'price': round(curr_close, 2), 'change': pct}
                    print(f"  ✅ {name}({code}): {curr_close:.2f} ({pct:+.2f}%)")
                elif len(timestamps) == 1:
                    curr_close = quotes['close'][-1]
                    results[code] = {'name': name, 'price': round(curr_close, 2), 'change': 0.0}
                    print(f"  ✅ {name}({code}): {curr_close:.2f}")
            except Exception as e:
                print(f"  ⚠️ {code} 获取失败: {str(e)[:50]}")
    return results


def fetch_global_market(pro=None):
    """用Tushare获取中国指数 + Yahoo Finance获取全球市场"""
    print("\n🌏 正在获取全球市场数据...")
    results = {}

    # 1. 用Tushare获取中国指数（前一日收盘）
    cn_indices = {
        'CSI300': ('000300.SH', '沪深300'),
        'CSI500': ('000905.SH', '中证500'),
        'GEM': ('399006.SZ', '创业板指'),
        'HSCEI': ('HSCEI', '恒生国企指数'),
    }
    if pro:
        for code, (ts_code, name) in cn_indices.items():
            try:
                end = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
                start = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')
                if ts_code == 'HSCEI':
                    df = pro.index_daily(ts_code=ts_code, start_date=start, end_date=end)
                else:
                    df = pro.index_daily(ts_code=ts_code, start_date=start, end_date=end)
                if df is not None and len(df) >= 2:
                    df = df.sort_values('trade_date')
                    curr = float(df.iloc[-1]['close'])
                    prev = float(df.iloc[-2]['close'])
                    pct = round((curr - prev) / prev * 100, 2)
                    results[code] = {'name': name, 'price': curr, 'change': pct}
                    print(f"  ✅ {name}({code}): {curr:.2f} ({pct:+.2f}%)")
            except Exception as e:
                print(f"  ⚠️ {code} Tushare失败: {str(e)[:40]}")

    # 2. 用Yahoo Finance获取全球市场（美国、香港、日本）
    global_symbols = ['SPX', 'NDX', 'DJI', 'VIX', 'DXY', 'XAU', 'XAG', 'CL', 'HSI', 'NKY']
    yahoo_results = fetch_yahoo_quotes(global_symbols)
    results.update(yahoo_results)

    # 3. 静态默认值（兜底）
    defaults = {
        'SPX': {'name': '标普500', 'price': 5300, 'change': 0.0},
        'NDX': {'name': '纳斯达克', 'price': 18500, 'change': 0.0},
        'DJI': {'name': '道琼斯', 'price': 39000, 'change': 0.0},
        'VIX': {'name': '恐慌指数VIX', 'price': 18.0, 'change': 0.0},
        'DXY': {'name': '美元指数', 'price': 99.0, 'change': 0.0},
        'XAU': {'name': '黄金现货', 'price': 2320, 'change': 0.0},
        'XAG': {'name': '白银现货', 'price': 27.5, 'change': 0.0},
        'CL': {'name': 'WTI原油', 'price': 78, 'change': 0.0},
        'HSI': {'name': '恒生指数', 'price': 22000, 'change': 0.0},
        'NKY': {'name': '日经225', 'price': 38000, 'change': 0.0},
        'CSI300': {'name': '沪深300', 'price': 4700, 'change': 0.0},
        'CSI500': {'name': '中证500', 'price': 5600, 'change': 0.0},
        'GEM': {'name': '创业板指', 'price': 1800, 'change': 0.0},
        'CNH': {'name': '离岸人民币', 'price': 7.25, 'change': 0.0},
    }
    for code, val in defaults.items():
        if code not in results:
            results[code] = val
            print(f"  💤 {code} 使用默认值")

    print(f"  📊 全球市场共获取 {len(results)} 个品种")
    return results


def fetch_all_futures(pro, trade_date):
    """获取期货收盘价+持仓量"""
    results = {}
    print(f"\n📡 正在获取 {trade_date} 期货数据...")

    success = 0
    alerts = []

    for code, info in FUTURES_MAP.items():
        try:
            df = pro.fut_daily(ts_code=info['ts_code'], trade_date=trade_date)
            if df is not None and len(df) > 0:
                row = df.iloc[0]
                close = float(row['close'])
                change2 = float(row.get('change2', 0))
                settle = float(row.get('settle', close))
                pct_chg = round(change2 / settle * 100, 2) if settle and settle != 0 else 0.0
                oi = int(row.get('oi', 0)) if row.get('oi') else 0
                oi_chg = int(row.get('oi_chg', 0)) if row.get('oi_chg') else 0
                oi_change_pct = round(oi_chg / (oi - oi_chg) * 100, 1) if (oi - oi_chg) > 0 else 0.0

                results[code] = {
                    'price': close, 'change': pct_chg, 'date': trade_date,
                    'oi': oi, 'oi_chg': oi_chg, 'oi_change': oi_change_pct,
                    'name': info['name']
                }

                arrow = '▲' if pct_chg >= 0 else '▼'
                oi_arrow = '📈' if oi_chg > 0 else ('📉' if oi_chg < 0 else '➡️')
                oi_str = f"持仓{oi/10000:.1f}万手"
                if oi_chg != 0:
                    oi_str += f" ({oi_chg:+,}手, {oi_change_pct:+.1f}%)"
                print(f"  ✅ {info['name']}({code}): ¥{close:,.0f} {arrow}{abs(pct_chg):.2f}% | {oi_str} {oi_arrow}")
                success += 1

                if abs(oi_change_pct) >= 15 and oi > 0:
                    alerts.append({
                        'code': code, 'name': info['name'],
                        'price': close, 'change': pct_chg,
                        'oi': oi, 'oi_chg': oi_chg, 'oi_change': oi_change_pct,
                        'direction': '增仓' if oi_chg > 0 else '减仓',
                        'emoji': '📈' if oi_chg > 0 else '📉'
                    })
            else:
                print(f"  ⚠️ {info['name']}({code}): 无数据")
        except Exception as e:
            print(f"  ❌ {info['name']}({code}): {str(e)[:60]}")
        time.sleep(0.12)

    print(f"\n  📊 成功获取 {success}/{len(FUTURES_MAP)} 个品种")

    if alerts:
        alerts.sort(key=lambda x: -abs(x['oi_change']))
        print(f"\n🚨 持仓异动警报（共 {len(alerts)} 条）")
        print("="*60)
        for a in alerts:
            print(f"{a['emoji']} {a['name']}({a['code']}) {a['direction']} {abs(a['oi_change']):.1f}% | ¥{a['price']:,.0f} | 持仓{a['oi']:,}手 ({a['oi_chg']:+,})")
        print("="*60)

    return results


def fetch_sina_news():
    """获取东方财富快讯（替代失效的新浪7x24）"""
    print("\n📰 正在获取东方财富快讯...")
    news = []
    try:
        url = 'https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_20_1_.html'
        resp = requests.get(url, timeout=10,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                     'Referer': 'https://finance.eastmoney.com/'})
        resp.encoding = 'utf-8'
        text = resp.text
        m = re.search(r'ajaxResult=(\{.*\})', text, re.DOTALL)
        if not m:
            print("  ❌ 数据解析失败")
            return []
        data = json.loads(m.group(1))
        items = data.get('LivesList', [])
        seen = set()
        for item in items:
            title = re.sub(r'<[^>]+>', '', item.get('title', ''))
            time_str = item.get('showtime', '')[11:16]
            source = item.get('source', '东方财富')
            if len(title) > 8:
                k = title[:25]
                if k not in seen:
                    seen.add(k)
                    news.append({'title': title, 'time': time_str, 'source': source, 'hot': False})
        print(f"  ✅ 获取到 {len(news)} 条")
    except Exception as e:
        print(f"  ❌ 获取失败: {e}")
    return news


def load_old_prices():
    try:
        with open(LOCAL_PRICES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def save_prices(data):
    with open(LOCAL_PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已保存 prices.json（{len(data)} 个品种）")


def save_global(data):
    with open(GLOBAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 global.json（{len(data)} 个品种）")


def save_news(data):
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 news.json（{len(data)} 条）")


def upload_to_pythonanywhere():
    print(f"\n📤 上传到 PythonAnywhere...")
    try:
        import paramiko
        pw = os.environ.get('PYANYWHERE_PASSWORD', '')
        if not pw:
            print("  ⚠️ 未设置 PYANYWHERE_PASSWORD")
            return False
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('dh1204.pythonanywhere.com', username='dh1204', password=pw)
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_PRICES_FILE, '/home/dh1204/demo_site/prices.json')
        sftp.put(GLOBAL_FILE, '/home/dh1204/demo_site/global.json')
        sftp.put(NEWS_FILE, '/home/dh1204/demo_site/news.json')
        sftp.close()
        ssh.close()
        print("  ✅ 上传成功！")
        return True
    except Exception as e:
        print(f"  ❌ 上传失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='测试不上传')
    parser.add_argument('--date', type=str, default='', help='指定日期 YYYYMMDD')
    parser.add_argument('--global-only', dest='global_only', action='store_true', help='仅更新全球数据')
    args = parser.parse_args()

    print("="*60)
    print("📊 大宗商品每日更新 v5.0")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # 先初始化Tushare（供全球市场和中国指数使用）
    pro = get_tushare()

    # 全球市场数据
    global_data = fetch_global_market(pro)
    save_global(global_data)

    if args.global_only:
        print("\n✅ 全球数据更新完成")
        return

    # 期货数据
    trade_date = args.date if args.date else get_trade_date(pro)
    print(f"\n📅 交易日: {trade_date}")

    futures_data = fetch_all_futures(pro, trade_date)

    # 合并
    old_prices = load_old_prices()
    for code, v in old_prices.items():
        if code not in futures_data:
            futures_data[code] = v

    save_prices(futures_data)

    # 新闻
    news = fetch_sina_news()
    save_news(news)

    if not args.test:
        upload_to_pythonanywhere()
    else:
        print("\n🧪 测试模式，未上传")

    if news:
        print(f"\n📰 财经快讯（前5条）:")
        for n in news[:5]:
            print(f"  [{n['time']}] {n['title'][:60]}")

    print("\n✅ 完成！")


if __name__ == '__main__':
    main()
