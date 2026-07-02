from app import db
from datetime import datetime


class DailyData(db.Model):
    """每日原始資料"""
    __tablename__ = 'daily_data'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)

    # 美股四大指數
    dow_jones = db.Column(db.Float)
    sp500 = db.Column(db.Float)
    nasdaq = db.Column(db.Float)
    philadelphia = db.Column(db.Float)

    # 台積電ADR
    tsm_adr = db.Column(db.Float)
    tsm_adr_change = db.Column(db.Float)

    # 台指期夜盤
    futures_close = db.Column(db.Float)
    futures_change = db.Column(db.Float)

    # 其他指標
    vix = db.Column(db.Float)
    usd_index = db.Column(db.Float)
    usd_twd = db.Column(db.Float)
    oil_price = db.Column(db.Float)
    gold_price = db.Column(db.Float)
    foreign_invest = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class AnalysisResult(db.Model):
    """分析結果"""
    __tablename__ = 'analysis_results'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)

    total_score = db.Column(db.Float)
    sentiment = db.Column(db.String(10))
    stars = db.Column(db.String(10))

    up_probability = db.Column(db.Float)
    down_probability = db.Column(db.Float)

    predict_open = db.Column(db.Float)
    predict_high = db.Column(db.Float)
    predict_low = db.Column(db.Float)
    predict_close = db.Column(db.Float)

    confidence = db.Column(db.Float)
    suggestion = db.Column(db.Text)
    risk_warning = db.Column(db.Text)

    score_breakdown = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.now)


class Verification(db.Model):
    """歷史驗證"""
    __tablename__ = 'verifications'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)

    # 預測值
    predicted_open = db.Column(db.Float)
    predicted_close = db.Column(db.Float)
    predicted_high = db.Column(db.Float)
    predicted_low = db.Column(db.Float)
    predicted_sentiment = db.Column(db.String(10))

    # 實際值
    actual_open = db.Column(db.Float)
    actual_close = db.Column(db.Float)
    actual_high = db.Column(db.Float)
    actual_low = db.Column(db.Float)
    actual_sentiment = db.Column(db.String(10))

    # 誤差
    open_error = db.Column(db.Float)
    close_error = db.Column(db.Float)
    high_error = db.Column(db.Float)
    low_error = db.Column(db.Float)
    sentiment_correct = db.Column(db.Boolean)

    verified_at = db.Column(db.DateTime, default=datetime.now)