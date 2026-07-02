"""
台指期夜盤爬蟲 - 使用 Selenium 模擬瀏覽器
從臺灣期貨交易所行情資訊網抓取真實數據
"""
import time
import re
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class Config:
    TIMEZONE = 'Asia/Taipei'


def clean_number(text):
    """
    清理數字字串，去除逗號、%符號等，轉換為 float
    """
    if not text:
        return 0
    # 去除逗號、空格、%符號
    cleaned = text.replace(',', '').replace(' ', '').replace('%', '')
    try:
        return float(cleaned)
    except:
        return 0


def fetch_night_from_taifex_selenium():
    """
    使用 Selenium 模擬瀏覽器，從期交所網站抓取台指期夜盤數據
    """
    driver = None
    try:
        print("  📊 啟動瀏覽器，前往期交所網站...")

        # 設定 Chrome 選項
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        url = "https://mis.taifex.com.tw/futures/AfterHoursSession/EquityIndices/FuturesDomestic/"
        driver.get(url)
        print("  ✅ 頁面加載完成")

        # 點擊「免責聲明」的「接受」按鈕
        try:
            print("  🔍 尋找並點擊『接受』按鈕...")
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '接受')]"))
            )
            accept_button.click()
            print("  ✅ 已點擊『接受』按鈕")
            time.sleep(2)
        except Exception as e:
            print(f"  ⚠️ 沒有找到『接受』按鈕或已接受: {e}")

        print("  🔍 尋找台指期數據...")

        # 方法1: 直接找包含「臺指期076」的表格行
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            # 找到包含「臺指期076」的行 (使用更靈活的匹配)
            rows = driver.find_elements(By.XPATH, "//tr[contains(., '臺指期076') or contains(., '台指期076')]")

            if rows:
                row = rows[0]
                cells = row.find_elements(By.TAG_NAME, "td")

                if len(cells) >= 15:
                    # 提取數據 (根據表格結構)
                    # 0:商品, 1:狀態, 2:買進, 3:買量, 4:賣出, 5:賣量,
                    # 6:成交價, 7:漲跌, 8:漲跌幅%, 9:振幅%, 10:成交量,
                    # 11:開盤, 12:最高, 13:最低, 14:參考價, 15:時間

                    close_price = clean_number(cells[6].text)
                    change = clean_number(cells[7].text)
                    change_percent = clean_number(cells[8].text)
                    volume = int(clean_number(cells[10].text))
                    open_price = clean_number(cells[11].text)
                    high_price = clean_number(cells[12].text)
                    low_price = clean_number(cells[13].text)
                    prev_close = clean_number(cells[14].text)

                    if close_price > 0:
                        print(f"  ✅ 找到台指期夜盤數據: {close_price:.2f} ({change:+.2f}, {change_percent:+.2f}%)")

                        tz = pytz.timezone(Config.TIMEZONE)
                        now = datetime.now(tz)

                        return {
                            'close': round(close_price, 2),
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2),
                            'open': round(open_price, 2),
                            'high': round(high_price, 2),
                            'low': round(low_price, 2),
                            'volume': volume,
                            'prev_close': round(prev_close, 2),
                            'source': '臺灣期交所 (Selenium)',
                            'is_mock': False,
                            'is_night': True,
                            'updated_at': now.strftime('%Y-%m-%d %H:%M:%S')
                        }

        except Exception as e:
            print(f"  ⚠️ 方法1失敗: {e}")

        # 方法2: 從頁面中直接搜索數字
        try:
            print("  🔍 嘗試方法2: 在頁面中搜尋關鍵數字...")
            page_text = driver.page_source

            # 尋找 44,995 這樣的數字 (台指期價格範圍 40000~46000)
            price_pattern = r'(\d{2,3}(?:,\d{3})+\.?\d*)'
            numbers = re.findall(price_pattern, page_text)

            candidates = []
            for num in numbers:
                try:
                    val = float(num.replace(',', ''))
                    if 40000 < val < 46000:
                        candidates.append(val)
                except:
                    pass

            if candidates:
                # 取最後一個 (通常是最新的)
                close_price = candidates[-1]
                print(f"  ✅ 從頁面找到價格: {close_price:.2f}")

                # 嘗試同時提取漲跌
                change = 0
                change_pattern = r'([+-]?\d{1,3}(?:,\d{3})*\.?\d*)'
                changes = re.findall(change_pattern, page_text)
                for ch in changes:
                    try:
                        val = float(ch.replace(',', ''))
                        if 100 < abs(val) < 1000:  # 漲跌點數範圍
                            change = val
                            break
                    except:
                        pass

                tz = pytz.timezone(Config.TIMEZONE)
                now = datetime.now(tz)

                return {
                    'close': round(close_price, 2),
                    'change': round(change, 2),
                    'change_percent': round((change / (close_price - change)) * 100, 2) if change != 0 else 0,
                    'open': 0,
                    'high': 0,
                    'low': 0,
                    'volume': 0,
                    'prev_close': round(close_price - change, 2) if change != 0 else 0,
                    'source': '臺灣期交所 (Selenium-備援)',
                    'is_mock': False,
                    'is_night': True,
                    'updated_at': now.strftime('%Y-%m-%d %H:%M:%S')
                }
        except Exception as e:
            print(f"  ⚠️ 方法2失敗: {e}")

        print("  ❌ 無法找到台指期數據")
        return None

    except Exception as e:
        print(f"  ❌ Selenium 抓取失敗: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("  🔒 瀏覽器已關閉")


def get_mock_futures():
    """模擬夜盤數據 (當所有爬蟲都失敗時)"""
    import random
    tz = pytz.timezone(Config.TIMEZONE)
    now = datetime.now(tz)

    base_price = 22000 + random.randint(-200, 200)
    change = round(random.uniform(-150, 150), 2)
    change_percent = round((change / base_price) * 100, 2)

    print(f"  📊 生成模擬夜盤數據: {base_price:.2f} ({change:+.2f}%)")

    return {
        'close': float(base_price),
        'change': change,
        'change_percent': change_percent,
        'open': round(base_price - random.randint(10, 50), 2),
        'high': round(base_price + random.randint(10, 50), 2),
        'low': round(base_price - random.randint(10, 50), 2),
        'volume': random.randint(30000, 150000),
        'prev_close': round(base_price - change, 2),
        'source': '模擬數據',
        'updated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
        'is_mock': True,
        'is_night': True
    }


def fetch_futures():
    """主入口：抓取台指期夜盤數據"""
    print("📊 開始抓取台指期夜盤數據...")
    print("🔍 使用 Selenium 模擬瀏覽器 (最可靠)")

    result = fetch_night_from_taifex_selenium()
    if result:
        return result

    print("\n⚠️ 所有方式都失敗，使用模擬數據")
    return get_mock_futures()


def get_futures_info():
    """取得台指期完整資訊"""
    return fetch_futures()


# 測試用
if __name__ == '__main__':
    print("="*60)
    print("📊 台指期夜盤爬蟲測試 (Selenium 版本)")
    print("="*60)
    print()

    data = fetch_futures()

    if data:
        print("\n" + "="*60)
        print("📊 台指期夜盤數據：")
        print("="*60)
        print(f"  成交價: {data['close']:.2f}")
        print(f"  漲跌點: {data.get('change', 0):+.2f}")
        print(f"  漲跌幅: {data.get('change_percent', 0):+.2f}%")
        if data.get('open'):
            print(f"  開盤價: {data['open']:.2f}")
            print(f"  最高價: {data['high']:.2f}")
            print(f"  最低價: {data['low']:.2f}")
            print(f"  昨收價: {data.get('prev_close', 0):.2f}")
            print(f"  成交量: {data.get('volume', 0):,}")
        print(f"  來源: {data.get('source', '未知')}")
        print(f"  更新時間: {data.get('updated_at', '未知')}")
        if data.get('is_mock'):
            print("  ⚠️ 注意：這是模擬數據")
        else:
            print("  ✅ 這是真實數據")
    else:
        print("\n❌ 無法取得台指期數據")