import requests
import time
from datetime import datetime


def fetch_us_stock_from_investing():
    """
    從 Investing.com 抓取美股數據（透過第三方 API）
    """
    try:
        # 使用免費的 API（無需 API Key）
        url = "https://query1.finance.yahoo.com/v7/finance/quote"

        symbols = ['^DJI', '^GSPC', '^IXIC', '^SOX']
        params = {
            'symbols': ','.join(symbols)
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        result = {}
        mapping = {
            '^DJI': 'dow_jones',
            '^GSPC': 'sp500',
            '^IXIC': 'nasdaq',
            '^SOX': 'philadelphia'
        }

        for item in data.get('quoteResponse', {}).get('result', []):
            symbol = item.get('symbol')
            if symbol in mapping:
                name = mapping[symbol]
                result[name] = {
                    'close': round(item.get('regularMarketPrice', 0), 2),
                    'change': round(item.get('regularMarketChangePercent', 0), 2)
                }
                print(f"✅ {name}: {result[name]['close']} ({result[name]['change']:+.2f}%)")

        return result if result else None

    except Exception as e:
        print(f"備援 API 失敗: {e}")
        return None


def fetch_us_stock():
    """主入口：嘗試多個來源"""
    print("📊 嘗試 Yahoo Finance...")
    result = fetch_us_stock_from_yahoo()

    if not result:
        print("📊 嘗試備援 API...")
        result = fetch_us_stock_from_investing()

    return result


def fetch_us_stock_from_yahoo():
    """使用 yfinance 抓取"""
    import yfinance as yf
    import time

    try:
        symbols = {
            'dow_jones': '^DJI',
            'sp500': '^GSPC',
            'nasdaq': '^IXIC',
            'philadelphia': '^SOX'
        }

        result = {}

        for name, symbol in symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="5d")

                if data is not None and not data.empty and len(data) >= 2:
                    last_close = data['Close'].iloc[-1]
                    prev_close = data['Close'].iloc[-2]
                    change = ((last_close - prev_close) / prev_close) * 100

                    result[name] = {
                        'close': round(last_close, 2),
                        'change': round(change, 2)
                    }
                    print(f"✅ {name}: {last_close:.2f} ({change:+.2f}%)")
                else:
                    print(f"⚠️ {name}: 資料不足")

            except Exception as e:
                print(f"❌ {name} 失敗: {e}")

            time.sleep(0.3)

        return result if result else None

    except Exception as e:
        print(f"Yahoo 爬蟲失敗: {e}")
        return None


# 測試用
if __name__ == '__main__':
    print("📊 開始抓取美股數據...\n")
    data = fetch_us_stock()

    if data:
        print("\n" + "=" * 50)
        print("📊 美股即時數據：")
        print("=" * 50)
        for name, values in data.items():
            change_emoji = "🟢" if values['change'] > 0 else "🔴" if values['change'] < 0 else "⚪"
            print(f"  {change_emoji} {name}: {values['close']:,.2f} ({values['change']:+.2f}%)")
    else:
        print("\n❌ 所有數據抓取失敗")
        print("請檢查網路連線或稍後再試")