"""
AI 評分系統
根據各項真實數據計算多空分數，生成預測報告
"""
import json
import math
from datetime import datetime
import pytz
from config import Config


class MarketScorer:
    """
    市場評分器
    根據各項數據計算多空分數，生成預測
    """

    # 權重配置（總和 = 100）
    WEIGHTS = {
        'us_stock': 40,        # 美股四大指數
        'adr': 30,             # 台積電ADR
        'futures': 20,         # 台指期夜盤
        'others': 10,          # 其他綜合因素 (VIX、美元、法人等)
    }

    def __init__(self, weights=None):
        self.weights = weights or self.WEIGHTS

    def calculate_score(self, data):
        """
        計算各項分數與總分

        Args:
            data: 包含所有市場數據的字典

        Returns:
            包含評分結果的字典
        """
        scores = {}
        total = 0

        # 1. 美股評分 (40分)
        us_score = self._score_us_stock(data.get('us_stock', {}))
        scores['us_stock'] = us_score
        total += us_score * (self.weights['us_stock'] / 100)

        # 2. ADR評分 (30分)
        adr_score = self._score_adr(data.get('tsm_adr', {}))
        scores['adr'] = adr_score
        total += adr_score * (self.weights['adr'] / 100)

        # 3. 台指期評分 (20分)
        futures_score = self._score_futures(data.get('futures', {}))
        scores['futures'] = futures_score
        total += futures_score * (self.weights['futures'] / 100)

        # 4. 其他綜合評分 (10分)
        others_score = self._score_others(data)
        scores['others'] = others_score
        total += others_score * (self.weights['others'] / 100)

        # 四捨五入
        total = round(total, 1)

        # 生成預測結果
        result = self._generate_prediction(total, scores, data)
        result['breakdown'] = scores

        return result

    def _score_us_stock(self, data):
        """
        美股評分 (權重 40%)
        四大指數漲跌加權平均
        - 費半 (SOX) 權重稍高，因為與台股關聯性最強
        """
        if not data:
            return 50

        # 四大指數權重
        indices = {
            'nasdaq': 0.25,        # 那斯達克 25%
            'sp500': 0.20,         # S&P500 20%
            'dow_jones': 0.20,     # 道瓊 20%
            'philadelphia': 0.35   # 費半 35% (與台股關聯最強)
        }

        changes = []
        weights = []

        for idx, weight in indices.items():
            if idx in data and data[idx] and isinstance(data[idx], dict) and 'change_percent' in data[idx]:
                changes.append(data[idx]['change_percent'])
                weights.append(weight)

        if not changes:
            return 50

        # 加權平均
        avg_change = sum(c * w for c, w in zip(changes, weights)) / sum(weights)

        # 漲1%加8分，跌1%減8分
        score = 50 + avg_change * 8
        return max(0, min(100, score))

    def _score_adr(self, data):
        """
        ADR評分 (權重 30%)
        台積電ADR漲跌幅
        """
        if not data or not isinstance(data, dict) or 'change_percent' not in data:
            return 50

        change = data['change_percent']
        # ADR漲1%加10分，跌1%減10分
        score = 50 + change * 10
        return max(0, min(100, score))

    def _score_futures(self, data):
        """
        台指期評分 (權重 20%)
        夜盤漲跌幅
        """
        if not data or not isinstance(data, dict) or 'change_percent' not in data:
            return 50

        change = data['change_percent']
        # 漲1%加8分，跌1%減8分
        score = 50 + change * 8
        return max(0, min(100, score))

    def _score_others(self, data):
        """
        其他綜合評分 (權重 10%)
        匯率、重大消息、外資、國際事件
        """
        score = 50
        adjustments = []

        # 1. VIX 恐慌指數
        vix = data.get('vix', {})
        if vix and isinstance(vix, dict) and 'close' in vix:
            vix_value = vix.get('close', 0)
            if vix_value > 0:
                if vix_value <= 15:
                    adjustments.append(8)
                elif vix_value <= 20:
                    adjustments.append(3)
                elif vix_value <= 25:
                    adjustments.append(-3)
                else:
                    adjustments.append(-8)

        # 2. 美元指數
        usd = data.get('usd_index', {})
        if usd and isinstance(usd, dict) and 'close' in usd:
            usd_value = usd.get('close', 0)
            if usd_value > 0:
                if usd_value <= 100:
                    adjustments.append(5)
                elif usd_value <= 103:
                    adjustments.append(0)
                else:
                    adjustments.append(-5)

        # 3. 三大法人 (如果有)
        institution = data.get('institution', {})
        if institution and isinstance(institution, dict) and 'foreign_invest' in institution:
            foreign = institution.get('foreign_invest', 0)
            if foreign > 50:
                adjustments.append(5)
            elif foreign < -50:
                adjustments.append(-5)

        # 綜合調整
        if adjustments:
            avg_adjustment = sum(adjustments) / len(adjustments)
            score = score + avg_adjustment

        return max(0, min(100, score))

    def _generate_prediction(self, total, scores, data):
        """根據總分生成預測結果"""

        # 多空判斷
        if total >= 65:
            sentiment = '偏多'
            stars = '★★★★☆'
        elif total >= 55:
            sentiment = '中性偏多'
            stars = '★★★☆☆'
        elif total >= 45:
            sentiment = '中立'
            stars = '★★★☆☆'
        elif total >= 35:
            sentiment = '中性偏空'
            stars = '★★☆☆☆'
        else:
            sentiment = '偏空'
            stars = '★☆☆☆☆'

        # 漲跌機率
        up_prob = 50 + (total - 50) * 0.7
        up_prob = max(20, min(90, up_prob))
        down_prob = 100 - up_prob

        # 預估點數（以台指期為基準）
        futures_data = data.get('futures', {})
        base_price = futures_data.get('close', 22000) if futures_data else 22000
        futures_change = futures_data.get('change', 0) if futures_data else 0

        # 根據分數計算漲跌幅度
        change_ratio = (total - 50) / 100 * 0.015
        predict_open = base_price * (1 + change_ratio * 0.5)
        predict_close = base_price * (1 + change_ratio * 1.2)
        predict_high = predict_open * (1 + abs(change_ratio) * 0.3)
        predict_low = predict_open * (1 - abs(change_ratio) * 0.2)

        # 🆕 加權指數開盤預估
        yesterday_close = 22000  # 可從資料庫取得昨日收盤
        adr_data = data.get('tsm_adr', {})
        adr_change = adr_data.get('change_points', 0) if adr_data else 0
        adr_impact = adr_change * 2.5  # ADR 1點約影響大盤 2.5 點
        predict_index_open = yesterday_close + (futures_change * 0.8) + (adr_impact * 0.5)

        # 信心指數
        if scores:
            values = list(scores.values())
            variance = sum((v - 50) ** 2 for v in values) / len(values)
            confidence = min(95, 60 + variance * 0.3)
        else:
            confidence = 70

        # 操作建議
        suggestion = self._generate_suggestion(sentiment, total)

        # 風險提醒
        risk_warning = self._generate_risk_warning(data)

        return {
            'total_score': round(total, 1),
            'sentiment': sentiment,
            'stars': stars,
            'up_probability': round(up_prob, 1),
            'down_probability': round(down_prob, 1),
            'predict_open': round(predict_open),
            'predict_high': round(predict_high),
            'predict_low': round(predict_low),
            'predict_close': round(predict_close),
            'predict_index_open': round(predict_index_open),  # 🆕
            'futures_change': round(futures_change, 2),       # 🆕
            'adr_impact': round(adr_impact, 2),               # 🆕
            'confidence': round(confidence, 1),
            'suggestion': suggestion,
            'risk_warning': risk_warning
        }

    def _generate_suggestion(self, sentiment, score):
        """生成操作建議"""
        suggestions = {
            '偏多': '📈 大盤趨勢偏多，可考慮增加持股水位，留意開盤可能跳空開高，避免追高殺低。建議關注科技股與半導體類股。',
            '中性偏多': '📊 市場偏多但力道有限，建議維持中性偏多操作，逢回可適量布局優質標的。',
            '中立': '⏸️ 市場方向不明，建議觀望為主，等待更明確的趨勢訊號再進場。',
            '中性偏空': '📉 市場偏空，建議降低持股比例，保守操作，優先保護本金。',
            '偏空': '⚠️ 市場明顯偏空，建議大幅降低持股，增加現金部位，避開高風險資產。'
        }
        return suggestions.get(sentiment, '市場方向不明，建議觀望。')

    def _generate_risk_warning(self, data):
        """生成風險提醒"""
        warnings = []

        # ADR 風險
        adr = data.get('tsm_adr', {})
        if adr and isinstance(adr, dict) and adr.get('change_percent', 0) < -3:
            warnings.append('⚠️ 台積電ADR跌幅超過3%，留意台股開盤壓力')

        # 美股風險
        us = data.get('us_stock', {})
        if us and isinstance(us, dict):
            for name, values in us.items():
                if name != 'updated_at' and isinstance(values, dict):
                    if values.get('change_percent', 0) < -3:
                        warnings.append(f'⚠️ {name} 跌幅超過3%，市場情緒偏空')

        # 台指期風險
        futures = data.get('futures', {})
        if futures and isinstance(futures, dict) and futures.get('change_percent', 0) < -3:
            warnings.append('⚠️ 台指期夜盤跌幅超過3%，留意開盤壓力')

        # VIX 風險
        vix = data.get('vix', {})
        if vix and isinstance(vix, dict) and vix.get('close', 0) > 25:
            warnings.append('⚠️ VIX恐慌指數偏高，市場波動加劇')

        return '；'.join(warnings) if warnings else '✅ 目前無重大風險訊號'


