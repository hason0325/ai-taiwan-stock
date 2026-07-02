"""
大宗商品爬蟲 (油價、黃金)
"""
import yfinance as yf
import time
from datetime import datetime
import pytz
from config import Config


def fetch_oil():
    """
    抓取 WTI 原油價格
    代碼: CL=F
    """
    try:
        ticker = yf.Ticker("CL=F")
        data = ticker.history(period="5d")

        if data is not None and not data.empty and len(data) >= 2:
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            change_points = round(last_close - prev_close, 2)
            change_percent = round(((last_close - prev_close) / prev_close) * 100, 2)

            tz = pytz.timezone(Config.TIMEZONE)
            now = datetime.now(tz)

            # 油價判斷
            if last_close > 85:
                status = '🔴 偏高 (影響通膨)'
            elif last_close > 75:
                status = '🟡 中性'
            else:
                status = '🟢 偏低 (有利經濟)'

            return {
                'close': round(last_close, 2),
                'change_points': change_points,
                'change_percent': change_percent,
                'status': status,
                'updated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Yahoo Finance (CL=F)'
            }
        return None
    except Exception as e:
        print(f"❌ 油價抓取失敗: {e}")
        return None


def fetch_gold():
    """
    抓取黃金價格
    代碼: GC=F
    """
    try:
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period="5d")

        if data is not None and not data.empty and len(data) >= 2:
            last_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            change_points = round(last_close - prev_close, 2)
            change_percent = round(((last_close - prev_close) / prev_close) * 100, 2)

            tz = pytz.timezone(Config.TIMEZONE)
            now = datetime.now(tz)

            # 黃金判斷
            if last_close > 2500:
                status = '🔴 避險需求高'
            elif last_close > 2200:
                status = '🟡 避險需求正常'
            else:
                status = '🟢 避險需求低'

            return {
                'close': round(last_close, 2),
                'change_points': change_points,
                'change_percent': change_percent,
                'status': status,
                'updated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'Yahoo Finance (GC=F)'
            }
        return None
    except Exception as e:
        print(f"❌ 黃金抓取失敗: {e}")
        return None


# 測試用
if __name__ == '__main__':
    print("=" * 50)
    print("📊 大宗商品爬蟲測試")
    print("=" * 50)

    oil = fetch_oil()
    if oil:
        print(f"🛢️ 油價: ${oil['close']:.2f} ({oil['change_points']:+.2f}) {oil['status']}")

    gold = fetch_gold()
    if gold:
        print(f"🥇 黃金: ${gold['close']:.2f} ({gold['change_points']:+.2f}) {gold['status']}")