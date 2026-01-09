import flet as ft
import requests
from datetime import datetime

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
    "bg": "#E8F4F8",
    "sidebar_bg": "#FFFFFF",
    "card_today": "#FFB74D",
    "card_tomorrow": "#81D4FA",
    "card_dayafter": "#CE93D8",
    "card_weekly": "#FFFFFF",
    "text_dark": "#37474F",
    "text_light": "#78909C",
    "temp_high": "#EF5350",
    "temp_low": "#42A5F5",
    "rain": "#5C6BC0",
    "accent": "#26A69A",
    "border": "#B0BEC5",
    "border_light": "#CFD8DC",
    "badge_a": "#66BB6A",
    "badge_b": "#FFCA28",
    "badge_c": "#EF5350",
}


def get_weather_icon(code):
    return WEATHER_CODE_ICONS.get(code, "🌈")


def get_reliability_info(rel):
    if rel == "A":
        return ("A", COLORS["badge_a"], "信頼度:高")
    elif rel == "B":
        return ("B", COLORS["badge_b"], "信頼度:中")
    elif rel == "C":
        return ("C", COLORS["badge_c"], "信頼度:低")
    return ("", "", "")


class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "🌈 お天気アプリ"
        self.page.bgcolor = COLORS["bg"]
        self.page.window.width = 1150
        self.page.window.height = 800
        
        self.area_data = {}
        
        self.weather_container = ft.Container(
            content=self.build_welcome_screen(),
            expand=True,
            padding=25,
        )
        
        self.area_list = ft.ListView(
            expand=True,
            spacing=4,
            padding=15,
        )
        
        self.build_ui()
        self.load_area_data()

    def rounded_card(self, content, bgcolor, width=None, height=None, padding=20, border_color=None):
        return ft.Container(
            content=content,
            bgcolor=bgcolor,
            width=width,
            height=height,
            padding=padding,
            border_radius=25,
            border=ft.border.all(2, border_color or COLORS["border_light"]),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#00000012",
                offset=ft.Offset(0, 4),
            ),
        )

    def build_welcome_screen(self):
        return ft.Column(
            controls=[
                ft.Container(height=40),
                ft.Text("🌤️", size=100),
                ft.Container(height=15),
                ft.Text(
                    "お天気アプリ",
                    size=38,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["text_dark"],
                ),
                ft.Container(height=10),
                ft.Text(
                    "Weather Forecast",
                    size=16,
                    color=COLORS["text_light"],
                    italic=True,
                ),
                ft.Container(height=40),
                self.rounded_card(
                    ft.Column([
                        ft.Text("👈", size=30),
                        ft.Container(height=5),
                        ft.Text("左のメニューから", size=16, color=COLORS["text_dark"]),
                        ft.Text("地域を選んでね！", size=18, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    bgcolor="#FFFFFF",
                    width=250,
                    padding=25,
                    border_color=COLORS["accent"],
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

    def build_ui(self):
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row([
                        ft.Container(
                            content=ft.Text("🌈", size=30),
                            padding=5,
                        ),
                        ft.Text(
                            "お天気アプリ",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["text_dark"],
                        ),
                    ], spacing=10),
                    ft.Container(
                        content=ft.Row([
                            ft.Text("⚡", size=14),
                            ft.Text("気象庁データ", size=13, weight=ft.FontWeight.W_500),
                        ], spacing=5),
                        bgcolor=COLORS["accent"],
                        padding=ft.padding.symmetric(horizontal=15, vertical=8),
                        border_radius=20,
                        border=ft.border.all(2, "#1E8E82"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=25, vertical=18),
            bgcolor="#FFFFFF",
            border=ft.border.only(bottom=ft.BorderSide(2, COLORS["border_light"])),
        )
        
        sidebar = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("📍", size=18),
                        ft.Text("地域を選択", size=15, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                    ], spacing=10),
                    padding=ft.padding.only(left=15, top=15, bottom=10),
                ),
                ft.Container(
                    content=self.area_list,
                    expand=True,
                ),
            ]),
            width=320,
            bgcolor=COLORS["sidebar_bg"],
            border=ft.border.only(right=ft.BorderSide(2, COLORS["border_light"])),
        )
        
        main_content = ft.Container(
            content=self.weather_container,
            expand=True,
            bgcolor=COLORS["bg"],
        )
        
        body = ft.Row(
            controls=[sidebar, main_content],
            expand=True,
            spacing=0,
        )
        
        self.page.add(
            ft.Column(
                controls=[header, body],
                expand=True,
                spacing=0,
            )
        )

    def load_area_data(self):
        try:
            response = requests.get(AREA_URL, timeout=10)
            self.area_data = response.json()
            self.build_area_list()
        except Exception as e:
            self.area_list.controls = [
                ft.Text(f"エラー: {e}", color=COLORS["badge_c"])
            ]
            self.page.update()

    def build_area_list(self):
        centers = self.area_data.get("centers", {})
        offices = self.area_data.get("offices", {})
        
        self.area_list.controls = []
        
        region_icons = {
            "北海道": "🏔️", "東北": "🌾", "関東": "🗼", "東海": "🏯",
            "北陸": "🌊", "近畿": "⛩️", "中国": "🍁", "四国": "🍊",
            "九州": "🌋", "沖縄": "🏝️",
        }
        
        def get_region_icon(name):
            for key, icon in region_icons.items():
                if key in name:
                    return icon
            return "📍"
        
        for center_code, center_info in centers.items():
            center_name = center_info["name"]
            children_codes = center_info.get("children", [])
            
            child_tiles = []
            for child_code in children_codes:
                if child_code in offices:
                    office = offices[child_code]
                    office_name = office["name"]
                    
                    tile = ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.LOCATION_CITY, size=18, color=COLORS["accent"]),
                                width=38,
                                height=38,
                                bgcolor=COLORS["bg"],
                                border_radius=10,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column([
                                ft.Text(office_name, size=13, weight=ft.FontWeight.W_500, color=COLORS["text_dark"]),
                                ft.Text(child_code, size=10, color=COLORS["text_light"]),
                            ], spacing=2, expand=True),
                        ], spacing=12),
                        padding=ft.padding.symmetric(horizontal=12, vertical=10),
                        border_radius=12,
                        ink=True,
                        on_click=lambda e, code=child_code, name=office_name: self.on_area_click(code, name),
                        on_hover=lambda e: self.on_tile_hover(e),
                    )
                    child_tiles.append(tile)
            
            if child_tiles:
                expansion = ft.ExpansionTile(
                    leading=ft.Container(
                        content=ft.Text(get_region_icon(center_name), size=22),
                        width=45,
                        height=45,
                        bgcolor=COLORS["bg"],
                        border_radius=12,
                        alignment=ft.alignment.center,
                    ),
                    title=ft.Text(center_name, size=14, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                    subtitle=ft.Text(f"{len(child_tiles)}地域", size=11, color=COLORS["text_light"]),
                    controls=child_tiles,
                    initially_expanded=False,
                    controls_padding=ft.padding.only(left=10, right=10, bottom=10),
                    tile_padding=ft.padding.symmetric(horizontal=12, vertical=8),
                )
                self.area_list.controls.append(expansion)
        
        self.page.update()

    def on_tile_hover(self, e):
        if e.data == "true":
            e.control.bgcolor = "#E3F2FD"
        else:
            e.control.bgcolor = None
        e.control.update()

    def on_area_click(self, area_code, area_name):
        try:
            self.weather_container.content = ft.Column([
                ft.Container(height=50),
                ft.ProgressRing(width=50, height=50, color=COLORS["accent"]),
                ft.Container(height=20),
                ft.Text("天気データを取得中...", size=14, color=COLORS["text_light"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            
            url = FORECAST_URL.format(area_code)
            response = requests.get(url, timeout=10)
            forecast_data = response.json()
            
            self.display_weather(area_name, forecast_data)
            
        except Exception as e:
            self.weather_container.content = ft.Column([
                ft.Text("😢", size=60),
                ft.Container(height=15),
                ft.Text("データの取得に失敗しました", size=18, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                ft.Container(height=8),
                ft.Text(str(e), size=12, color=COLORS["badge_c"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()

    def parse_forecast_data(self, forecast_data):
        """
        APIデータを解析し、日付ごとの天気情報を整理する
        
        返り値:
        {
            "2025-12-18": {
                "weather_code": "101",
                "weather": "晴れ 朝晩 くもり",
                "wind": "...",
                "wave": "...",
                "pop": "10",
                "temp_min": "5",
                "temp_max": "13",
            },
            ...
        }
        """
        result = {}
        
        # 第一部分: 3日間予報
        if len(forecast_data) >= 1:
            three_day = forecast_data[0]
            time_series = three_day.get("timeSeries", [])
            
            # timeSeries[0]: 天気、風、波（3日分）
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
            
            # timeSeries[1]: 降水確率（6時間ごと、今日〜明日）
            if len(time_series) >= 2:
                pop_ts = time_series[1]
                pop_times = pop_ts.get("timeDefines", [])
                pop_areas = pop_ts.get("areas", [])
                
                if pop_areas:
                    pops = pop_areas[0].get("pops", [])
                    # 日付ごとの最初の降水確率を取得
                    for i, time_def in enumerate(pop_times):
                        date_str = time_def[:10]
                        if date_str not in result:
                            result[date_str] = {}
                        # まだpopが設定されていなければ設定
                        if "pop" not in result[date_str] and i < len(pops) and pops[i]:
                            result[date_str]["pop"] = pops[i]
            
            # timeSeries[2]: 気温（明日の最低・最高のみ）
            # temps[0] = 明日の最低気温 (00:00)
            # temps[1] = 明日の最高気温 (09:00)
            if len(time_series) >= 3:
                temp_ts = time_series[2]
                temp_times = temp_ts.get("timeDefines", [])
                temp_areas = temp_ts.get("areas", [])
                
                if temp_areas and len(temp_times) >= 2:
                    temps = temp_areas[0].get("temps", [])
                    # 明日の日付を取得（temp_times[0]が明日の00:00）
                    tomorrow_date = temp_times[0][:10]
                    
                    if tomorrow_date not in result:
                        result[tomorrow_date] = {}
                    
                    if len(temps) >= 1 and temps[0]:
                        result[tomorrow_date]["temp_min"] = temps[0]
                    if len(temps) >= 2 and temps[1]:
                        result[tomorrow_date]["temp_max"] = temps[1]
        
        # 第二部分: 週間予報（明後日以降のデータを補完）
        if len(forecast_data) >= 2:
            weekly = forecast_data[1]
            weekly_ts = weekly.get("timeSeries", [])
            
            # timeSeries[0]: 天気、降水確率、信頼度
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
                        
                        # 週間予報の天気コード（3日間予報にない場合のみ使用）
                        if "weather_code" not in result[date_str] and i < len(weather_codes):
                            result[date_str]["weather_code"] = weather_codes[i]
                        
                        # 降水確率（3日間予報にない場合）
                        if "pop" not in result[date_str] and i < len(pops) and pops[i]:
                            result[date_str]["pop"] = pops[i]
                        
                        # 信頼度
                        if i < len(reliabilities) and reliabilities[i]:
                            result[date_str]["reliability"] = reliabilities[i]
            
            # timeSeries[1]: 気温（週間）
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
                        
                        # 気温（まだ設定されていなければ）
                        if "temp_min" not in result[date_str] and i < len(temps_min) and temps_min[i]:
                            result[date_str]["temp_min"] = temps_min[i]
                        if "temp_max" not in result[date_str] and i < len(temps_max) and temps_max[i]:
                            result[date_str]["temp_max"] = temps_max[i]
        
        return result

    def display_weather(self, area_name, forecast_data):
        content = []
        
        content.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("📍", size=28),
                        width=50,
                        height=50,
                        bgcolor=COLORS["card_today"],
                        border_radius=15,
                        border=ft.border.all(2, "#E69A28"),
                        alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        ft.Text(area_name, size=26, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                        ft.Text(
                            forecast_data[0].get("publishingOffice", ""),
                            size=12,
                            color=COLORS["text_light"],
                        ),
                    ], spacing=3),
                ], spacing=15),
                margin=ft.margin.only(bottom=25),
            )
        )
        
        try:
            # データを解析
            parsed_data = self.parse_forecast_data(forecast_data)
            
            # 日付順にソート
            sorted_dates = sorted(parsed_data.keys())
            
            if sorted_dates:
                # 3日間の天気
                content.append(
                    ft.Row([
                        ft.Text("☀️", size=22),
                        ft.Text("3日間の天気", size=18, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                    ], spacing=10)
                )
                content.append(ft.Container(height=15))
                
                day_configs = [
                    ("TODAY", COLORS["card_today"], "#E69A28"),
                    ("明日", COLORS["card_tomorrow"], "#5BB8D8"),
                    ("明後日", COLORS["card_dayafter"], "#B070B8"),
                ]
                
                # 3日間予報のtimeDefinesから日付を取得
                time_series = forecast_data[0].get("timeSeries", [])
                three_day_dates = []
                if time_series:
                    time_defines = time_series[0].get("timeDefines", [])
                    three_day_dates = [t[:10] for t in time_defines[:3]]
                
                forecast_cards = []
                for i, date_str in enumerate(three_day_dates):
                    day_data = parsed_data.get(date_str, {})
                    
                    weather_code = day_data.get("weather_code", "100")
                    weather_text = day_data.get("weather", "")
                    wind_text = day_data.get("wind", "")
                    wave_text = day_data.get("wave", "")
                    pop = day_data.get("pop")
                    temp_min = day_data.get("temp_min")
                    temp_max = day_data.get("temp_max")
                    
                    icon = get_weather_icon(weather_code)
                    label, bg_color, border_color = day_configs[i] if i < len(day_configs) else (date_str[5:], "#FFFFFF", COLORS["border"])
                    
                    extra_info = []
                    if wind_text:
                        short_wind = wind_text[:18] + "..." if len(wind_text) > 18 else wind_text
                        extra_info.append(
                            ft.Row([
                                ft.Text("🌬️", size=11),
                                ft.Text(short_wind, size=10, color="#FFFFFFCC"),
                            ], spacing=5)
                        )
                    if wave_text:
                        extra_info.append(
                            ft.Row([
                                ft.Text("🌊", size=11),
                                ft.Text(wave_text, size=10, color="#FFFFFFCC"),
                            ], spacing=5)
                        )
                    
                    card_content = ft.Column([
                        ft.Container(
                            content=ft.Text(label, size=13, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                            bgcolor="#00000030",
                            padding=ft.padding.symmetric(horizontal=15, vertical=6),
                            border_radius=20,
                        ),
                        ft.Text(date_str[5:], size=11, color="#FFFFFF99"),
                        ft.Container(height=8),
                        ft.Text(icon, size=55),
                        ft.Container(height=5),
                        ft.Container(
                            content=ft.Text(
                                weather_text[:14] + "..." if len(weather_text) > 14 else weather_text,
                                size=11,
                                color="#FFFFFF",
                                text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.W_500,
                            ),
                            width=130,
                            height=38,
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Text("☔", size=14),
                                ft.Text(
                                    f"{pop}%" if pop else "--",
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                            bgcolor="#00000020",
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            border_radius=12,
                        ),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Text(
                                f"{temp_min}°" if temp_min else "--°",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#E3F2FD",
                            ),
                            ft.Text("/", size=16, color="#FFFFFF80"),
                            ft.Text(
                                f"{temp_max}°" if temp_max else "--°",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#FFEBEE",
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                        ft.Container(height=8),
                        ft.Column(extra_info, spacing=3) if extra_info else ft.Container(),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3)
                    
                    card = ft.Container(
                        content=card_content,
                        bgcolor=bg_color,
                        width=175,
                        padding=18,
                        border_radius=25,
                        border=ft.border.all(3, border_color),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=12,
                            color="#00000015",
                            offset=ft.Offset(0, 5),
                        ),
                    )
                    forecast_cards.append(card)
                
                content.append(ft.Row(forecast_cards, spacing=18, wrap=True))
            
            # 週間予報
            if len(forecast_data) > 1:
                weekly = forecast_data[1]
                weekly_series = weekly.get("timeSeries", [])
                
                if weekly_series:
                    content.append(ft.Container(height=30))
                    content.append(
                        ft.Row([
                            ft.Text("📅", size=22),
                            ft.Text("週間予報", size=18, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                        ], spacing=10)
                    )
                    content.append(ft.Container(height=15))
                    
                    weekly_weather = weekly_series[0] if weekly_series else {}
                    weekly_times = weekly_weather.get("timeDefines", [])
                    
                    weekly_cards = []
                    for i, time_def in enumerate(weekly_times[:7]):
                        date_str = time_def[:10]
                        day_data = parsed_data.get(date_str, {})
                        
                        code = day_data.get("weather_code", "100")
                        pop = day_data.get("pop", "")
                        rel = day_data.get("reliability", "")
                        t_min = day_data.get("temp_min", "")
                        t_max = day_data.get("temp_max", "")
                        
                        # 最初の日（今日/明日）はスキップする場合がある
                        if not pop and not t_min and not t_max:
                            continue
                        
                        icon = get_weather_icon(code)
                        rel_badge, rel_color, rel_tip = get_reliability_info(rel)
                        
                        card_content = ft.Column([
                            ft.Text(date_str[5:], size=12, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                            ft.Container(height=5),
                            ft.Text(icon, size=32),
                            ft.Container(height=5),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text("☔", size=11),
                                    ft.Text(f"{pop}%", size=12, weight=ft.FontWeight.BOLD, color=COLORS["rain"]),
                                ], spacing=3, alignment=ft.MainAxisAlignment.CENTER),
                                bgcolor=COLORS["bg"],
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10,
                            ) if pop else ft.Container(height=25),
                            ft.Container(height=5),
                            ft.Row([
                                ft.Text(t_min if t_min else "--", size=13, weight=ft.FontWeight.BOLD, color=COLORS["temp_low"]),
                                ft.Text("/", size=12, color=COLORS["text_light"]),
                                ft.Text(t_max if t_max else "--", size=13, weight=ft.FontWeight.BOLD, color=COLORS["temp_high"]),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=3),
                            ft.Container(height=5),
                            ft.Container(
                                content=ft.Text(rel_badge, size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                bgcolor=rel_color,
                                padding=ft.padding.symmetric(horizontal=10, vertical=3),
                                border_radius=8,
                                tooltip=rel_tip,
                            ) if rel_badge else ft.Container(height=20),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
                        
                        card = ft.Container(
                            content=card_content,
                            bgcolor="#FFFFFF",
                            width=95,
                            padding=12,
                            border_radius=18,
                            border=ft.border.all(1.5, COLORS["border_light"]),
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=6,
                                color="#00000008",
                                offset=ft.Offset(0, 2),
                            ),
                        )
                        weekly_cards.append(card)
                    
                    content.append(ft.Row(weekly_cards, spacing=12, wrap=True))
                    
                    # 平年値
                    temp_avg = forecast_data[1].get("tempAverage", {})
                    precip_avg = forecast_data[1].get("precipAverage", {})
                    
                    if temp_avg.get("areas") or precip_avg.get("areas"):
                        content.append(ft.Container(height=25))
                        content.append(
                            ft.Row([
                                ft.Text("📊", size=18),
                                ft.Text("平年値", size=16, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                            ], spacing=10)
                        )
                        content.append(ft.Container(height=12))
                        
                        avg_cards = []
                        if temp_avg.get("areas"):
                            for area in temp_avg["areas"][:2]:
                                avg_cards.append(
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Text("🌡️", size=16),
                                            ft.Column([
                                                ft.Text(area["area"]["name"], size=12, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                                                ft.Row([
                                                    ft.Text(f"{area['min']}°", size=11, color=COLORS["temp_low"]),
                                                    ft.Text("〜", size=11, color=COLORS["text_light"]),
                                                    ft.Text(f"{area['max']}°", size=11, color=COLORS["temp_high"]),
                                                ], spacing=3),
                                            ], spacing=2),
                                        ], spacing=10),
                                        bgcolor="#FFFFFF",
                                        padding=12,
                                        border_radius=15,
                                        border=ft.border.all(1.5, COLORS["border_light"]),
                                    )
                                )
                        
                        if precip_avg.get("areas"):
                            for area in precip_avg["areas"][:2]:
                                avg_cards.append(
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Text("💧", size=16),
                                            ft.Column([
                                                ft.Text(area["area"]["name"], size=12, weight=ft.FontWeight.BOLD, color=COLORS["text_dark"]),
                                                ft.Text(f"{area['min']}〜{area['max']}mm", size=11, color=COLORS["text_light"]),
                                            ], spacing=2),
                                        ], spacing=10),
                                        bgcolor="#FFFFFF",
                                        padding=12,
                                        border_radius=15,
                                        border=ft.border.all(1.5, COLORS["border_light"]),
                                    )
                                )
                        
                        content.append(ft.Row(avg_cards, spacing=12, wrap=True))
        
        except Exception as e:
            content.append(
                ft.Text(f"表示エラー: {e}", color=COLORS["badge_c"], size=12)
            )
        
        self.weather_container.content = ft.Column(
            controls=content,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.page.update()


def main(page: ft.Page):
    WeatherApp(page)


ft.app(main)
