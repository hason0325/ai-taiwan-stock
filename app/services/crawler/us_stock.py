import yfinance as yf
import time
from datetime import datetime
import pytz
from config import Config


def fetch_us_stock():
    """
    抓取美股四大指數：道瓊、S&P500、那斯達克、費半
    回傳格式：
    {
        'dow_jones': {'close': 39450.23, 'change_percent': 0.85, 'change_points': 335.67},
        ...
    }
    """
    try:
        # 使用不同的代碼格式
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

                    # 漲跌幅 (%)
                    change_percent = ((last_close - prev_close) / prev_close) * 100

                    # 漲跌點數 (價格變動)
                    change_points = last_close - prev_close

                    result[name] = {
                        'close': round(last_close, 2),
                        'change_percent': round(change_percent, 2),  # 漲跌幅 %
                        'change_points': round(change_points, 2)  # 漲跌點數
                    }
                    print(f"✅ {name}: {last_close:.2f} ({change_points:+.2f}, {change_percent:+.2f}%)")
                else:
                    print(f"⚠️ {name}: 資料不足")

            except Exception as e:
                print(f"❌ {name} 失敗: {e}")

            time.sleep(0.3)

        # 加入更新時間
        if result:
            tz = pytz.timezone(Config.TIMEZONE)
            result['updated_at'] = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

        return result if result else None

    except Exception as e:
        print(f"美股爬蟲失敗: {e}")
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
            if name != 'updated_at':
                change_emoji = "🟢" if values['change_points'] > 0 else "🔴" if values['change_points'] < 0 else "⚪"
                print(
                    f"  {change_emoji} {name}: {values['close']:,.2f} ({values['change_points']:+.2f}, {values['change_percent']:+.2f}%)")
    else:
        print("\n❌ 所有數據抓取失敗")