"""
歷史驗證模組
每日比對預測與實際，計算命中率
"""
from app import db
from app.models import AnalysisResult, Verification
from datetime import datetime, timedelta
import pytz
from config import Config


class Verifier:
    """歷史驗證器"""

    def __init__(self):
        self.tz = pytz.timezone(Config.TIMEZONE)

    def verify_daily(self, date=None):
        """
        驗證單日預測與實際
        """
        if not date:
            date = datetime.now(self.tz).date() - timedelta(days=1)

        # 取得該日的分析結果
        analysis = AnalysisResult.query.filter_by(date=date).first()
        if not analysis:
            return None

        # 取得實際的大盤數據 (從期交所或 Yahoo Finance)
        actual_data = self._fetch_actual_data(date)
        if not actual_data:
            return None

        # 計算誤差
        verification = Verification(
            date=date,
            predicted_open=analysis.predict_open,
            predicted_close=analysis.predict_close,
            predicted_high=analysis.predict_high,
            predicted_low=analysis.predict_low,
            predicted_sentiment=analysis.sentiment,
            actual_open=actual_data['open'],
            actual_close=actual_data['close'],
            actual_high=actual_data['high'],
            actual_low=actual_data['low'],
            actual_sentiment=actual_data['sentiment'],
            open_error=round(analysis.predict_open - actual_data['open'], 2),
            close_error=round(analysis.predict_close - actual_data['close'], 2),
            high_error=round(analysis.predict_high - actual_data['high'], 2),
            low_error=round(analysis.predict_low - actual_data['low'], 2),
            sentiment_correct=(analysis.sentiment == actual_data['sentiment'])
        )

        db.session.add(verification)
        db.session.commit()

        return verification

    def _fetch_actual_data(self, date):
        """
        抓取實際大盤數據
        這裡可以從期交所或 Yahoo Finance 取得
        """
        try:
            import yfinance as yf
            # 使用台指期或加權指數
            ticker = yf.Ticker("^TWII")
            data = ticker.history(start=date, end=date + timedelta(days=1))

            if data.empty:
                return None

            close = data['Close'].iloc[-1]
            open_price = data['Open'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]

            # 判斷實際多空 (漲跌幅 > 0.5% 為偏多，< -0.5% 為偏空)
            if close > open_price * 1.005:
                sentiment = '偏多'
            elif close < open_price * 0.995:
                sentiment = '偏空'
            else:
                sentiment = '中立'

            return {
                'open': round(open_price, 2),
                'close': round(close, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'sentiment': sentiment
            }
        except Exception as e:
            print(f"⚠️ 抓取實際數據失敗: {e}")
            return None

    def get_accuracy(self, days=7):
        """
        計算命中率
        days: 天數 (7, 30, 90)
        """
        cutoff_date = datetime.now(self.tz).date() - timedelta(days=days)

        verifications = Verification.query.filter(
            Verification.date >= cutoff_date,
            Verification.actual_close.isnot(None)
        ).all()

        if not verifications:
            return 0

        total = len(verifications)
        correct = sum(1 for v in verifications if v.sentiment_correct)

        return round((correct / total) * 100, 1) if total > 0 else 0


def get_accuracy_report():
    """
    取得完整的命中率報告
    """
    verifier = Verifier()

    return {
        'week_accuracy': verifier.get_accuracy(7),
        'month_accuracy': verifier.get_accuracy(30),
        'quarter_accuracy': verifier.get_accuracy(90)
    }