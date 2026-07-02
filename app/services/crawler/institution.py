"""
三大法人買賣超爬蟲
資料來源: FinMind API (免費)
"""
import requests
import time
from datetime import datetime, timedelta
import pytz
from config import Config


def fetch_institution():
    """
    抓取三大法人買賣超
    使用 FinMind 免費 API
    """
    try:
        print("  📊 抓取三大法人買賣超...")

        tz = pytz.timezone(Config.TIMEZONE)
        now = datetime.now(tz)
        date_str = now.strftime('%Y-%m-%d')

        # 使用 FinMind API (免費，無需 API Key)
        url = "https://api.finmind.tw/api/v3/data"
        params = {
            'dataset': 'TaiwanStockInstitution',
            'date': date_str,
            'stock_id': '2330'  # 台積電
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if data.get('data') and len(data['data']) > 0:
                latest = data['data'][0]

                result = {
                    'foreign_invest': latest.get('Foreign_Invest', 0),  # 外資
                    'investment_trust': latest.get('Investment_Trust', 0),  # 投信
                    'dealer': latest.get('Dealer', 0),  # 自營商
                    'total': latest.get('Foreign_Invest', 0) + latest.get('Investment_Trust', 0) + latest.get('Dealer',
                                                                                                              0),
                    'date': date_str,
                    'source': 'FinMind API'
                }

                print(
                    f"  ✅ 三大法人: 外資 {result['foreign_invest']:+.2f} 億, 投信 {result['investment_trust']:+.2f} 億, 自營 {result['dealer']:+.2f} 億")
                return result
            else:
                # 如果今天沒數據，抓昨天的
                yesterday = now - timedelta(days=1)
                date_str = yesterday.strftime('%Y-%m-%d')
                params['date'] = date_str
                response = requests.get(url, params=params, headers=headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('data') and len(data['data']) > 0:
                        latest = data['data'][0]
                        result = {
                            'foreign_invest': latest.get('Foreign_Invest', 0),
                            'investment_trust': latest.get('Investment_Trust', 0),
                            'dealer': latest.get('Dealer', 0),
                            'total': latest.get('Foreign_Invest', 0) + latest.get('Investment_Trust', 0) + latest.get(
                                'Dealer', 0),
                            'date': date_str,
                            'source': 'FinMind API'
                        }
                        print(f"  ✅ 三大法人 (昨日): 外資 {result['foreign_invest']:+.2f} 億")
                        return result

        print("  ⚠️ 三大法人抓取失敗，使用模擬數據")
        return get_mock_institution()

    except Exception as e:
        print(f"  ❌ 三大法人抓取失敗: {e}")
        return get_mock_institution()


def get_mock_institution():
    """模擬三大法人數據 (當 API 失敗時)"""
    import random
    tz = pytz.timezone(Config.TIMEZONE)
    now = datetime.now(tz)

    return {
        'foreign_invest': round(random.uniform(-80, 80), 2),
        'investment_trust': round(random.uniform(-30, 30), 2),
        'dealer': round(random.uniform(-20, 20), 2),
        'total': 0,
        'date': now.strftime('%Y-%m-%d'),
        'source': '模擬數據',
        'is_mock': True
    }


# 測試用
if __name__ == '__main__':
    print("=" * 50)
    print("📊 三大法人爬蟲測試")
    print("=" * 50)
    data = fetch_institution()
    if data:
        print(f"外資: {data['foreign_invest']:+.2f} 億")
        print(f"投信: {data['investment_trust']:+.2f} 億")
        print(f"自營: {data['dealer']:+.2f} 億")