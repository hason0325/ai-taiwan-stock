import os


class Config:
    SECRET_KEY = 'your-secret-key-change-this'

    # 使用絕對路徑
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'stock.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TIMEZONE = 'Asia/Taipei'
    SCHEDULE_TIME = '06:30'
    USD_TWD = 32.5

    # 評分權重 (總和 = 100)
    WEIGHTS = {
        'us_stock': 40,
        'adr': 30,
        'futures': 20,
        'others': 10
    }