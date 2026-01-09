import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "db" / "weather.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS areas (
            area_code TEXT PRIMARY KEY,
            area_name TEXT NOT NULL,
            area_name_en TEXT,
            area_type TEXT,
            parent_code TEXT,
            office_name TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            area_name TEXT,
            forecast_date TEXT NOT NULL,
            weather_code TEXT,
            weather TEXT,
            wind TEXT,
            wave TEXT,
            pop TEXT,
            temp_min TEXT,
            temp_max TEXT,
            reliability TEXT,
            fetched_at TEXT NOT NULL,
            FOREIGN KEY (area_code) REFERENCES areas (area_code)
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_forecasts_area_code 
        ON forecasts (area_code)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_forecasts_date 
        ON forecasts (forecast_date)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_forecasts_fetched 
        ON forecasts (fetched_at)
    ''')
    
    conn.commit()
    conn.close()


def save_area(area_code, area_name, area_name_en=None, area_type=None, 
              parent_code=None, office_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO areas 
        (area_code, area_name, area_name_en, area_type, parent_code, office_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (area_code, area_name, area_name_en, area_type, parent_code, office_name))
    
    conn.commit()
    conn.close()


def save_areas_from_json(area_data):
    conn = get_connection()
    cursor = conn.cursor()
    
    centers = area_data.get("centers", {})
    for code, info in centers.items():
        cursor.execute('''
            INSERT OR REPLACE INTO areas 
            (area_code, area_name, area_name_en, area_type, parent_code, office_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code, info.get("name"), info.get("enName"), "center", None, info.get("officeName")))
    
    offices = area_data.get("offices", {})
    for code, info in offices.items():
        cursor.execute('''
            INSERT OR REPLACE INTO areas 
            (area_code, area_name, area_name_en, area_type, parent_code, office_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code, info.get("name"), info.get("enName"), "office", info.get("parent"), info.get("officeName")))
    
    conn.commit()
    conn.close()


def get_all_areas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM areas ORDER BY area_code')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_areas_by_type(area_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM areas WHERE area_type = ? ORDER BY area_code', (area_type,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_offices_by_center(center_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM areas WHERE parent_code = ? ORDER BY area_code', (center_code,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_forecast(area_code, area_name, forecast_date, weather_code=None,
                  weather=None, wind=None, wave=None, pop=None,
                  temp_min=None, temp_max=None, reliability=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO forecasts 
        (area_code, area_name, forecast_date, weather_code, weather, 
         wind, wave, pop, temp_min, temp_max, reliability, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (area_code, area_name, forecast_date, weather_code, weather,
          wind, wave, pop, temp_min, temp_max, reliability, fetched_at))
    
    conn.commit()
    conn.close()


def save_forecasts_from_parsed_data(area_code, area_name, parsed_data):
    conn = get_connection()
    cursor = conn.cursor()
    
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for forecast_date, data in parsed_data.items():
        cursor.execute('''
            INSERT INTO forecasts 
            (area_code, area_name, forecast_date, weather_code, weather, 
             wind, wave, pop, temp_min, temp_max, reliability, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            area_code,
            area_name,
            forecast_date,
            data.get("weather_code"),
            data.get("weather"),
            data.get("wind"),
            data.get("wave"),
            data.get("pop"),
            data.get("temp_min"),
            data.get("temp_max"),
            data.get("reliability"),
            fetched_at
        ))
    
    conn.commit()
    conn.close()


def get_latest_forecasts(area_code):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT MAX(fetched_at) as latest FROM forecasts WHERE area_code = ?
    ''', (area_code,))
    result = cursor.fetchone()
    
    if not result or not result['latest']:
        conn.close()
        return []
    
    latest_fetched = result['latest']
    
    cursor.execute('''
        SELECT * FROM forecasts 
        WHERE area_code = ? AND fetched_at = ?
        ORDER BY forecast_date
    ''', (area_code, latest_fetched))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_forecasts_by_date(area_code, fetched_at):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM forecasts 
        WHERE area_code = ? AND fetched_at = ?
        ORDER BY forecast_date
    ''', (area_code, fetched_at))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_fetch_history(area_code):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT fetched_at FROM forecasts 
        WHERE area_code = ?
        ORDER BY fetched_at DESC
    ''', (area_code,))
    
    rows = cursor.fetchall()
    conn.close()
    return [row['fetched_at'] for row in rows]


def get_all_fetch_dates():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT fetched_at FROM forecasts ORDER BY fetched_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    return [row['fetched_at'] for row in rows]


if __name__ == "__main__":
    init_database()
    
    save_area("130000", "東京都", "Tokyo", "office", "010300", "気象庁")
    
    save_forecast(
        area_code="130000",
        area_name="東京都",
        forecast_date="2025-12-18",
        weather_code="101",
        weather="晴れ 朝晩 くもり",
        pop="10",
        temp_min="5",
        temp_max="13"
    )
    
    print("=== areas ===")
    for area in get_all_areas():
        print(area)
    
    print("\n=== forecasts ===")
    for f in get_latest_forecasts("130000"):
        print(f)
