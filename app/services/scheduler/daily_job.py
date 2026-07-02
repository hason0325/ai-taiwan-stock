from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import pytz
from datetime import datetime, timedelta
from config import Config
from app.services.crawler.us_stock import fetch_us_stock
from app.services.crawler.adr import fetch_tsm_adr
from app.services.crawler.futures import fetch_futures
from app.services.analyzer.scorer import MarketScorer
from app.services.analyzer.verifier import Verifier
from app import db
from app.models import DailyData, AnalysisResult, Verification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def daily_analysis():
    """每日分析任務 - 在台灣時間早上 6:30 執行"""

    tz = pytz.timezone(Config.TIMEZONE)
    now = datetime.now(tz)
    today = now.date()

    logger.info(f"📊 開始執行每日分析 - 台灣時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. 抓取所有數據
        logger.info("  🔍 抓取美股數據...")
        us_stock = fetch_us_stock()

        logger.info("  🔍 抓取台積電ADR...")
        adr = fetch_tsm_adr()

        logger.info("  🔍 抓取台指期夜盤...")
        futures = fetch_futures()

        # 2. 儲存原始數據到資料庫
        if us_stock:
            daily_data = DailyData(
                date=today,
                dow_jones=us_stock.get('dow_jones', {}).get('close'),
                sp500=us_stock.get('sp500', {}).get('close'),
                nasdaq=us_stock.get('nasdaq', {}).get('close'),
                philadelphia=us_stock.get('philadelphia', {}).get('close'),
                tsm_adr=adr.get('close') if adr else None,
                tsm_adr_change=adr.get('change_percent') if adr else None,
                futures_close=futures.get('close') if futures else None,
                futures_change=futures.get('change_percent') if futures else None
            )
            db.session.add(daily_data)
            logger.info("  ✅ 原始數據已儲存")

        # 3. 執行 AI 評分
        logger.info("  🧠 執行 AI 評分...")
        scorer = MarketScorer()
        analysis_data = {
            'us_stock': us_stock,
            'tsm_adr': adr,
            'futures': futures
        }
        result = scorer.calculate_score(analysis_data)

        # 4. 儲存分析結果
        analysis_result = AnalysisResult(
            date=today,
            total_score=result['total_score'],
            sentiment=result['sentiment'],
            stars=result['stars'],
            up_probability=result['up_probability'],
            down_probability=result['down_probability'],
            predict_open=result['predict_open'],
            predict_high=result['predict_high'],
            predict_low=result['predict_low'],
            predict_close=result['predict_close'],
            confidence=result['confidence'],
            suggestion=result['suggestion'],
            risk_warning=result['risk_warning'],
            score_breakdown=result['breakdown']
        )
        db.session.add(analysis_result)
        db.session.commit()
        logger.info(f"  ✅ AI 評分完成 - 總分: {result['total_score']}分, 多空: {result['sentiment']}")

        # 5. 🆕 自動驗證昨天的預測 (如果有昨天的數據)
        yesterday = today - timedelta(days=1)
        verifier = Verifier()

        # 檢查昨天的分析結果是否存在
        yesterday_analysis = AnalysisResult.query.filter_by(date=yesterday).first()
        if yesterday_analysis:
            # 檢查是否已經驗證過
            existing = Verification.query.filter_by(date=yesterday).first()
            if not existing:
                logger.info(f"  🔍 驗證昨日 ({yesterday}) 預測...")
                verification = verifier.verify_daily(yesterday)
                if verification:
                    logger.info(f"  ✅ 昨日驗證完成 - {'正確' if verification.sentiment_correct else '錯誤'}")
                else:
                    logger.info(f"  ⚠️ 昨日驗證失敗 (可能無實際數據)")

        # 6. 🆕 定期清理舊數據 (保留最近 90 天)
        cutoff_date = today - timedelta(days=90)
        old_data = AnalysisResult.query.filter(AnalysisResult.date < cutoff_date).delete()
        old_verifications = Verification.query.filter(Verification.date < cutoff_date).delete()
        db.session.commit()
        if old_data or old_verifications:
            logger.info(f"  🧹 清理 {cutoff_date} 之前的舊數據")

        logger.info("✅ 每日分析完成")

    except Exception as e:
        logger.error(f"❌ 分析失敗: {e}")
        db.session.rollback()


def init_scheduler():
    """初始化排程器"""
    scheduler = BackgroundScheduler(timezone=Config.TIMEZONE)

    scheduler.add_job(
        func=daily_analysis,
        trigger=CronTrigger(hour=6, minute=30, timezone=Config.TIMEZONE),
        id='daily_analysis',
        replace_existing=True
    )

    scheduler.start()

    tz = pytz.timezone(Config.TIMEZONE)
    now = datetime.now(tz)
    logger.info(f"🚀 排程器已啟動 (台灣時區) - 當前時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("⏰ 每日 6:30 執行分析任務")