"""
技術面分析模組
計算均線、MACD、KD等技術指標判斷
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from config import Config


class TechnicalAnalyzer:
    """技術面分析器"""

    def __init__(self):
        self.tz = pytz.timezone(Config.TIMEZONE)

    def analyze_tw_index(self):
        """
    分析台股加權指數技術面
    """
        try:
            ticker = yf.Ticker("^TWII")
            data = ticker.history(period="6mo")

            if data.empty:
                return None

            # 計算技術指標
            close = data['Close']

            # 1. 均線
            ma5 = close.rolling(5).mean().iloc[-1]
            ma10 = close.rolling(10).mean().iloc[-1]
            ma20 = close.rolling(20).mean().iloc[-1]
            ma60 = close.rolling(60).mean().iloc[-1]
            current = close.iloc[-1]

            # 2. 均線排列
            ma_trend = self._get_ma_trend(current, ma5, ma10, ma20, ma60)

            # 3. RSI
            rsi = self._calculate_rsi(close, 14)

            # 4. MACD
            macd, signal, hist = self._calculate_macd(close)

            # 5. 布林通道
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close, 20)

            # 6. 綜合判斷
            signals = self._generate_signals(current, ma5, ma10, ma20, ma60, rsi, macd, signal, hist, bb_upper,
                                             bb_middle, bb_lower)

            return {
                'current_price': round(current, 2),
                'ma5': round(ma5, 2) if not pd.isna(ma5) else None,
                'ma10': round(ma10, 2) if not pd.isna(ma10) else None,
                'ma20': round(ma20, 2) if not pd.isna(ma20) else None,
                'ma60': round(ma60, 2) if not pd.isna(ma60) else None,
                'ma_trend': ma_trend,
                'rsi': round(rsi, 2),
                'macd': round(macd, 4),
                'macd_signal': round(signal, 4),
                'macd_histogram': round(hist, 4),
                'bb_upper': round(bb_upper, 2) if not pd.isna(bb_upper) else None,
                'bb_middle': round(bb_middle, 2) if not pd.isna(bb_middle) else None,
                'bb_lower': round(bb_lower, 2) if not pd.isna(bb_lower) else None,
                'signals': signals,
                'updated_at': datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            print(f"⚠️ 技術面分析失敗: {e}")
            return None

    def _get_ma_trend(self, current, ma5, ma10, ma20, ma60):
        """判斷均線排列趨勢"""
        if not all([current, ma5, ma10, ma20, ma60]):
            return '數據不足'

        if current > ma5 > ma10 > ma20 > ma60:
            return '多頭排列 (強勢)'
        elif current > ma5 and ma5 > ma10 and ma10 > ma20:
            return '短線多頭'
        elif current < ma5 < ma10 < ma20 < ma60:
            return '空頭排列 (弱勢)'
        elif current < ma5 and ma5 < ma10 and ma10 < ma20:
            return '短線空頭'
        else:
            return '震盪整理'

    def _calculate_rsi(self, prices, period=14):
        """計算 RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """計算 MACD"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd.iloc[-1], macd_signal.iloc[-1], macd_hist.iloc[-1]

    def _calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """計算布林通道"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper.iloc[-1], middle.iloc[-1], lower.iloc[-1]

    def _generate_signals(self, current, ma5, ma10, ma20, ma60, rsi, macd, signal, hist, bb_upper, bb_middle, bb_lower):
        """生成技術信號"""
        signals = []

        # 均線信號
        if current > ma5 and ma5 > ma10:
            signals.append('✅ 短期均線多頭')
        elif current < ma5 and ma5 < ma10:
            signals.append('❌ 短期均線空頭')

        # RSI 信號
        if rsi > 70:
            signals.append('⚠️ RSI 過熱 (>70)，可能回檔')
        elif rsi < 30:
            signals.append('💡 RSI 超賣 (<30)，可能反彈')
        elif 40 < rsi < 60:
            signals.append('➖ RSI 中性區間')

        # MACD 信號
        if macd > signal and hist > 0:
            signals.append('✅ MACD 黃金交叉 (買進訊號)')
        elif macd < signal and hist < 0:
            signals.append('❌ MACD 死亡交叉 (賣出訊號)')

        # 布林通道信號
        if current > bb_upper:
            signals.append('⚠️ 價格突破上軌，過熱')
        elif current < bb_lower:
            signals.append('💡 價格跌破下軌，超賣')

        return signals


def get_technical_summary():
    """取得技術面摘要"""
    analyzer = TechnicalAnalyzer()
    result = analyzer.analyze_tw_index()

    if result:
        # 簡化摘要
        summary = {
            'trend': result['ma_trend'],
            'rsi': result['rsi'],
            'macd_signal': '黃金交叉' if result['macd'] > result['macd_signal'] else '死亡交叉' if result['macd'] <
                                                                                                   result[
                                                                                                       'macd_signal'] else '持平',
            'signals_count': len(result['signals']),
            'signals': result['signals'],
            'bb_position': '上軌' if result['current_price'] > result['bb_upper'] else '下軌' if result[
                                                                                                     'current_price'] <
                                                                                                 result[
                                                                                                     'bb_lower'] else '中軌'
        }
        return summary

    return None