import sys
import os

# 加入專案根目錄
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.scheduler.daily_job import init_scheduler

app = create_app()

# PythonAnywhere 需要這個變數
application = app

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_scheduler()

    app.run(debug=True, host='0.0.0.0', port=5016)