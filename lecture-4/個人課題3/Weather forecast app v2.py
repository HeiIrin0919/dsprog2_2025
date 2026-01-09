import flet as ft
import requests
from datetime import datetime
from database import (
    init_database,
    save_areas_from_json,
    save_forecasts_from_parsed_data,
    get_latest_forecasts,
    get_fetch_history,
    get_forecasts_by_date,
)

AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"

WEATHER_CODE_ICONS = {
    "100": "☀️", "101": "🌤️", "102": "🌤️🌧️", "103": "🌤️🌧️", "104": "🌤️❄️",
    "110": "🌤️", "111": "🌤️", "112": "🌤️🌧️", "113": "🌤️🌧️", "114": "🌤️🌧️",
    "115": "🌤️❄️", "116": "🌤️❄️", "117": "🌤️❄️", "118": "🌤️🌧️", "119": "🌤️⛈️",
    "200": "☁️", "201": "☁️🌤️", "202": "☁️🌧️", "203": "☁️🌧️", "204": "☁️❄️",
    "205": "☁️❄️", "206": "☁️🌧️", "207": "☁️🌧️", "208": "☁️🌧️", "209": "🌫️",
    "210": "☁️🌤️", "211": "☁️🌤️", "212": "☁️🌧️", "213": "☁️🌧️", "214": "☁️🌧️",
    "215": "☁️❄️", "216": "☁️❄️", "217": "☁️❄️", "218": "☁️🌧️", "219": "☁️⛈️",
    "220": "☁️", "221": "☁️⛈️", "222": "☁️❄️⛈️", "223": "☁️🌤️", "224": "☁️⛈️",
    "225": "☁️❄️", "226": "☁️❄️", "228": "☁️🌧️❄️", "229": "☁️🌧️❄️", "230": "☁️❄️",
    "231": "☁️❄️⛈️", "240": "☁️", "250": "☁️", "260": "☁️❄️", "270": "☁️❄️",
    "281": "☁️🌧️❄️",
    "300": "🌧️", "301": "🌧️🌤️", "302": "🌧️☁️", "303": "🌧️❄️", "304": "🌧️",
    "306": "🌧️", "308": "🌧️⛈️", "309": "🌧️❄️", "311": "🌧️🌤️", "313": "🌧️☁️",
    "314": "🌧️❄️", "315": "🌧️❄️", "316": "🌧️☁️", "317": "🌧️☁️", "320": "🌧️",
    "321": "🌧️☁️", "322": "🌧️⛈️", "323": "🌧️🌤️", "324": "🌧️🌤️", "325": "🌧️☁️",
    "326": "🌧️❄️", "327": "🌧️❄️", "328": "🌧️❄️", "329": "🌧️❄️", "340": "🌧️❄️",
    "350": "🌧️", "361": "❄️🌧️", "371": "❄️🌧️",
    "400": "❄️", "401": "❄️🌤️", "402": "❄️☁️", "403": "❄️🌧️", "405": "❄️",
    "406": "❄️", "407": "❄️⛈️", "409": "❄️🌧️", "411": "❄️🌤️", "413": "❄️☁️",
    "414": "❄️🌧️", "420": "❄️", "421": "❄️☁️", "422": "❄️⛈️", "423": "❄️🌤️",
    "425": "❄️☁️", "426": "❄️🌧️", "427": "❄️🌧️", "450": "❄️",
}

COLORS = {
    "sidebar_bg": "#1E2330",
    "sidebar_hover": "#2D3548",
    "text_white": "#FFFFFF",
    "text_gray": "#94A3B8",
    "accent": "#6366F1",
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0",
    "temp_high": "#EF4444",
    "temp_low": "#3B82F6",
    "badge_a": "#22C55E",
    "badge_b": "#F59E0B",
    "badge_c": "#EF4444",
}

WEATHER_THEMES = {
    "sunny": {
        "gradient": ["#87CEEB", "#4A90D9", "#2E6AB3"],
        "text": "#FFFFFF",
        "sub_text": "#FFFFFFCC",
        "card_bg": "#FFFFFF30",
        "card_text": "#1E293B",
        "card_sub": "#475569",
    },
    "cloudy": {
        "gradient": ["#94A3B8", "#64748B", "#475569"],
        "text": "#FFFFFF",
        "sub_text": "#FFFFFFCC",
        "card_bg": "#FFFFFF25",
        "card_text": "#FFFFFF",
        "card_sub": "#FFFFFFAA",
    },
    "rainy": {
        "gradient": ["#64748B", "#475569", "#334155"],
        "text": "#FFFFFF",
        "sub_text": "#FFFFFFCC",
        "card_bg": "#FFFFFF20",
        "card_text": "#FFFFFF",
        "card_sub": "#FFFFFFAA",
    },
    "snowy": {
        "gradient": ["#E0E7FF", "#C7D2FE", "#A5B4FC"],
        "text": "#1E293B",
        "sub_text": "#475569",
        "card_bg": "#FFFFFF50",
        "card_text": "#1E293B",
        "card_sub": "#475569",
    },
}


