"""
國際重大事件日曆
"""
from datetime import datetime, timedelta
import pytz
from config import Config


def fetch_events():
    """
    抓取近期國際重大事件
    目前使用靜態資料，未來可串接 API
    """
    tz = pytz.timezone(Config.TIMEZONE)
    now = datetime.now(tz)

    # 靜態事件資料 (未來可擴充為爬蟲)
    events = [
        {
            'date': now.strftime('%Y-%m-%d'),
            'title': 'FOMC 利率決議',
            'impact': '高',
            'time': '02:00'
        },
        {
            'date': (now + timedelta(days=1)).strftime('%Y-%m-%d'),
            'title': '美國非農就業數據',
            'impact': '高',
            'time': '20:30'
        },
        {
            'date': (now + timedelta(days=2)).strftime('%Y-%m-%d'),
            'title': '台灣央行理監事會議',
            'impact': '中',
            'time': '16:00'
        }
    ]

    return events


def get_important_events():
    """取得重要事件 (影響力高或中)"""
    events = fetch_events()
    return [e for e in events if e['impact'] in ['高', '中']]