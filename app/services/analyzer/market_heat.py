"""
市場熱度儀表板
綜合多項指標計算市場溫度
"""


class MarketHeat:
    def __init__(self, data):
        self.data = data
        self.heat_score = 50  # 基準分

    def calculate(self):
        """計算市場熱度 (0-100)"""
        adjustments = []

        # 1. VIX (權重 30%)
        vix = self.data.get('vix', {})
        if vix and vix.get('close'):
            if vix['close'] <= 15:
                adjustments.append(15)  # 樂觀
            elif vix['close'] <= 20:
                adjustments.append(5)  # 偏多
            elif vix['close'] <= 25:
                adjustments.append(-5)  # 偏空
            else:
                adjustments.append(-15)  # 恐慌

        # 2. 美元指數 (權重 20%)
        usd = self.data.get('usd_index', {})
        if usd and usd.get('close'):
            if usd['close'] <= 100:
                adjustments.append(10)
            elif usd['close'] <= 103:
                adjustments.append(0)
            else:
                adjustments.append(-10)

        # 3. 美股漲跌 (權重 30%)
        us_stock = self.data.get('us_stock', {})
        if us_stock:
            up_count = 0
            total = 0
            for name, values in us_stock.items():
                if name != 'updated_at' and isinstance(values, dict):
                    total += 1
                    if values.get('change_percent', 0) > 0:
                        up_count += 1
            if total > 0:
                ratio = up_count / total
                if ratio >= 0.75:
                    adjustments.append(10)
                elif ratio >= 0.5:
                    adjustments.append(5)
                elif ratio >= 0.25:
                    adjustments.append(-5)
                else:
                    adjustments.append(-10)

        # 4. 台指期夜盤 (權重 20%)
        futures = self.data.get('futures', {})
        if futures and futures.get('change_percent'):
            if futures['change_percent'] > 1:
                adjustments.append(10)
            elif futures['change_percent'] > 0:
                adjustments.append(5)
            elif futures['change_percent'] > -1:
                adjustments.append(-5)
            else:
                adjustments.append(-10)

        # 計算總分
        self.heat_score = max(0, min(100, 50 + sum(adjustments)))
        return self.get_status()

    def get_status(self):
        """取得熱度狀態"""
        if self.heat_score >= 70:
            return {
                'score': self.heat_score,
                'level': '🔥 過熱',
                'color': 'danger',
                'description': '市場情緒過熱，短線可能過度樂觀，留意追高風險'
            }
        elif self.heat_score >= 60:
            return {
                'score': self.heat_score,
                'level': '☀️ 偏多',
                'color': 'warning',
                'description': '市場情緒偏多，資金動能充足，順勢操作'
            }
        elif self.heat_score >= 40:
            return {
                'score': self.heat_score,
                'level': '🌤️ 中性',
                'color': 'info',
                'description': '市場方向不明，建議觀望或小量布局'
            }
        elif self.heat_score >= 30:
            return {
                'score': self.heat_score,
                'level': '🌧️ 偏空',
                'color': 'warning',
                'description': '市場情緒偏空，降低持股，保守操作'
            }
        else:
            return {
                'score': self.heat_score,
                'level': '❄️ 恐慌',
                'color': 'danger',
                'description': '市場極度恐慌，可能出現非理性殺盤，留意反彈機會'
            }