def get_weather_icon(code):
    return WEATHER_CODE_ICONS.get(code, "🌈")


def get_weather_theme(code):
    if not code:
        return WEATHER_THEMES["sunny"]
    code_num = int(code) if code.isdigit() else 100
    if code_num < 200:
        return WEATHER_THEMES["sunny"]
    elif code_num < 300:
        return WEATHER_THEMES["cloudy"]
    elif code_num < 400:
        return WEATHER_THEMES["rainy"]
    else:
        return WEATHER_THEMES["snowy"]


def get_reliability_info(rel):
    if rel == "A":
        return ("A", COLORS["badge_a"], "信頼度：高い")
    elif rel == "B":
        return ("B", COLORS["badge_b"], "信頼度：普通")
    elif rel == "C":
        return ("C", COLORS["badge_c"], "信頼度：低い")
    return ("", "", "")


class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "天気予報アプリ v2"
        self.page.bgcolor = "#F1F5F9"
        self.page.window.width = 1200
        self.page.window.height = 850
        self.page.padding = 0
        
        self.area_data = {}
        self.current_area_code = None
        self.current_area_name = None
        
        init_database()
        
        self.history_dropdown = ft.Dropdown(
            label="過去の予報",
            width=200,
            visible=False,
            on_change=self.on_history_select,
            border_color=COLORS["accent"],
            text_size=12,
        )
        
        self.weather_container = ft.Container(
            content=self.build_welcome_screen(),
            expand=True,
        )
        
        self.area_list = ft.ListView(
            expand=True,
            spacing=2,
            padding=ft.padding.symmetric(horizontal=8, vertical=8),
        )
        
        self.build_ui()
        self.load_area_data()

    def build_welcome_screen(self):
        return ft.Container(
            content=ft.Column([
                ft.Container(height=100),
                ft.Text("🌤️", size=100),
                ft.Container(height=20),
                ft.Text(
                    "天気予報アプリ",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color="#1E293B",
                ),
                ft.Text(
                    "気象庁公式データ使用",
                    size=14,
                    color="#64748B",
                ),
                ft.Container(height=40),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ARROW_BACK, color=COLORS["accent"], size=20),
                        ft.Text("左側から地域を選択してください", size=14, color="#64748B"),
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                    padding=20,
                    border_radius=12,
                    border=ft.border.all(1, "#E2E8F0"),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#F8FAFC", "#F1F5F9"],
            ),
        )

    def build_ui(self):
        sidebar_header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("☁️", size=24),
                    width=40,
                    height=40,
                    bgcolor=COLORS["accent"],
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
                ft.Column([
                    ft.Text("天気予報", size=16, weight=ft.FontWeight.BOLD, color=COLORS["text_white"]),
                    ft.Text("v2", size=10, color=COLORS["text_gray"]),
                ], spacing=0),
            ], spacing=12),
            padding=ft.padding.all(16),
        )
        
        sidebar = ft.Container(
            content=ft.Column([
                sidebar_header,
                ft.Divider(height=1, color="#374151"),
                ft.Container(
                    content=ft.Text("地域選択", size=11, color=COLORS["text_gray"], weight=ft.FontWeight.W_500),
                    padding=ft.padding.only(left=16, top=12, bottom=8),
                ),
                ft.Container(content=self.area_list, expand=True),
            ], spacing=0),
            width=260,
            bgcolor=COLORS["sidebar_bg"],
        )
        
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    self.history_dropdown,
                ]),
            ], alignment=ft.MainAxisAlignment.END),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            bgcolor="#FFFFFF",
            border=ft.border.only(bottom=ft.BorderSide(1, "#E2E8F0")),
        )
        
        main_area = ft.Column([
            header,
            ft.Container(content=self.weather_container, expand=True),
        ], spacing=0, expand=True)
        
        self.page.add(
            ft.Row([sidebar, main_area], expand=True, spacing=0)
        )

    def load_area_data(self):
        try:
            response = requests.get(AREA_URL, timeout=10)
            self.area_data = response.json()
            save_areas_from_json(self.area_data)
            self.build_area_list()
        except Exception as e:
            self.area_list.controls = [
                ft.Text(f"エラー: {e}", color=COLORS["badge_c"], size=12)
            ]
            self.page.update()

    def build_area_list(self):
        centers = self.area_data.get("centers", {})
        offices = self.area_data.get("offices", {})
        self.area_list.controls = []
        
        for center_code, center_info in centers.items():
            center_name = center_info["name"]
            children_codes = center_info.get("children", [])
            
            child_tiles = []
            for child_code in children_codes:
                if child_code in offices:
                    office_name = offices[child_code]["name"]
                    tile = ft.Container(
                        content=ft.Text(office_name, size=12, color=COLORS["text_white"]),
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        border_radius=6,
                        on_click=lambda e, code=child_code, name=office_name: self.on_area_click(code, name),
                        on_hover=lambda e: self.on_tile_hover(e),
                    )
                    child_tiles.append(tile)
            
            if child_tiles:
                expansion = ft.ExpansionTile(
                    title=ft.Text(center_name, size=12, weight=ft.FontWeight.W_600, color=COLORS["text_white"]),
                    subtitle=ft.Text(f"{len(child_tiles)}地域", size=10, color=COLORS["text_gray"]),
                    controls=child_tiles,
                    initially_expanded=False,
                    tile_padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    collapsed_icon_color=COLORS["text_gray"],
                    icon_color=COLORS["text_white"],
                    bgcolor=COLORS["sidebar_hover"],
                    collapsed_bgcolor=COLORS["sidebar_bg"],
                )
                self.area_list.controls.append(expansion)
        
        self.page.update()

    def on_tile_hover(self, e):
        e.control.bgcolor = COLORS["sidebar_hover"] if e.data == "true" else None
        e.control.update()

    def on_area_click(self, area_code, area_name):
        self.current_area_code = area_code
        self.current_area_name = area_name
        
        try:
            self.weather_container.content = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=40, height=40, color=COLORS["accent"]),
                    ft.Container(height=16),
                    ft.Text("データを取得中...", size=14, color="#64748B"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
            )
            self.page.update()
            
            url = FORECAST_URL.format(area_code)
            response = requests.get(url, timeout=10)
            forecast_data = response.json()
            
            parsed_data = self.parse_forecast_data(forecast_data)
            save_forecasts_from_parsed_data(area_code, area_name, parsed_data)
            self.update_history_dropdown(area_code)
            self.display_weather_from_db(area_code, area_name)
            
        except Exception as e:
            self.weather_container.content = ft.Container(
                content=ft.Column([
                    ft.Text("😢", size=50),
                    ft.Text("データの取得に失敗しました", size=16, color="#1E293B", weight=ft.FontWeight.BOLD),
                    ft.Text(str(e), size=12, color=COLORS["badge_c"]),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
            )
            self.page.update()

    def update_history_dropdown(self, area_code):
        history = get_fetch_history(area_code)
        if len(history) > 1:
            self.history_dropdown.options = [ft.dropdown.Option(key=h, text=h) for h in history]
            self.history_dropdown.value = history[0]
            self.history_dropdown.visible = True
        else:
            self.history_dropdown.visible = False
        self.page.update()

    def on_history_select(self, e):
        if self.current_area_code and e.control.value:
            self.display_weather_from_db(self.current_area_code, self.current_area_name, fetched_at=e.control.value)

    def parse_forecast_data(self, forecast_data):
        result = {}
        
        if len(forecast_data) >= 1:
            three_day = forecast_data[0]
            time_series = three_day.get("timeSeries", [])
            
            if len(time_series) >= 1:
                weather_ts = time_series[0]
                time_defines = weather_ts.get("timeDefines", [])
                areas = weather_ts.get("areas", [])
                
                if areas:
                    area = areas[0]
                    weather_codes = area.get("weatherCodes", [])
                    weathers = area.get("weathers", [])
                    winds = area.get("winds", [])
                    waves = area.get("waves", [])
                    
                    for i, time_def in enumerate(time_defines):
                        date_str = time_def[:10]
                        if date_str not in result:
                            result[date_str] = {}
                        result[date_str]["weather_code"] = weather_codes[i] if i < len(weather_codes) else ""
                        result[date_str]["weather"] = weathers[i] if i < len(weathers) else ""
                        result[date_str]["wind"] = winds[i] if i < len(winds) else ""
                        result[date_str]["wave"] = waves[i] if i < len(waves) else ""
            
            if len(time_series) >= 2:
                pop_ts = time_series[1]
                pop_times = pop_ts.get("timeDefines", [])
                pop_areas = pop_ts.get("areas", [])
                
                if pop_areas:
                    pops = pop_areas[0].get("pops", [])
                    for i, time_def in enumerate(pop_times):
                        date_str = time_def[:10]
                        if date_str not in result:
                            result[date_str] = {}
                        if "pop" not in result[date_str] and i < len(pops) and pops[i]:
                            result[date_str]["pop"] = pops[i]
            
            if len(time_series) >= 3:
                temp_ts = time_series[2]
                temp_times = temp_ts.get("timeDefines", [])
                temp_areas = temp_ts.get("areas", [])
                
                if temp_areas and len(temp_times) >= 2:
                    temps = temp_areas[0].get("temps", [])
                    tomorrow_date = temp_times[0][:10]
                    if tomorrow_date not in result:
                        result[tomorrow_date] = {}
                    if len(temps) >= 1 and temps[0]:
                        result[tomorrow_date]["temp_min"] = temps[0]
                    if len(temps) >= 2 and temps[1]:
                        result[tomorrow_date]["temp_max"] = temps[1]
        
        if len(forecast_data) >= 2:
            weekly = forecast_data[1]
            weekly_ts = weekly.get("timeSeries", [])
            
            if len(weekly_ts) >= 1:
                weather_ts = weekly_ts[0]
                time_defines = weather_ts.get("timeDefines", [])
                areas = weather_ts.get("areas", [])
                
                if areas:
                    area = areas[0]
                    weather_codes = area.get("weatherCodes", [])
                    pops = area.get("pops", [])
                    reliabilities = area.get("reliabilities", [])
                    
                    for i, time_def in enumerate(time_defines):
                        date_str = time_def[:10]
                        if date_str not in result:
                            result[date_str] = {}
                        if "weather_code" not in result[date_str] and i < len(weather_codes):
                            result[date_str]["weather_code"] = weather_codes[i]
                        if "pop" not in result[date_str] and i < len(pops) and pops[i]:
                            result[date_str]["pop"] = pops[i]
                        if i < len(reliabilities) and reliabilities[i]:
                            result[date_str]["reliability"] = reliabilities[i]
            
            if len(weekly_ts) >= 2:
                temp_ts = weekly_ts[1]
                temp_times = temp_ts.get("timeDefines", [])
                temp_areas = temp_ts.get("areas", [])
                
                if temp_areas:
                    area = temp_areas[0]
                    temps_min = area.get("tempsMin", [])
                    temps_max = area.get("tempsMax", [])
                    
                    for i, time_def in enumerate(temp_times):
                        date_str = time_def[:10]
                        if date_str not in result:
                            result[date_str] = {}
                        if "temp_min" not in result[date_str] and i < len(temps_min) and temps_min[i]:
                            result[date_str]["temp_min"] = temps_min[i]
                        if "temp_max" not in result[date_str] and i < len(temps_max) and temps_max[i]:
                            result[date_str]["temp_max"] = temps_max[i]
        
        return result

    def display_weather_from_db(self, area_code, area_name, fetched_at=None):
        forecasts = get_forecasts_by_date(area_code, fetched_at) if fetched_at else get_latest_forecasts(area_code)
        
        if not forecasts:
            self.weather_container.content = ft.Text("データがありません", color="#64748B")
            self.page.update()
            return
        
        today_data = forecasts[0] if forecasts else {}
        today_code = today_data.get("weather_code", "100")
        theme = get_weather_theme(today_code)
        
        today_weather = today_data.get("weather", "")
        today_pop = today_data.get("pop", "--")
        today_temp_min = today_data.get("temp_min", "--")
        today_temp_max = today_data.get("temp_max", "--")
        today_wind = today_data.get("wind", "")
        today_date = today_data.get("forecast_date", "")[:10]
        
        hero_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(area_name, size=28, weight=ft.FontWeight.BOLD, color=theme["text"]),
                        ft.Text(f"{today_date}  今日の天気", size=13, color=theme["sub_text"]),
                    ], spacing=4),
                    ft.Text(get_weather_icon(today_code), size=80),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Text(today_weather, size=16, color=theme["text"], weight=ft.FontWeight.W_500),
                ft.Container(height=20),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("気温", size=11, color=theme["card_sub"]),
                            ft.Row([
                                ft.Text(f"{today_temp_min}°" if today_temp_min and today_temp_min != "--" else "--", size=24, color="#3B82F6", weight=ft.FontWeight.BOLD),
                                ft.Text("/", size=18, color=theme["card_sub"]),
                                ft.Text(f"{today_temp_max}°" if today_temp_max and today_temp_max != "--" else "--", size=24, color="#EF4444", weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                        ], spacing=4),
                        bgcolor=theme["card_bg"],
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        border_radius=12,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("降水確率", size=11, color=theme["card_sub"]),
                            ft.Text(f"{today_pop}%" if today_pop and today_pop != "--" else "--", size=24, color=theme["card_text"], weight=ft.FontWeight.BOLD),
                        ], spacing=4),
                        bgcolor=theme["card_bg"],
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        border_radius=12,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("風", size=11, color=theme["card_sub"]),
                            ft.Text(today_wind[:10] + "..." if len(today_wind) > 10 else today_wind or "--", size=13, color=theme["card_text"], weight=ft.FontWeight.W_500),
                        ], spacing=4),
                        bgcolor=theme["card_bg"],
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        border_radius=12,
                        expand=True,
                    ),
                ], spacing=12),
            ]),
            padding=30,
            border_radius=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=theme["gradient"],
            ),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=20, color="#00000015", offset=ft.Offset(0, 8)),
        )
        
        day_labels = ["今日", "明日", "明後日"]
        forecast_items = []
        for i, f in enumerate(forecasts[:3]):
            date_str = f.get("forecast_date", "")[5:]
            code = f.get("weather_code", "100")
            pop = f.get("pop", "--")
            t_min = f.get("temp_min", "--")
            t_max = f.get("temp_max", "--")
            
            item = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(day_labels[i] if i < 3 else date_str, size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                        width=60,
                    ),
                    ft.Text(date_str, size=11, color="#64748B", width=50),
                    ft.Text(get_weather_icon(code), size=28),
                    ft.Container(
                        content=ft.Text(f"{pop}%", size=13, color="#64748B"),
                        width=50,
                        alignment=ft.alignment.center,
                    ),
                    ft.Row([
                        ft.Text(f"{t_min}°" if t_min != "--" else "--", size=14, color=COLORS["temp_low"], weight=ft.FontWeight.BOLD),
                        ft.Text("/", size=12, color="#CBD5E1"),
                        ft.Text(f"{t_max}°" if t_max != "--" else "--", size=14, color=COLORS["temp_high"], weight=ft.FontWeight.BOLD),
                    ], spacing=4, width=80),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.symmetric(horizontal=16, vertical=14),
                border=ft.border.only(bottom=ft.BorderSide(1, "#F1F5F9")) if i < 2 else None,
            )
            forecast_items.append(item)
        
        three_day_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("3日間の予報", size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    padding=ft.padding.only(left=16, top=16, bottom=8),
                ),
                ft.Column(forecast_items, spacing=0),
            ]),
            bgcolor="#FFFFFF",
            border_radius=16,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000008", offset=ft.Offset(0, 4)),
        )
        
        weekly_items = []
        for f in forecasts[3:]:
            date_str = f.get("forecast_date", "")[5:]
            code = f.get("weather_code", "100")
            pop = f.get("pop", "")
            rel = f.get("reliability", "")
            t_min = f.get("temp_min", "")
            t_max = f.get("temp_max", "")
            
            if not pop and not t_min and not t_max:
                continue
            
            rel_badge, rel_color, rel_tip = get_reliability_info(rel)
            
            item = ft.Container(
                content=ft.Column([
                    ft.Text(date_str, size=12, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Text(get_weather_icon(code), size=26),
                    ft.Text(f"{pop}%" if pop else "--", size=11, color="#64748B"),
                    ft.Row([
                        ft.Text(t_min if t_min else "--", size=12, color=COLORS["temp_low"], weight=ft.FontWeight.BOLD),
                        ft.Text("/", size=10, color="#CBD5E1"),
                        ft.Text(t_max if t_max else "--", size=12, color=COLORS["temp_high"], weight=ft.FontWeight.BOLD),
                    ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(
                        content=ft.Text(rel_badge, size=9, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                        bgcolor=rel_color,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        border_radius=4,
                    ) if rel_badge else ft.Container(height=16),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                width=70,
                padding=ft.padding.symmetric(vertical=12),
            )
            weekly_items.append(item)
        
        weekly_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("週間予報", size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    padding=ft.padding.only(left=16, top=16, bottom=12),
                ),
                ft.Container(
                    content=ft.Row(weekly_items, alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    padding=ft.padding.only(bottom=16),
                ),
            ]),
            bgcolor="#FFFFFF",
            border_radius=16,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000008", offset=ft.Offset(0, 4)),
        ) if weekly_items else ft.Container()
        
        self.weather_container.content = ft.Container(
            content=ft.Column([
                hero_section,
                ft.Container(height=20),
                three_day_card,
                ft.Container(height=16),
                weekly_card,
            ], scroll=ft.ScrollMode.AUTO),
            padding=24,
            expand=True,
        )
        self.page.update()


def main(page: ft.Page):
    WeatherApp(page)


ft.app(main)
