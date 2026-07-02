from flask import Blueprint, render_template, jsonify
from app.models import AnalysisResult, Verification
from app.services.crawler.us_stock import fetch_us_stock
from app.services.crawler.adr import fetch_tsm_adr
from app.services.crawler.futures import fetch_futures
from app.services.crawler.vix_usd import fetch_vix, fetch_usd_index
from app.services.crawler.commodity import fetch_oil, fetch_gold
from app.services.analyzer.scorer import MarketScorer
from app.services.analyzer.verifier import get_accuracy_report
from app.services.analyzer.market_heat import MarketHeat
from app.services.analyzer.technical import get_technical_summary
from app.services.analyzer.intraday import get_intraday_status
from datetime import datetime, timedelta
import pytz
from config import Config

bp = Blueprint('web', __name__)


@bp.route('/')
def index():
    """首頁 - 顯示AI分析報告與即時數據"""

    tz = pytz.timezone(Config.TIMEZONE)
    taiwan_now = datetime.now(tz)
    today = taiwan_now.date()

    # 抓取即時數據
    us_stock_data = fetch_us_stock()
    tsm_adr_data = fetch_tsm_adr()
    futures_data = fetch_futures()
    vix_data = fetch_vix()
    usd_index_data = fetch_usd_index()
    oil_data = fetch_oil()
    gold_data = fetch_gold()

    # 執行 AI 評分
    scorer = MarketScorer()
    analysis_data = {
        'us_stock': us_stock_data,
        'tsm_adr': tsm_adr_data,
        'futures': futures_data,
        'vix': vix_data,
        'usd_index': usd_index_data,
        'oil': oil_data,
        'gold': gold_data
    }
    score_result = scorer.calculate_score(analysis_data)

    # 計算市場熱度
    heat = MarketHeat(analysis_data)
    market_heat = heat.calculate()

    # 取得技術面分析
    technical = get_technical_summary()

    # 取得盤中監控
    intraday = get_intraday_status()

    # 從資料庫取得最新的分析結果
    latest_result = AnalysisResult.query.order_by(AnalysisResult.date.desc()).first()

    if latest_result and latest_result.date == today:
        report = latest_result
    else:
        class LiveReport:
            pass

        report = LiveReport()
        report.date = today.strftime('%Y-%m-%d')
        report.stars = score_result['stars']
        report.sentiment = score_result['sentiment']
        report.up_probability = score_result['up_probability']
        report.down_probability = score_result['down_probability']
        report.predict_open = score_result['predict_open']
        report.predict_close = score_result['predict_close']
        report.predict_high = score_result['predict_high']
        report.predict_low = score_result['predict_low']
        report.predict_index_open = score_result.get('predict_index_open', 0)
        report.confidence = score_result['confidence']
        report.suggestion = score_result['suggestion']
        report.risk_warning = score_result['risk_warning']
        report.score_breakdown = score_result['breakdown']
        report.total_score = score_result['total_score']

    verification = get_accuracy_report()

    return render_template('index.html',
                           report=report,
                           verification=verification,
                           us_stock=us_stock_data,
                           tsm_adr=tsm_adr_data,
                           futures=futures_data,
                           vix=vix_data,
                           usd_index=usd_index_data,
                           oil=oil_data,
                           gold=gold_data,
                           market_heat=market_heat,
                           technical=technical,
                           intraday=intraday,
                           server_time=taiwan_now.strftime('%Y-%m-%d %H:%M:%S'))


@bp.route('/report')
def full_report():
    """完整分析報告頁"""

    tz = pytz.timezone(Config.TIMEZONE)
    taiwan_now = datetime.now(tz)

    us_stock_data = fetch_us_stock()
    tsm_adr_data = fetch_tsm_adr()
    futures_data = fetch_futures()
    vix_data = fetch_vix()
    usd_index_data = fetch_usd_index()
    oil_data = fetch_oil()
    gold_data = fetch_gold()

    scorer = MarketScorer()
    analysis_data = {
        'us_stock': us_stock_data,
        'tsm_adr': tsm_adr_data,
        'futures': futures_data,
        'vix': vix_data,
        'usd_index': usd_index_data,
        'oil': oil_data,
        'gold': gold_data
    }
    score_result = scorer.calculate_score(analysis_data)

    # 計算市場熱度
    heat = MarketHeat(analysis_data)
    market_heat = heat.calculate()

    class LiveReport:
        pass

    report = LiveReport()
    report.date = taiwan_now.strftime('%Y-%m-%d')
    report.stars = score_result['stars']
    report.sentiment = score_result['sentiment']
    report.up_probability = score_result['up_probability']
    report.down_probability = score_result['down_probability']
    report.predict_open = score_result['predict_open']
    report.predict_close = score_result['predict_close']
    report.predict_high = score_result['predict_high']
    report.predict_low = score_result['predict_low']
    report.confidence = score_result['confidence']
    report.suggestion = score_result['suggestion']
    report.risk_warning = score_result['risk_warning']
    report.score_breakdown = score_result['breakdown']
    report.total_score = score_result['total_score']

    verification = get_accuracy_report()

    return render_template('report.html',
                           report=report,
                           verification=verification,
                           us_stock=us_stock_data,
                           tsm_adr=tsm_adr_data,
                           futures=futures_data,
                           vix=vix_data,
                           usd_index=usd_index_data,
                           oil=oil_data,
                           gold=gold_data,
                           market_heat=market_heat,
                           server_time=taiwan_now.strftime('%Y-%m-%d %H:%M:%S'))


@bp.route('/history')
def history():
    """歷史績效頁"""
    tz = pytz.timezone(Config.TIMEZONE)
    taiwan_now = datetime.now(tz)

    cutoff_date = taiwan_now.date() - timedelta(days=30)
    history_records = Verification.query.filter(
        Verification.date >= cutoff_date
    ).order_by(Verification.date.desc()).all()

    total = len(history_records)
    correct = sum(1 for r in history_records if r.sentiment_correct)

    summary = {
        'total_predictions': total,
        'correct_predictions': correct,
        'overall_accuracy': round((correct / total) * 100, 1) if total > 0 else 0
    }

    verification = get_accuracy_report()

    return render_template('history.html',
                           verification=verification,
                           history_data=history_records,
                           summary=summary,
                           server_time=taiwan_now.strftime('%Y-%m-%d %H:%M:%S'))


@bp.route('/about')
def about():
    """關於頁面"""
    tz = pytz.timezone(Config.TIMEZONE)
    taiwan_now = datetime.now(tz)
    return render_template('about.html', server_time=taiwan_now.strftime('%Y-%m-%d %H:%M:%S'))


@bp.route('/api/intraday')
def api_intraday():
    """盤中監控 API"""
    status = get_intraday_status()
    return jsonify(status)


@bp.route('/api/technical')
def api_technical():
    """技術面分析 API"""
    technical = get_technical_summary()
    return jsonify(technical)


@bp.route('/api/heat')
def api_heat():
    """市場熱度 API"""
    us_stock_data = fetch_us_stock()
    tsm_adr_data = fetch_tsm_adr()
    futures_data = fetch_futures()
    vix_data = fetch_vix()
    usd_index_data = fetch_usd_index()

    analysis_data = {
        'us_stock': us_stock_data,
        'tsm_adr': tsm_adr_data,
        'futures': futures_data,
        'vix': vix_data,
        'usd_index': usd_index_data
    }
    heat = MarketHeat(analysis_data)
    market_heat = heat.calculate()
    return jsonify(market_heat)