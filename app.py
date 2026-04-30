# -*- coding: utf-8 -*-
"""
大宗商品追踪系统 v1.4
- 全球市场数据
- 宏观资讯
- 7x24财经新闻
- 全部28个品种
"""

from flask import Flask, render_template, jsonify, request, redirect, session
import os, json

app = Flask(__name__)
app.secret_key = 'dh1204_v14_2026'
app.config['JSON_AS_ASCII'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRICES_FILE = os.path.join(BASE_DIR, 'prices.json')

def load_prices():
    try:
        with open(PRICES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_prices(data):
    with open(PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

PRICES = load_prices()

NOTES_FILE = os.path.join(BASE_DIR, 'notes.json')
GLOBAL_FILE = os.path.join(BASE_DIR, 'global.json')

def load_notes():
    try:
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_global():
    try:
        with open(GLOBAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

PRICES = load_prices()
GLOBAL_DATA = load_global()

REPORTS_FILE = os.path.join(BASE_DIR, 'reports.json')

def load_reports():
    try:
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

REPORTS_DATA = load_reports()

NEWS_FILE = os.path.join(BASE_DIR, 'news.json')

def load_news():
    try:
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

NEWS_DATA = load_news()

VIX_FILE = os.path.join(BASE_DIR, 'vix_data.json')

def load_vix():
    try:
        with open(VIX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'update_time': '', 'varieties': {}}

VIX_DATA = load_vix()

PCR_FILE = os.path.join(BASE_DIR, 'pcr.json')

def load_pcr():
    try:
        with open(PCR_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

PCR_DATA = load_pcr()

def reload_pcr():
    global PCR_DATA
    try:
        with open(PCR_FILE, 'r', encoding='utf-8') as f:
            PCR_DATA = json.load(f)
    except:
        pass

def reload_vix():
    global VIX_DATA
    try:
        with open(VIX_FILE, 'r', encoding='utf-8') as f:
            VIX_DATA = json.load(f)
    except:
        pass

def load_notes():
    try:
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_notes(data):
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

CODES = ['IM','IF','CU','AL','NI','AU','AG','AO','I','RB','JM','HC','SM',
         'SC','MA','TA','EB','RU','P','M','LH','CF','SR','SA','FG','LC','ZN','Y','PX']

NAMES = {
    'IM':'中证1000','IF':'沪深300','CU':'沪铜','AL':'沪铝','NI':'沪镍',
    'AU':'沪金','AG':'沪银','AO':'氧化铝','I':'铁矿石','RB':'螺纹钢',
    'JM':'焦煤','HC':'热卷','SM':'锰硅','SC':'原油','MA':'甲醇',
    'TA':'PTA','EB':'苯乙烯','RU':'天然橡胶','P':'棕榈油','M':'豆粕',
    'LH':'生猪','CF':'棉花','SR':'白糖','SA':'纯碱','FG':'玻璃','LC':'碳酸锂',
    'ZN':'沪锌','Y':'豆油','PX':'对二甲苯'
}

CATS = {
    'IM':'股指','IF':'股指','CU':'有色','AL':'有色','NI':'有色',
    'AU':'贵金属','AG':'贵金属','AO':'有色','I':'黑色','RB':'黑色',
    'JM':'黑色','HC':'黑色','SM':'黑色','SC':'能源','MA':'化工',
    'TA':'化工','EB':'化工','RU':'农产品','P':'农产品','M':'农产品',
    'LH':'农产品','CF':'农产品','SR':'农产品','SA':'建材','FG':'建材','LC':'有色',
    'ZN':'有色','Y':'农产品','PX':'化工'
}

DIRS = {
    'IM':'📊 股指期货','IF':'📊 股指期货','CU':'⚠️ 观望','AL':'✅ 偏多',
    'NI':'❌ 禁止开仓','AU':'📊 偏多(避险)','AG':'📊 跟随黄金','AO':'📊 关注',
    'I':'✅ 多头止损790','RB':'📊 成本支撑','JM':'✅ 震荡偏强',
    'HC':'📊 关注','SM':'🏆 聚焦品种','SC':'🌊 地缘影响大','MA':'📊 成本支撑',
    'TA':'📊 成本主导','EB':'📊 成本定价','RU':'🔔 三重逻辑','P':'📊 跟随马盘',
    'M':'📊 跟随美豆','LH':'🐷 养殖周期','CF':'📊 关注','SR':'📊 关注',
    'SA':'📊 关注','FG':'📊 关注','LC':'🏆 聚焦品种',
    'ZN':'📊 关注','Y':'📊 跟随美豆','PX':'🏆 聚焦品种'
}

# ===== 投资框架数据（关键品种详细，其余简化）=====
FRAMES = {
    'LC': {'name':'碳酸锂','unit':'元/吨','direction':'🏆 聚焦品种 · 偏多','position':'🏆 聚焦','update_date':'2026-04-24',
           'key_levels':[('¥80,000+','偏强','neutral'),('¥72,000-75,000','支撑区','long'),('¥65,000以下','长线布局区','long')],
           'macro':{'核心指标':'锂价 · 新能源车产销','当前判断':'澳矿成本支撑，需求旺季临近','观察点':['锂辉石价格','磷酸铁锂排产']},
           'supply':{'核心指标':'进口量 · 盐湖产量','当前判断':'进口窗口收窄，供应压力缓解','观察点':['澳矿发运','宜春矿端']},
           'signal_long':'澳矿成本支撑+需求旺季+去库','signal_short':'供过于求预期','reversal':'价格涨但去库放缓',
           'news':['下游节前备库启动','澳矿到港量下降'],'reports': [{'inst': 'GSX', 'date': '2026-04-29', 'title': 'Higher for Longer Pt 2: China Energy Security', 'bull': 'Bullish', 'summary': '美伊战争持续超预期，全球能源"更高更久"格局确立；中国能源安全战略受益'}, {'inst': 'JPM', 'date': '2026-04-28', 'title': 'OPECxit: UAE to leave OPEC', 'bull': 'Neutral', 'summary': 'UAE为OPEC第三大产油国（3.9mb/d）；霍尔木兹关闭阻止出口；冲突正常化后增加供应'}, {'inst': 'ANZ', 'date': '2026-04-29', 'title': 'OPEC still relevant but less decisive', 'bull': 'Neutral', 'summary': 'UAE退出OPEC正式化，短期影响有限；中期额外供应约1.0mb/d；风险不对称'}, {'inst': 'RiskMacro', 'date': '2026-04-30', 'title': 'X-Asset Dashboard', 'bull': 'Neutral', 'summary': '新兴市场股票/铜/大豆跑赢；黄金白银波动率偏度显示避险升温'}, {'inst': 'JPM', 'date': '2026-04-26', 'title': 'Press Metal升级至OW：铝短缺1.9mt，升水飙至$300/t', 'bull': 'Bullish', 'summary': '目标价RM10.10（Street最高）；铝短缺1.9mt；MJP升水从$140飙至$300/t；实际库存仅9天'}, {'inst': 'JPM', 'date': '2026-04-27', 'title': 'China Metals Activity Tracker: 6周铜强势去库', 'bull': 'Bullish', 'summary': '中国铜库存6周减少超250kt，降至245kt（10年同期最低）；LME铜$13,000以上持续买入'}, {'inst': 'BOA', 'date': '2026-04-24', 'title': 'Global Metals Weekly: Sulphuric acid corrodes copper margins', 'bull': 'Bullish', 'summary': '全球硫磺供应受霍尔木兹中断冲击；约1Mt铜矿供应面临风险；中国电网Q1投资+37%'}]},

    'SM': {'name':'锰硅','unit':'元/吨','direction':'🏆 聚焦品种 · 震荡偏强','position':'🏆 聚焦','update_date':'2026-04-24',
           'key_levels':[('¥8,500+','偏强','neutral'),('¥7,000-7,500','支撑区','long'),('¥6,500以下','偏弱','short')],
           'macro':{'核心指标':'南方限电 · 锰矿价格','当前判断':'南方限电收紧供应，成本坚挺','观察点':['南方电网限电','锰矿进口量']},
           'supply':{'核心指标':'主产区开工率 · 钢厂招标','当前判断':'产区开工降，招标价上调','观察点':['硅锰开工率','天津港锰矿库存']},
           'signal_long':'南方限电加剧+锰矿大涨+招标价上调','signal_short':'限电解除+锰矿到港增加','reversal':'招标价涨但现货跟涨乏力',
           'news':['南方限电影响贵州/广西产区','锰矿价格坚挺'],'reports':[]},

    'JM': {'name':'焦煤','unit':'元/吨','direction':'✅ 震荡偏强','position':'✅ 持仓','update_date':'2026-04-24',
           'key_levels':[('¥1,300+','偏强','neutral'),('¥1,100-1,150','支撑区','long'),('¥1,000以下','偏弱','short')],
           'macro':{'核心指标':'澳煤政策 · 蒙煤通关','当前判断':'蒙煤通关正常，供应稳定','观察点':['中蒙口岸通关车数']},
           'supply':{'核心指标':'煤矿安检 · 焦化厂开工率','当前判断':'主产区安检持续，供应略紧','观察点':['安检范围','焦化厂库存天数']},
           'signal_long':'安检升级+焦化厂集中补库','signal_short':'澳煤政策放松+焦化厂限产','reversal':'焦化厂库存高企仍压价采购',
           'news':['主产区安检持续','蒙煤通关800车/日'],'reports':[]},


    'IM': {'name':'中证1000','unit':'点','direction':'📊 震荡','position':'📊 股指','update_date':'2026-04-30',
           'key_levels':[('6200+','强阻力','neutral'),('5800-6200','震荡','neutral'),('5500-5800','支撑','long'),('5500以下','偏弱','short')],
           'macro':{'核心指标':'A股情绪 · 流动性 · 美股联动','当前判断':'Trump-Xi峰会5月14-15日为市场核心催化剂','观察点':['北向资金','两融余额','美股走势']},
           'supply':{'核心指标':'期货升贴水 · 持仓量','当前判断':'贴水结构，空头占优','观察点':['升贴水变化','持仓量']},
           'signal_long':'政策刺激超预期+北向大幅净流入+贴水收窄','signal_short':'美股大跌+北向大幅净流出+升水转贴水','reversal':'升水扩大但指数不涨',
           'news':[],'reports':[{'inst': 'JPM', 'date': '2026-04-27', 'title': 'US Market Intel Afternoon Briefing', 'bull': 'Bullish', 'summary': '美股财报季开局强劲，Visa涨幅超8%；标普利润率升至13.4%；中东推油价WTI至$106.88'}, {'inst': 'ANZ', 'date': '2026-04-30', 'title': "Monetary Policy Expectations: What's Priced In", 'bull': 'Neutral', 'summary': '新西兰5月降10bp；欧洲央行降3bp；美联储全年仅降2bp；全球央行政策分化'}, {'inst': 'GS', 'date': '2026-04-29', 'title': 'US Big Tech Names: Inovance TP raise, BYD strong 1Q26', 'bull': 'Bullish', 'summary': 'Inovance目标价上调；BYD 1Q26强劲；算力需求持续高景气'}]},

    'IF': {'name':'沪深300','unit':'点','direction':'📊 震荡','position':'📊 股指','update_date':'2026-04-30',
           'key_levels':[('4200+','强阻力','neutral'),('3500-3800','支撑','long'),('3500以下','偏弱','short')],
           'macro':{'核心指标':'PMI·人民币汇率·美股','当前判断':'PPI通缩趋缓，企业盈利改善','观察点':['PMI','人民币']},
           'supply':{'核心指标':'期货升贴水','当前判断':'贴水结构，谨慎情绪','观察点':['升贴水']},
           'signal_long':'PMI超预期+北向净流入','signal_short':'美股暴跌+外资流出','reversal':'贴水突然收窄',
           'news':[],'reports':[{'inst': 'JPM', 'date': '2026-04-29', 'title': 'Powell to remain on a divided committee', 'bull': 'Neutral', 'summary': 'Powell明确留任为制衡美联储独立性威胁；3位鹰派票委反对宽松；全年按兵不动'}, {'inst': 'IMF', 'date': '2026-04-29', 'title': 'EM Local Currency Bond Monitor', 'bull': 'Neutral', 'summary': '新兴市场本币债券资金流入监测；汇率波动为主要风险'}]},

    'CU': {'name':'沪铜','unit':'元/吨','direction':'⚠️ 观望','position':'⚠️ 观望','update_date':'2026-04-24',
           'key_levels':[('$13,500+','空单布局区','short'),('$12,000-12,200','分批布局多单','long'),('$11,500以下','长线多头极配区','long')],
           'macro':{'核心指标':'美元指数 · 美伊战争 · 全球PMI','当前判断':'Trump-Xi峰会（5月14-15日）最大宏观催化剂','观察点':['美元指数','霍尔木兹通行量','全球PMI']},
           'supply':{'核心指标':'LME/SHFE库存 · TC/RC · 冶炼厂检修','当前判断':'TC/RC维持低位，非洲湿法铜进口存隐患','观察点':['LME库存','洋山铜溢价','冶炼厂检修量']},
           'signal_long':'TC/RC持续低位+硫酸价格大涨+库存持续去化','signal_short':'产业护盘无力+铜相关股票无法跟进+PMI不及预期','reversal':'铜价走强但股票无法跟进',
           'news':['Trump-Xi峰会5月14-15日','LME铜库存去化加快'],
           'reports':[{'inst':'JPM','date':'2026-04-22','title':'Trump-Xi峰会前瞻','bull':'Neutral','summary':'铜需求预期改善'}]},

    'AL': {'name':'沪铝','unit':'元/吨','direction':'✅ 偏多','position':'✅ 偏多','update_date':'2026-04-24',
           'key_levels':[('¥26,500+','空单布局区','short'),('¥24,000-25,000','震荡整理','neutral'),('¥23,500以下','关注做多机会','long')],
           'macro':{'核心指标':'美伊冲突 · 铝锭物流 · 油价','当前判断':'伊朗袭击中东铝厂，铝价+6%','观察点':['中东局势','铝锭进口量','现货升贴水']},
           'supply':{'核心指标':'LME库存（130万吨）· 铝厂复产','当前判断':'LME库存创同期新高，云南复产低于预期','观察点':['LME库存','铝锭社会库存','铝厂动态']},
           'signal_long':'库存持续去化+铝厂复产不及预期+新能源需求强劲','signal_short':'库存持续攀升+进口大量到港+氧化铝大跌','reversal':'铝价走强但现货贴水扩大',
           'news':['伊朗袭击中东铝厂，铝价+6%','LME库存130万吨（同期最高）'],
           'reports':[{'inst':'JPM','date':'2026-04-21','title':'伊朗铝厂遭袭','bull':'Bullish','summary':'供应冲击推动铝价'}]},

    'NI': {'name':'沪镍','unit':'元/吨','direction':'❌ 系统性亏损，禁止开仓','position':'❌ 禁止开仓','update_date':'2026-04-24',
           'key_levels':[('¥150,000+','偏强','neutral'),('¥135,000-140,000','关键支撑区','neutral'),('¥130,000以下','偏弱','short')],
           'macro':{'核心指标':'印尼镍矿政策 · HPAL进展','当前判断':'印尼政策是最大变量','观察点':['印尼能矿部公告','出口配额']},
           'supply':{'核心指标':'LME/SHFE库存（34万吨历史高位）','当前判断':'库存压力持续压制价格','观察点':['LME镍库存','不锈钢厂开工率']},
           'signal_long':'LME库存持续下降+印尼政策收紧','signal_short':'库存攀升+印尼政策放松','reversal':'月线放量突破后缩量整理',
           'news':['印尼配额政策暂无变化','LME镍库存34万吨（历史高位）'],'reports':[]},

    'I': {'name':'铁矿石','unit':'元/吨','direction':'✅ 多头 · 止损790','position':'✅ 多头止损790','update_date':'2026-04-24',
          'key_levels':[('¥830+','上行突破，做多信号','long'),('¥805-830','预警观察区','neutral'),('¥790以下','止损离场','short')],
          'macro':{'核心指标':'四大矿发运量 · 港口库存','当前判断':'钢厂利润改善+供给扰动','观察点':['四大矿发运','港口库存']},
          'supply':{'核心指标':'澳洲/巴西发货量 · 钢厂补库','当前判断':'港口库存小幅下降，钢厂补库积极','观察点':['港口库存','钢厂库存天数']},
          'signal_long':'月线布林开口>15%+日线突破EMA20+港口库存持续下降','signal_short':'日线跌破EMA20(约¥791)+港口库存突破1.5亿吨','reversal':'价格突破830但持仓量下降',
          'news':['必和必拓发运受限（热带气旋）','钢厂利润改善，补库积极'],'reports':[]},

    'RU': {'name':'天然橡胶','unit':'元/吨','direction':'🔔 三重逻辑 · 偏多','position':'🔔 三重逻辑','update_date':'2026-04-24',
           'key_levels':[('¥18,000+','偏强','neutral'),('¥16,000-17,000','支撑区','long'),('¥15,000以下','长线布局区','long')],
           'macro':{'核心指标':'合成胶负荷 · 天胶进口','当前判断':'顺丁胶停车+4月进口下滑+东南亚断供三重利好','观察点':['顺丁胶停车','4月进口预报']},
           'supply':{'核心指标':'RU-NR价差 · 全钢胎开工率','当前判断':'全钢胎高位，RU-NR收窄=NR强','观察点':['全钢胎开工率','青岛港库存']},
           'signal_long':'NR涨幅>3%+RU-NR收窄>5%+顺丁胶停车持续','signal_short':'厄尔尼诺减弱+进口大量到港','reversal':'RU-NR价差扩大',
           'news':['顺丁胶停车率维持高位','4月天胶进口下降'],
           'reports':[{'inst':'新湖期货','date':'2026-03-25','title':'天胶上涨潜力充足','bull':'Bullish','summary':'三重逻辑叠加，厄尔尼诺加剧供应担忧'}]},

    'SC': {'name':'原油','unit':'元/桶','direction':'🌊 地缘高度不确定','position':'🌊 地缘','update_date':'2026-04-24',
           'key_levels':[('$85+','偏强','neutral'),('$70-85','震荡','neutral'),('$60以下','成本支撑区','long')],
           'macro':{'核心指标':'美伊局势 · OPEC+减产 · 全球需求','当前判断':'霍尔木兹通行受限，伊朗库存撑26天','观察点':['伊朗核谈判','OPEC+产量','全球库存']},
           'supply':{'核心指标':'EIA库存 · 美国产量','当前判断':'美国页岩油增产，OPEC+维持减产','观察点':['EIA周报','美国钻井数']},
           'signal_long':'美伊冲突升级+OPEC+超预期减产','signal_short':'美伊谈判缓和+全球经济衰退','reversal':'伊朗库存耗尽但价格不涨',
           'news':['霍尔木兹通行受限','伊朗库存约26天后耗尽'],'reports':[]},

    'AU': {'name':'沪金','unit':'元/克','direction':'📊 偏多（避险）','position':'📊 避险','update_date':'2026-04-24',
           'key_levels':[('¥1,100+','偏强','neutral'),('¥1,000-1,050','支撑区','long'),('¥950以下','长线布局区','long')],
           'macro':{'核心指标':'美元指数 · 美伊局势 · 实际利率','当前判断':'美伊冲突+去美元化=黄金避险需求强','观察点':['美元指数','美伊局势','全球央行购金']},
           'supply':{'核心指标':'ETF持仓量 · 央行购金','当前判断':'全球央行持续购金，中国连续增持','观察点':['SPDR持仓','中国央行购金']},
           'signal_long':'美伊冲突升级+全球央行超预期购金+美元跌破95','signal_short':'美伊谈判突破+美元突破110+实际利率上行','reversal':'金价创新高但ETF流出',
           'news':['美伊局势紧张','全球央行持续购金'],'reports':[]},

    'IM': {'name':'中证1000','unit':'点','direction':'📊 震荡','position':'📊 股指','update_date':'2026-04-24',
           'key_levels':[('6200+','强阻力','neutral'),('5800-6200','震荡','neutral'),('5500-5800','支撑','long'),('5500以下','偏弱','short')],
           'macro':{'核心指标':'A股情绪 · 流动性 · 美股联动','当前判断':'Trump-Xi峰会5月14-15日为市场核心催化剂','观察点':['北向资金','两融余额','美股走势']},
           'supply':{'核心指标':'期货升贴水 · 持仓量','当前判断':'贴水结构，空头占优','观察点':['升贴水变化','持仓量']},
           'signal_long':'政策刺激超预期+北向大幅净流入+贴水收窄','signal_short':'美股大跌+北向大幅净流出+升水转贴水','reversal':'升水扩大但指数不涨',
           'news':['Trump-Xi峰会5月14-15日为核心催化剂'],'reports':[]},

    # === 简化框架品种 ===
    'IF': {'name':'沪深300','unit':'点','direction':'📊 震荡','position':'📊 股指','update_date':'2026-04-24',
           'key_levels':[('4200+','强阻力','neutral'),('3500-3800','支撑','long'),('3500以下','偏弱','short')],
           'macro':{'核心指标':'PMI·人民币汇率·美股','当前判断':'PPI通缩趋缓，企业盈利改善','观察点':['PMI','人民币']},
           'supply':{'核心指标':'期货升贴水','当前判断':'贴水结构，谨慎情绪','观察点':['升贴水']},
           'signal_long':'PMI超预期+北向净流入','signal_short':'美股暴跌+外资流出','reversal':'贴水突然收窄',
           'news':[],'reports':[{'inst':'JPM','date':'2026-04-22','title':'Trump-Xi峰会前瞻','bull':'Neutral','summary':'MXCN和CSI300受益'}]},

    'AG': {'name':'沪银','unit':'元/千克','direction':'📊 跟随黄金','position':'📊 贵金属','update_date':'2026-04-24',
           'key_levels':[('¥25,000+','偏强','neutral'),('¥18,000-25,000','震荡','neutral'),('¥15,000以下','低位布局','long')],
           'macro':{'核心指标':'黄金走势·美元指数','当前判断':'跟随黄金，弹性更大','观察点':['黄金','金银比']},
           'supply':{'核心指标':'ETF持仓·工业需求','当前判断':'光伏/电子需求平稳','观察点':['光伏装机']},
           'signal_long':'黄金突破+金银比修复','signal_short':'黄金大跌+工业需求下滑','reversal':'金银比突破80',
           'news':[],'reports':[]},

    'AO': {'name':'氧化铝','unit':'元/吨','direction':'📊 成本支撑','position':'📊 关注','update_date':'2026-04-24',
           'key_levels':[('¥4,500+','偏强','neutral'),('¥3,500-4,500','震荡','neutral'),('¥3,000以下','成本支撑区','long')],
           'macro':{'核心指标':'铝土矿价格·烧碱价格','当前判断':'烧碱价格高位，成本支撑强','观察点':['烧碱价格']},
           'supply':{'核心指标':'氧化铝库存','当前判断':'供需基本平衡','观察点':['氧化铝厂库存']},
           'signal_long':'烧碱大涨+铝厂补库','signal_short':'烧碱大跌+库存累积','reversal':'氧化铝与烧碱走势背离',
           'news':['烧碱价格高位，成本支撑较强'],'reports':[]},

    'RB': {'name':'螺纹钢','unit':'元/吨','direction':'📊 成本支撑','position':'📊 关注','update_date':'2026-04-24',
           'key_levels':[('¥4,500+','偏强','neutral'),('¥3,500-4,500','震荡','neutral'),('¥3,000以下','成本支撑区','long')],
           'macro':{'核心指标':'房地产需求·基建投资','当前判断':'地产需求仍弱，基建托底','观察点':['螺纹钢库存']},
           'supply':{'核心指标':'钢厂开工率·库存','当前判断':'供应充足，库存压力不大','观察点':['高炉开工率']},
           'signal_long':'基建加速+钢厂减产','signal_short':'需求下滑+库存累积','reversal':'库存上升但价格仍强',
           'news':['螺纹钢库存小幅下降','基建需求托底'],'reports':[]},

    'HC': {'name':'热卷','unit':'元/吨','direction':'📊 跟随螺纹','position':'📊 关注','update_date':'2026-04-24',
           'key_levels':[('¥4,200+','偏强','neutral'),('¥3,500-4,200','震荡','neutral'),('¥3,000以下','成本支撑区','long')],
           'macro':{'核心指标':'汽车/家电需求·出口','当前判断':'汽车需求回暖，出口旺盛','观察点':['汽车产销']},
           'supply':{'核心指标':'钢厂开工率·库存','当前判断':'供应稳定，库存压力小','观察点':['热卷周产量']},
           'signal_long':'汽车产销超预期+出口大增','signal_short':'需求下滑+库存累积','reversal':'库存上升但价格跟涨',
           'news':['汽车产销数据改善'],'reports':[]},

    'MA': {'name':'甲醇','unit':'元/吨','direction':'📊 成本支撑','position':'📊 关注','update_date':'2026-04-24',
           'key_levels':[('¥3,500+','偏强','neutral'),('¥2,500-3,500','震荡','neutral'),('¥2,200以下','成本支撑区','long')],
           'macro':{'核心指标':'煤炭价格·天然气','当前判断':'煤炭价格稳定，成本支撑','观察点':['内矿价格']},
           'supply':{'核心指标':'甲醇装置开工率·库存','当前判断':'装置检修，供应收紧','观察点':['甲醇开工率']},
           'signal_long':'煤炭上涨+装置意外停车','signal_short':'煤炭下跌+库存累积','reversal':'库存上升但价格不跌',
           'news':['甲醇装置检修中','港口库存下降'],'reports':[]},

    'TA': {'name':'PTA','unit':'元/吨','direction':'📊 成本主导','position':'📊 关注','update_date':'2026-04-24',
           'key_levels':[('¥7,000+','偏强','neutral'),('¥5,500-7,000','震荡','neutral'),('¥5,000以下','成本支撑区','long')],
           'macro':{'核心指标':'聚酯需求·纺织服装出口','当前判断':'聚酯负荷高，需求支撑强','观察点':['聚酯开工率']},
           'supply':{'核心指标':'PTA装置检修·聚酯需求','当前判断':'PTA库存不高，需求稳定','观察点':['PTA周产量']},
           'signal_long':'聚酯需求超预期+装置意外检修','signal_short':'聚酯减产+原油大跌','reversal':'加工费高位但库存累积',
           'news':['聚酯负荷维持高位','PTA装置检修中'],'reports':[]},

    'EB': {'name':'苯乙烯','unit':'元/吨','direction':'📊 成本定价','position':'📊 关注','update_date':'2026-04-24',
           'key_levels':[('¥11,000+','偏强','neutral'),('¥9,000-11,000','震荡','neutral'),('¥8,000以下','成本支撑区','long')],
           'macro':{'核心指标':'纯苯价格·下游需求','当前判断':'纯苯支撑，PS/EPS需求平稳','观察点':['纯苯价格']},
           'supply':{'核心指标':'装置开工率·港口库存','当前判断':'供应稳定，库存不高','观察点':['EB开工率']},
           'signal_long':'纯苯大涨+下游需求超预期','signal_short':'纯苯大跌+装置复产','reversal':'港口库存累积',
           'news':['纯苯价格支撑较强'],'reports':[]},

    'P': {'name':'棕榈油','unit':'元/吨','direction':'📊 跟随马盘','position':'📊 关注','update_date':'2026-04-24',
          'key_levels':[('¥12,000+','偏强','neutral'),('¥9,000-12,000','震荡','neutral'),('¥7,000以下','成本支撑区','long')],
          'macro':{'核心指标':'马棕产量·印尼出口政策','当前判断':'MPOB报告偏多','观察点':['马棕产量']},
          'supply':{'核心指标':'港口库存·豆棕价差','当前判断':'库存不高，豆棕价差收窄','观察点':['港口库存']},
          'signal_long':'马棕大幅减产+印尼收紧出口','signal_short':'马棕复产+需求下滑','reversal':'豆棕价差持续收窄',
          'news':['马棕库存下降','豆棕价差收窄'],'reports':[]},

    'M': {'name':'豆粕','unit':'元/吨','direction':'📊 跟随美豆','position':'📊 饲料','update_date':'2026-04-24',
          'key_levels':[('¥4,500+','偏强','neutral'),('¥3,500-4,500','震荡','neutral'),('¥3,000以下','成本支撑区','long')],
          'macro':{'核心指标':'美豆价格·豆粕库存','当前判断':'跟随美豆，区间震荡','观察点':['CBOT大豆']},
          'supply':{'核心指标':'大豆到港量·油厂开机率','当前判断':'到港量稳定，库存平稳','观察点':['大豆到港']},
          'signal_long':'美豆大涨+饲料需求超预期','signal_short':'美豆大跌+库存累积','reversal':'库存上升但开机率不降',
          'news':['豆粕库存平稳','饲料需求正常'],'reports':[]},

    'LH': {'name':'生猪','unit':'元/吨','direction':'🐷 养殖周期','position':'🐷 养殖','update_date':'2026-04-24',
           'key_levels':[('¥25,000+','偏强','neutral'),('¥18,000-25,000','震荡','neutral'),('¥15,000以下','养殖成本区','long')],
           'macro':{'核心指标':'能繁母猪存栏·收储政策','当前判断':'去产能持续，周期底部','观察点':['能繁母猪','收储']},
           'supply':{'核心指标':'出栏量·屠宰开工率','当前判断':'出栏量高位，供应充足','观察点':['出栏量','屠宰开工']},
           'signal_long':'去产能超预期+收储加码','signal_short':'二次育肥出栏+需求下滑','reversal':'仔猪价格先于肉猪上涨',
           'news':['生猪去产能持续','养殖成本支撑较强'],'reports':[]},

    'CF': {'name':'棉花','unit':'元/吨','direction':'📊 关注','position':'📊 农产品','update_date':'2026-04-24',
           'key_levels':[('¥18,000+','偏强','neutral'),('¥15,000-18,000','震荡','neutral'),('¥13,000以下','成本支撑区','long')],
           'macro':{'核心指标':'美棉价格·新疆棉政策','当前判断':'美棉偏强支撑国内','观察点':['美棉','新疆棉']},
           'supply':{'核心指标':'商业库存·纺企开工率','当前判断':'商业库存偏高，需求平稳','观察点':['商业库存']},
           'signal_long':'美棉大涨+纺企补库','signal_short':'美棉大跌+订单下滑','reversal':'纺企库存持续下降',
           'news':['美棉价格偏强'],'reports':[]},

    'SR': {'name':'白糖','unit':'元/吨','direction':'📊 关注','position':'📊 农产品','update_date':'2026-04-24',
           'key_levels':[('¥8,000+','偏强','neutral'),('¥6,000-8,000','震荡','neutral'),('¥5,500以下','成本支撑区','long')],
           'macro':{'核心指标':'原糖价格·进口成本','当前判断':'原糖偏强，进口窗口收窄','观察点':['原糖','进口成本']},
           'supply':{'核心指标':'国产糖产量·库存','当前判断':'本榨季产量下降，库存偏紧','观察点':['国产糖产量']},
           'signal_long':'原糖大涨+进口利润倒挂','signal_short':'原糖大跌+抛储','reversal':'进口大量到港',
           'news':['原糖偏强运行'],'reports':[]},

    'SA': {'name':'纯碱','unit':'元/吨','direction':'📊 关注','position':'📊 建材','update_date':'2026-04-24',
           'key_levels':[('¥3,500+','偏强','neutral'),('¥2,500-3,500','震荡','neutral'),('¥2,000以下','成本支撑区','long')],
           'macro':{'核心指标':'纯碱产量·下游浮法玻璃','当前判断':'浮法玻璃冷修增加，需求转弱','观察点':['浮法玻璃','纯碱库存']},
           'supply':{'核心指标':'氨碱法/联碱法开工率','当前判断':'开工率高位，供应充足','观察点':['纯碱开工率']},
           'signal_long':'光伏玻璃投产+冷修减少','signal_short':'浮法玻璃大规模冷修','reversal':'纯碱厂库存持续下降',
           'news':['纯碱开工率维持高位'],'reports':[]},

    'FG': {'name':'玻璃','unit':'元/吨','direction':'📊 关注','position':'📊 建材','update_date':'2026-04-24',
           'key_levels':[('¥2,500+','偏强','neutral'),('¥1,800-2,500','震荡','neutral'),('¥1,500以下','成本支撑区','long')],
           'macro':{'核心指标':'房地产竣工·深加工订单','当前判断':'竣工面积下降，需求疲软','观察点':['竣工面积']},
           'supply':{'核心指标':'在产产能·库存','当前判断':'冷修增加，库存压力略缓解','观察点':['在产日熔量']},
           'signal_long':'政策松绑+冷修加速','signal_short':'需求下滑+库存累积','reversal':'库存突然下降',
           'news':['浮法玻璃库存高位','冷修产线增加'],'reports':[]},

    'ZN': {'name':'沪锌','unit':'元/吨','direction':'📊 关注','position':'📊 关注','update_date':'2026-04-24',
           'key_levels':[('¥28,000+','偏强','neutral'),('¥24,000-28,000','震荡','neutral'),('¥22,000以下','成本支撑区','long')],
           'macro':{'核心指标':'锌矿供应·镀锌需求','当前判断':'锌矿供应偏紧，镀锌需求平稳','观察点':['锌矿TC','镀锌板出口']},
           'supply':{'核心指标':'锌矿进口量·冶炼厂开工率','当前判断':'矿端紧张传导至锭','观察点':['锌矿到港','冶炼厂库存']},
           'signal_long':'锌矿大涨+镀锌需求超预期','signal_short':'矿端放松+需求下滑','reversal':'LME库存持续下降',
           'news':['锌矿TC加工费下降','镀锌板出口保持增长'],'reports':[]},

    'Y': {'name':'豆油','unit':'元/吨','direction':'📊 跟随美豆','position':'📊 农产品','update_date':'2026-04-24',
          'key_levels':[('¥12,000+','偏强','neutral'),('¥9,000-12,000','震荡','neutral'),('¥8,000以下','成本支撑区','long')],
          'macro':{'核心指标':'美豆价格·马棕走势','当前判断':'美豆偏强，国内供应偏紧','观察点':['CBOT大豆','马棕产量']},
          'supply':{'核心指标':'大豆到港量·油厂开机率','当前判断':'豆油库存偏低，供应偏紧','观察点':['大豆到港','豆油库存']},
          'signal_long':'美豆大涨+豆油库存持续下降','signal_short':'美豆大跌+油厂累库','reversal':'豆油库存拐头上升',
          'news':['豆油库存持续下降','油厂开机率稳定'],'reports':[]},

    'PX': {'name':'对二甲苯','unit':'元/吨','direction':'🏆 聚焦品种','position':'🏆 聚焦','update_date':'2026-04-24',
           'key_levels':[('¥12,000+','偏强','neutral'),('¥9,000-12,000','震荡','neutral'),('¥7,500以下','成本支撑区','long')],
           'macro':{'核心指标':'PX进口量·聚酯需求','当前判断':'大摩测算PTA利润修复，PX需求支撑强','观察点':['PX进口量','聚酯开工率']},
           'supply':{'核心指标':'PX装置开工率·PTA需求','当前判断':'国内PX新产能释放，供应压力增加','观察点':['PX开工率','PTA开工率']},
           'signal_long':'PTA检修少+聚酯需求强','signal_short':'PX新产能释放+聚酯减产','reversal':'PX社会库存持续下降',
           'news':['聚酯负荷维持高位','PX新装置即将投产'],'reports':[]},
}

# ===== 路由 =====

@app.route('/')
def index():
    frames_data = {}
    for code in CODES:
        f = FRAMES.get(code, {})
        frames_data[code] = {
            'name': f.get('name', NAMES.get(code, code)),
            'direction': f.get('direction', DIRS.get(code, '📊')),
            'position': f.get('position', ''),
            'key_levels': f.get('key_levels', [])
        }
    return render_template('index.html',
        frames_json=json.dumps(frames_data, ensure_ascii=False),
        prices_json=json.dumps(PRICES, ensure_ascii=False),
        global_json=json.dumps(GLOBAL_DATA, ensure_ascii=False),
        reports_json=json.dumps(REPORTS_DATA, ensure_ascii=False),
        news_json=json.dumps(NEWS_DATA, ensure_ascii=False)
    )

@app.route('/variety/<code>')
def variety(code):
    code = code.upper()
    f = FRAMES.get(code, {})
    p = PRICES.get(code, {})
    name = f.get('name', NAMES.get(code, code))
    direction = f.get('direction', DIRS.get(code, '📊'))
    unit = f.get('unit', '')
    dir_class = 'neu'
    if '禁止' in direction or '❌' in direction: dir_class = 'down'
    elif '多' in direction or '偏多' in direction or '✅' in direction: dir_class = 'up'
    notes = load_notes()
    note = notes.get(code, '')
    
    # VIX数据
    reload_vix()
    vix_var = VIX_DATA.get('varieties', {}).get(code, {})
    
    # PCR数据
    reload_pcr()
    pcr_var = PCR_DATA.get(code, {})
    
    return render_template('variety.html',
        code=code, name=name, unit=unit,
        direction=direction, dir_class=dir_class,
        frame=f, price=p, note=note,
        all_codes=CODES, names=NAMES, dirs=DIRS,
        vix_data=vix_var, pcr_data=pcr_var
    )

@app.route('/api/prices')
def api_prices():
    return jsonify(PRICES)

@app.route('/admin')
def admin():
    if request.args.get('pwd') == 'dh1204':
        session['admin'] = True
    if not session.get('admin'):
        return render_template('admin.html', error='请先登录', prices=PRICES, codes=CODES, names=NAMES)
    return render_template('admin.html', error='', prices=PRICES, codes=CODES, names=NAMES)

@app.route('/admin/update', methods=['POST'])
def admin_update():
    if not session.get('admin'):
        return jsonify({'error':'Unauthorized'}), 401
    data = request.get_json()
    code = data.get('code','').upper()
    price = float(data.get('price', 0))
    change = float(data.get('change', 0))
    date = data.get('date', '')
    PRICES[code] = {'price': price, 'change': change, 'date': date}
    save_prices(PRICES)
    return jsonify({'success': True})

@app.route('/admin/reset', methods=['POST'])
def admin_reset():
    if not session.get('admin'):
        return jsonify({'error':'Unauthorized'}), 401
    session.clear()
    return redirect('/')

@app.route('/api/notes/<code>')
def get_notes(code):
    notes = load_notes()
    return jsonify({'note': notes.get(code.upper(), ''), 'all': notes})

@app.route('/api/notes/<code>', methods=['POST'])
def save_note(code):
    data = request.get_json()
    note = data.get('note', '').strip()
    notes = load_notes()
    code = code.upper()
    if note:
        notes[code] = note
    elif code in notes:
        del notes[code]
    save_notes(notes)
    return jsonify({'success': True, 'note': note})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
