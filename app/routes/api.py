from flask import Blueprint, jsonify
from app.models import AnalysisResult
from app.services.crawler.us_stock import fetch_us_stock
from app.services.crawler.adr import fetch_tsm_adr
from app.services.crawler.futures import fetch_futures, get_futures_info  # 🆕 新增
from datetime import datetime
import pytz
from config import Config

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/health')
def health():
    tz = pytz.timezone(Config.TIMEZONE)
    return jsonify({
        'status': 'ok',
        'time': datetime.now(tz).isoformat(),
        'timezone': Config.TIMEZONE
    })

@bp.route('/us_stock')
def get_us_stock():
    """取得即時美股數據"""
    data = fetch_us_stock()
    tz = pytz.timezone(Config.TIMEZONE)
    if data:
        return jsonify({
            'status': 'success',
            'data': data,
            'updated_at': datetime.now(tz).isoformat(),
            'timezone': Config.TIMEZONE
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '無法抓取美股數據'
        }), 500

@bp.route('/tsm_adr')
def get_tsm_adr():
    """取得台積電ADR數據"""
    data = fetch_tsm_adr()
    tz = pytz.timezone(Config.TIMEZONE)
    if data:
        return jsonify({
            'status': 'success',
            'data': data,
            'updated_at': datetime.now(tz).isoformat(),
            'timezone': Config.TIMEZONE
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '無法抓取台積電ADR數據'
        }), 500

# 🆕 新增：台指期夜盤
@bp.route('/futures')
def get_futures():
    """取得台指期夜盤數據"""
    data = fetch_futures()
    if data:
        return jsonify({
            'status': 'success',
            'data': data
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '無法抓取台指期數據'
        }), 500

@bp.route('/futures/detail')
def get_futures_detail():
    """取得台指期完整資訊（開高低收）"""
    data = get_futures_info()
    if data:
        return jsonify({
            'status': 'success',
            'data': data
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '無法抓取台指期詳細數據'
        }), 500

@bp.route('/latest')
def latest():
    """取得最新分析結果"""
    result = AnalysisResult.query.order_by(AnalysisResult.date.desc()).first()
    if not result:
        return jsonify({'error': 'No data'}), 404
    return jsonify({
        'date': result.date.isoformat(),
        'score': result.total_score,
        'sentiment': result.sentiment,
        'up_probability': result.up_probability
    })