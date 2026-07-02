"""
盤中監控模組
從證交所官方網站抓取即時數據
"""
import requests
import re
from datetime import datetime, timedelta
import pytz
from config import Config


class IntradayMonitor:
    """盤中監控器"""

    def __init__(self):
        self.tz = pytz.timezone(Config.TIMEZONE)

    def get_tw_index(self):
        """
        從 Yahoo Finance 抓取加權指數，修正漲跌計算
        """
        try:
            import yfinance as yf
            ticker = yf.Ticker("^TWII")

            # 抓取最近 5 天數據，確保有昨日收盤
            data = ticker.history(period="5d")

            if data.empty:
                return None

            # 最新數據
            last = data.iloc[-1]
            current = last['Close']

            # 昨日收盤 (前一天的 Close)
            if len(data) >= 2:
                prev_close = data['Close'].iloc[-2]
            else:
                prev_close = current

            # 正確的漲跌 = 今日收盤 - 昨日收盤
            change = current - prev_close
            change_percent = (change / prev_close) * 100

            # 當日開盤
            open_price = data['Open'].iloc[-1] if 'Open' in data else current

            # 當日最高/最低
            high = data['High'].iloc[-1] if 'High' in data else current
            low = data['Low'].iloc[-1] if 'Low' in data else current

            # 成交量 (加權指數的 Volume 常常是 0，嘗試從其他欄位取得)
            volume = data['Volume'].iloc[-1] if 'Volume' in data else 0
            if volume == 0:
                # 如果成交量為 0，使用預估或顯示 N/A
                volume = None

            return {
                'current': round(current, 2),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'prev_close': round(prev_close, 2),  # 🆕 昨日收盤
                'change': round(change, 2),          # 🆕 正確漲跌
                'change_percent': round(change_percent, 2),  # 🆕 正確漲跌幅
                'volume': volume,
                'source': 'Yahoo Finance'
            }

        except Exception as e:
            print(f"⚠️ 加權指數抓取失敗: {e}")
            return None

    def _is_market_open(self):
        """判斷是否為交易時段"""
        now = datetime.now(self.tz)
        weekday = now.weekday()
        hour = now.hour
        minute = now.minute

        if weekday >= 5:
            return False

        if (hour == 9 and minute >= 0) or (10 <= hour <= 12) or (hour == 13 and minute <= 30):
            return True

        return False

    def get_market_status(self, prediction=None):
        """取得完整的市場狀態"""
        actual = self.get_tw_index()

        if not actual:
            return {
                'is_market_open': self._is_market_open(),
                'actual': None,
                'comparison': None,
                'updated_at': datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')
            }

        status = {
            'is_market_open': self._is_market_open(),
            'actual': actual,
            'updated_at': datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')
        }

        return status


def get_intraday_status(prediction=None):
    """取得盤中狀態"""
    monitor = IntradayMonitor()
    status = monitor.get_market_status(prediction)

    if status['actual']:
        actual = status['actual']
        if status['is_market_open']:
            status['display_status'] = '🟢 交易中'
        else:
            status['display_status'] = '⏸️ 已收盤'

    return status