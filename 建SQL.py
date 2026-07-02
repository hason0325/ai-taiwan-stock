from app import create_app, db
from app.models import AnalysisResult, Verification, DailyData

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ 資料庫建立完成！")
    print(f"📁 資料庫位置: instance/stock.db")

    # 檢查是否有資料
    count = AnalysisResult.query.count()
    print(f"📊 目前分析結果筆數: {count}")

    count_v = Verification.query.count()
    print(f"📊 目前驗證記錄筆數: {count_v}")