# 測試用
if __name__ == '__main__':
    test_data = {
        'us_stock': {
            'dow_jones': {'change_percent': 0.85},
            'sp500': {'change_percent': 0.62},
            'nasdaq': {'change_percent': 1.12},
            'philadelphia': {'change_percent': 1.85}
        },
        'tsm_adr': {'change_percent': 1.25, 'change_points': 2.5},
        'futures': {'close': 22000, 'change_percent': 0.8, 'change': 176}
    }

    scorer = MarketScorer()
    result = scorer.calculate_score(test_data)

    print("="*50)
    print("📊 AI 評分結果")
    print("="*50)
    print(f"  美股 (40%): {result['breakdown']['us_stock']:.1f} 分")
    print(f"  ADR (30%): {result['breakdown']['adr']:.1f} 分")
    print(f"  台指期 (20%): {result['breakdown']['futures']:.1f} 分")
    print(f"  其他 (10%): {result['breakdown']['others']:.1f} 分")
    print("-"*50)
    print(f"  總分: {result['total_score']} 分")
    print(f"  多空: {result['sentiment']} {result['stars']}")
    print(f"  上漲機率: {result['up_probability']}%")
    print(f"  信心指數: {result['confidence']}%")
    print(f"  預估開盤: +{result['predict_open']}")
    print(f"  預估收盤: +{result['predict_close']}")
    print(f"  加權指數開盤預估: {result['predict_index_open']}")