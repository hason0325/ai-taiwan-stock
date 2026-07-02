"""
VIX 恐慌指數 + 美元指數 爬蟲
"""
import yfinance as yf
import time
from datetime import datetime
import pytz
from config import Config


def fetch_vix():
    """
    抓取 VIX 恐慌指數
    代碼: ^VIX
    數值越高表示市場越恐慌 (通常 > 25 表示恐慌)
    """
    try:
        ticker = yf.Ticker("^VIX")
        data = ticker.history(period="5d")

        if data is not None and not data.empty and len(data) >= 2:
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            change_points = round(last_close - prev_close, 2)
            change_percent = round(((last_close - prev_close) / prev_close) * 100, 2)

            # 判斷市場情緒
            if last_close <= 15:
                status = '🟢 平靜'
            elif last_close <= 20:
                status = '🟡 正常'
            elif last_close <= 25:
                status = '🟠 警戒'
            else:
                status = '🔴 恐慌'

            tz = pytz.timezone(Config.TIMEZONE)
            now = datetime.now(tz)

            print(f"✅ VIX: {last_close:.2f} ({change_points:+.2f}, {change_percent:+.2f}%) → {status}")

            return {
                'close': round(last_close, 2),
                'change_points': round(change_points, 2),
                'change_percent': round(change_percent, 2),
                'status': status,
                'updated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Yahoo Finance (^VIX)'
            }
        else:
            print("⚠️ VIX 資料不足")
            return None

    except Exception as e:
        print(f"❌ VIX 抓取失敗: {e}")
        return None


def fetch_usd_index():
    """
    抓取美元指數 (DXY)
    代碼: DX-Y.NYB
    美元指數 < 100 偏多，> 103 偏空
    """
    try:
        ticker = yf.Ticker("DX-Y.NYB")
        data = ticker.history(period="5d")

        if data is not None and not data.empty and len(data) >= 2:
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            change_points = round(last_close - prev_close, 2)
            change_percent = round(((last_close - prev_close) / prev_close) * 100, 2)

            # 判斷美元強弱
            if last_close <= 100:
                status = '🟢 弱勢 (有利股市)'
            elif last_close <= 103:
                status = '🟡 中性'
            else:
                status = '🔴 強勢 (不利股市)'

            tz = pytz.timezone(Config.TIMEZONE)
            now = datetime.now(tz)

            print(f"✅ 美元指數: {last_close:.2f} ({change_points:+.2f}, {change_percent:+.2f}%) → {status}")

            return {
                'close': round(last_close, 2),
                'change_points': round(change_points, 2),
                'change_percent': round(change_percent, 2),
                'status': status,
                'updated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Yahoo Finance (DX-Y.NYB)'
            }
        else:
            print("⚠️ 美元指數 資料不足")
            return None

    except Exception as e:
        print(f"❌ 美元指數 抓取失敗: {e}")
        return None


def fetch_usd_twd():
    """
    抓取美元/台幣匯率
    代碼: TWD=X
    """
    try:
        ticker = yf.Ticker("TWD=X")
        data = ticker.history(period="5d")

        if data is not None and not data.empty and len(data) >= 2:
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            change_points = round(last_close - prev_close, 4)
            change_percent = round(((last_close - prev_close) / prev_close) * 100, 2)

            tz = pytz.timezone(Config.TIMEZONE)
            now = datetime.now(tz)

            print(f"✅ 美元/台幣: {last_close:.4f} ({change_points:+.4f}, {change_percent:+.2f}%)")

            return {
                'close': round(last_close, 4),
                'change_points': round(change_points, 4),
                'change_percent': round(change_percent, 2),
                'updated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Yahoo Finance (TWD=X)'
            }
        else:
            print("⚠️ 美元/台幣 資料不足")
            return None

    except Exception as e:
        print(f"❌ 美元/台幣 抓取失敗: {e}")
        return None


# 測試用
if __name__ == '__main__':
    print("=" * 50)
    print("📊 VIX + 美元指數 爬蟲測試")
    print("=" * 50)
    print()

    # VIX
    vix = fetch_vix()
    if vix:
        print(f"VIX: {vix['close']:.2f} ({vix['change_points']:+.2f}) → {vix['status']}")
    print()

    # 美元指數
    usd = fetch_usd_index()
    if usd:
        print(f"美元指數: {usd['close']:.2f} ({usd['change_points']:+.2f}) → {usd['status']}")
    print()

    # 美元/台幣
    twd = fetch_usd_twd()
    if twd:
        print(f"美元/台幣: {twd['close']:.4f} ({twd['change_points']:+.4f})")