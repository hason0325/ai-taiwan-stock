import yfinance as yf
import time
from datetime import datetime
import pytz
from config import Config


def fetch_tsm_adr():
    """
    抓取台積電 ADR 數據
    TSM: 台積電 ADR (NYSE)
    回傳格式：
    {
        'close': 185.50,
        'change_percent': 1.25,    # 漲跌幅 %
        'change_points': 2.29,     # 漲跌點數
        'tw_price': 1205.75,
        'volume': 12345678,
        'usd_twd': 32.5
    }
    """
    try:
        ticker = yf.Ticker("TSM")
        data = ticker.history(period="5d")

        if data is not None and not data.empty and len(data) >= 2:
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]

            # 漲跌幅 (%)
            change_percent = ((last_close - prev_close) / prev_close) * 100

            # 漲跌點數 (價格變動)
            change_points = last_close - prev_close

            # 使用 config 中的匯率
            usd_twd = Config.USD_TWD

            # 換算成台股價格 (ADR 1股 = 5股台積電)
            tw_price = (last_close * usd_twd) / 5

            result = {
                'close': round(last_close, 2),
                'change_percent': round(change_percent, 2),  # 漲跌幅 %
                'change_points': round(change_points, 2),  # 漲跌點數
                'tw_price': round(tw_price, 2),
                'volume': int(data['Volume'].iloc[-1]) if 'Volume' in data else 0,
                'usd_twd': usd_twd
            }

            tz = pytz.timezone(Config.TIMEZONE)
            now = datetime.now(tz)
            print(
                f"✅ 台積電ADR: ${last_close:.2f} ({change_points:+.2f}, {change_percent:+.2f}%) → 約台股 ${tw_price:.2f} (台灣時間: {now.strftime('%H:%M:%S')})")
            return result
        else:
            print("⚠️ 台積電ADR 資料不足")
            return None

    except Exception as e:
        print(f"❌ 台積電ADR 抓取失敗: {e}")
        return None


def fetch_adr_list():
    """
    抓取多檔ADR (未來可擴充)
    """
    adr_list = {
        'TSM': '台積電',
        'UMC': '聯電',
        'ASE': '日月光',
        'CHT': '中華電信'
    }

    results = {}
    for symbol, name in adr_list.items():
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="5d")

            if data is not None and not data.empty and len(data) >= 2:
                last_close = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                change_percent = ((last_close - prev_close) / prev_close) * 100
                change_points = last_close - prev_close

                results[symbol] = {
                    'name': name,
                    'close': round(last_close, 2),
                    'change_percent': round(change_percent, 2),
                    'change_points': round(change_points, 2)
                }
                print(f"✅ {name} ADR: ${last_close:.2f} ({change_points:+.2f}, {change_percent:+.2f}%)")

            time.sleep(0.3)
        except Exception as e:
            print(f"❌ {name} ADR 抓取失敗: {e}")

    return results


# 測試用
if __name__ == '__main__':
    print("📊 開始抓取台積電ADR...\n")

    tsm = fetch_tsm_adr()
    if tsm:
        print("\n" + "=" * 50)
        print("📊 台積電ADR 即時數據：")
        print("=" * 50)
        print(f"  ADR價格: ${tsm['close']:.2f}")
        print(f"  漲跌點數: {tsm['change_points']:+.2f}")
        print(f"  漲跌幅: {tsm['change_percent']:+.2f}%")
        print(f"  換算台股: ${tsm['tw_price']:.2f}")
        print(f"  成交量: {tsm['volume']:,}")
        print(f"  匯率: {tsm['usd_twd']:.2f}")