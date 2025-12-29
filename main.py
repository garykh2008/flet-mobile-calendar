import flet as ft
import calendar
import datetime
import copy

# 設定星期幾的標題
WEEK_DAYS = ["一", "二", "三", "四", "五", "六", "日"]

# -----------------------------------------------------------------------------
# 資料層 (Repository) - 負責所有資料的增刪改查
# -----------------------------------------------------------------------------
class EventRepository:
    def __init__(self, page: ft.Page):
        self.page = page
        self.storage_key = "events"
        self._cache = self._load_from_storage()

    def _load_from_storage(self):
        """從 client_storage 讀取資料，並進行簡單的格式驗證"""
        data = self.page.client_storage.get(self.storage_key) or {}
        
        # 簡單驗證：檢查是否有舊格式資料
        if data:
            first_key = next(iter(data))
            if data[first_key] and "start_time" not in data[first_key][0]:
                print("EventRepository: 偵測到舊資料格式，重置資料庫...")
                self.page.client_storage.clear()
                return {}
        return data

    def _save_to_storage(self):
        """將快取寫入 client_storage"""
        self.page.client_storage.set(self.storage_key, self._cache)

    def get_events(self, date_str: str) -> list:
        """取得特定日期的行程列表 (回傳複本以免被意外修改)"""
        return copy.deepcopy(self._cache.get(date_str, []))

    def add_event(self, date_str: str, event_data: dict):
        """新增行程"""
        if date_str not in self._cache:
            self._cache[date_str] = []
        self._cache[date_str].append(event_data)
        self._save_to_storage()

    def update_event(self, date_str: str, index: int, event_data: dict):
        """更新行程"""
        if date_str in self._cache and 0 <= index < len(self._cache[date_str]):
            self._cache[date_str][index] = event_data
            self._save_to_storage()

    def delete_event(self, date_str: str, index: int):
        """刪除行程"""
        if date_str in self._cache and 0 <= index < len(self._cache[date_str]):
            del self._cache[date_str][index]
            # 如果該日期沒資料了，可以選擇清空 key，這裡選擇保留空 list
            self._save_to_storage()

# -----------------------------------------------------------------------------
# UI 層 - 負責顯示與互動
# -----------------------------------------------------------------------------
def main(page: ft.Page):
    # 1. 基礎設定
    page.title = "Flet 行事曆"
    
    # 讀取並設定主題 (預設為淺色)
    saved_theme = page.client_storage.get("theme_mode")
    page.theme_mode = ft.ThemeMode.DARK if saved_theme == "dark" else ft.ThemeMode.LIGHT
    
    # 依據主題設定背景色
    page.bgcolor = ft.colors.BLACK if page.theme_mode == ft.ThemeMode.DARK else ft.colors.WHITE

    # 初始化 Repository
    repo = EventRepository(page)

    # 2. 應用程式狀態 (UI State)
    today = datetime.date.today()
    state = {
        "current_year": today.year,
        "current_month": today.month,
        "selected_date": today.strftime("%Y-%m-%d"),
        # UI 暫存狀態
        "temp_time_type": None, 
        "temp_start_time": datetime.time(9, 0),
        "temp_end_time": datetime.time(10, 0),
        "editing_index": -1 
    }

    # 3. UI 元件宣告
    calendar_grid = ft.Column(spacing=2)
    current_month_text = ft.Text(size=20, weight=ft.FontWeight.BOLD)
    selected_date_text = ft.Text(size=16, color=ft.colors.GREY_700)
    event_list_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    # 4. 時間選擇器 UI 邏輯
    def on_time_picked(e):
        picked_time = time_picker.value
        if not picked_time:
            return
        
        # 更新 UI 顯示與 State
        target_btn = btn_start_time if state["temp_time_type"] == "start" else btn_end_time
        target_key = "temp_start_time" if state["temp_time_type"] == "start" else "temp_end_time"
        
        state[target_key] = picked_time
        target_btn.text = picked_time.strftime("%H:%M")
        target_btn.update()

    time_picker = ft.TimePicker(
        confirm_text="確定", cancel_text="取消", help_text="選擇時間", on_change=on_time_picked
    )
    page.overlay.append(time_picker)

    def open_time_picker(time_type):
        state["temp_time_type"] = time_type
        time_picker.value = state["temp_start_time"] if time_type == "start" else state["temp_end_time"]
        time_picker.open = True
        page.update()

    btn_start_time = ft.OutlinedButton("09:00", on_click=lambda _: open_time_picker("start"))
    btn_end_time = ft.OutlinedButton("10:00", on_click=lambda _: open_time_picker("end"))

    # 5. Dialog UI 元件 (拉到外面共用)
    tf_title = ft.TextField(label="行程標題", autofocus=True)
    sw_all_day = ft.Switch(label="全天行程", value=False)
    dd_reminder = ft.Dropdown(
        label="提醒通知",
        options=[
            ft.dropdown.Option("none", "無"),
            ft.dropdown.Option("10m", "10 分鐘前"),
            ft.dropdown.Option("1h", "1 小時前"),
            ft.dropdown.Option("1d", "1 天前"),
        ],
        value="none"
    )
    tf_desc = ft.TextField(label="備註", multiline=True, min_lines=2, max_lines=4)
    row_time_picker = ft.Row(
        [ft.Text("時間:"), btn_start_time, ft.Text("-"), btn_end_time],
        alignment=ft.MainAxisAlignment.START, visible=True
    )

    # 定義可選顏色 (名稱: 色碼)
    COLOR_OPTIONS = {
        "blue": ft.colors.BLUE,
        "red": ft.colors.RED,
        "green": ft.colors.GREEN,
        "orange": ft.colors.ORANGE,
        "purple": ft.colors.PURPLE,
        "grey": ft.colors.GREY
    }
    # 記錄目前選中的顏色 (預設藍色)
    state["temp_color"] = "blue"

    # 建立顏色選擇器 UI
    color_picker_row = ft.Row(spacing=10)

    def render_color_picker():
        color_picker_row.controls.clear()
        for color_name, color_code in COLOR_OPTIONS.items():
            is_selected = state["temp_color"] == color_name
            
            def on_color_click(e, c=color_name):
                state["temp_color"] = c
                render_color_picker() # 重繪選擇器以更新邊框
                page.update()

            color_picker_row.controls.append(
                ft.Container(
                    width=30, height=30, border_radius=15,
                    bgcolor=color_code,
                    border=ft.border.all(2, ft.colors.BLACK) if is_selected else None,
                    on_click=on_color_click,
                    data=color_name
                )
            )

    def on_all_day_change(e):
        row_time_picker.visible = not sw_all_day.value
        page.update()
    sw_all_day.on_change = on_all_day_change

    # 6. 核心邏輯函數 (使用 Repository)
    def render_events():
        date_str = state["selected_date"]
        # 從 Repository 獲取資料，而不是直接存取 client_storage
        events = repo.get_events(date_str)
        
        y, m, d = map(int, date_str.split('-'))
        selected_date_text.value = f"{y}年{m}月{d}日 的行程"
        event_list_view.controls.clear()
        
        def handle_delete(e):
            idx = e.control.data
            repo.delete_event(date_str, idx) # 使用 Repository 刪除
            render_events() # 重繪
            render_calendar() # 更新日曆小紅點
        
        def handle_long_press(e):
            idx = e.control.data
            show_actions_sheet(idx)

        if not events:
            event_list_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.EVENT_NOTE, size=50, color=ft.colors.GREY_300),
                        ft.Text("今天沒有安排行程", color=ft.colors.GREY_400)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center, padding=40
                )
            )
        else:
            for i, event in enumerate(events):
                # UI 建構邏輯 (保持不變)
                # 取得顏色設定，預設為藍色
                event_color_name = event.get("color", "blue")
                event_color = COLOR_OPTIONS.get(event_color_name, ft.colors.BLUE)

                if event.get("is_all_day", False):
                    time_display = ft.Container(
                        content=ft.Text("全天", size=12, color=ft.colors.WHITE),
                        bgcolor=event_color, # 全天標籤跟隨顏色
                        padding=ft.padding.symmetric(horizontal=8, vertical=2), border_radius=4
                    )
                else:
                    start = event.get("start_time", "??:??")
                    end = event.get("end_time", "??:??")
                    time_display = ft.Text(f"{start} - {end}", size=12, color=ft.colors.GREY_600)

                rem_val = event.get("reminder", "none")
                reminder_text = ""
                if rem_val != "none":
                     map_rem = {"10m": "10分前", "1h": "1小時前", "1d": "1天前"}
                     reminder_text = f"🔔 {map_rem.get(rem_val, '')}"

                card_content = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(event["title"], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                time_display
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.Text(event.get("description", ""), size=14, color=ft.colors.GREY_700, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                ft.Text(reminder_text, size=12, color=ft.colors.ORANGE_600)
                            ])
                        ]),
                        padding=ft.padding.only(left=15, top=12, bottom=12, right=15),
                        # 使用 Border 來實現左側色條，避免 Row Stretch 高度計算問題
                        border=ft.border.only(left=ft.BorderSide(10, event_color)),
                        border_radius=ft.border_radius.only(top_left=10, bottom_left=10) # 讓左上左下有圓角
                    )
                )

                event_list_view.controls.append(
                    ft.Dismissible(
                        key=f"{date_str}_{i}_{event['title']}", 
                        on_dismiss=handle_delete, data=i,
                        background=ft.Container(bgcolor=ft.colors.RED, content=ft.Icon(ft.icons.DELETE, color="white")),
                        content=ft.GestureDetector(
                            on_long_press_start=handle_long_press, content=card_content, data=i
                        )
                    )
                )
        page.update()

    def render_calendar():
        year = state["current_year"]
        month = state["current_month"]
        current_month_text.value = f"{year}年 {month}月"
        cal = calendar.monthcalendar(year, month)
        calendar_grid.controls.clear()
        
        calendar_grid.controls.append(
            ft.Row(
                controls=[
                    ft.Container(content=ft.Text(day, color=ft.colors.GREY_600, size=12), alignment=ft.alignment.center, expand=1) 
                    for day in WEEK_DAYS
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        for week in cal:
            week_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            for day in week:
                if day == 0:
                    week_row.controls.append(ft.Container(expand=1))
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    is_selected = date_str == state["selected_date"]
                    is_today = date_str == today.strftime("%Y-%m-%d")
                    # 使用 Repository 檢查是否有行程
                    events_on_day = repo.get_events(date_str)
                    has_events = len(events_on_day) > 0
                    
                    # 判斷是否為深色模式
                    is_dark = page.theme_mode == ft.ThemeMode.DARK
                    
                    # 定義顏色邏輯
                    if is_selected:
                        # 選中狀態：淺色用藍，深色用靛青色
                        bg_color = ft.colors.INDIGO if is_dark else ft.colors.BLUE
                        text_color = ft.colors.WHITE
                    elif is_today:
                        # 今天 (未選中)：淺色用淺藍底深藍字，深色用深灰底淺藍字
                        bg_color = ft.colors.GREY_800 if is_dark else ft.colors.BLUE_50
                        text_color = ft.colors.BLUE_200 if is_dark else ft.colors.BLUE
                    else:
                        # 一般日期
                        bg_color = ft.colors.TRANSPARENT
                        text_color = None # 自動跟隨主題 (黑/白)
                    
                    # 嘗試使用第一筆行程的顏色，如果沒有則用紅色
                    dot_color = ft.colors.TRANSPARENT
                    if has_events:
                        first_event_color = events_on_day[0].get("color", "red")
                        dot_color = COLOR_OPTIONS.get(first_event_color, ft.colors.RED)

                    dot = ft.Container(width=4, height=4, border_radius=2, bgcolor=dot_color, margin=ft.margin.only(top=2))

                    def on_day_click(e, d=date_str):
                        state["selected_date"] = d
                        render_calendar() 
                        render_events()   

                    day_container = ft.Container(
                        content=ft.Column([ft.Text(str(day), color=text_color, weight=ft.FontWeight.BOLD), dot], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                        bgcolor=bg_color, border_radius=ft.border_radius.all(10), padding=5, alignment=ft.alignment.center,
                        on_click=on_day_click, expand=1, aspect_ratio=1
                    )
                    week_row.controls.append(day_container)
            calendar_grid.controls.append(week_row)
        page.update()

    # Dialog 與 Actions Sheet 邏輯
    def show_edit_dialog(index=-1):
        state["editing_index"] = index
        date_str = state["selected_date"]
        
        if index >= 0:
            # 使用 Repository 讀取單筆資料
            events = repo.get_events(date_str)
            event = events[index]
            page.dialog.title = ft.Text("編輯行程")
            tf_title.value = event["title"]
            sw_all_day.value = event["is_all_day"]
            dd_reminder.value = event["reminder"]
            tf_desc.value = event["description"]
            # 載入顏色
            state["temp_color"] = event.get("color", "blue")
            
            if not event["is_all_day"]:
                h_s, m_s = map(int, event["start_time"].split(":"))
                h_e, m_e = map(int, event["end_time"].split(":"))
                state["temp_start_time"] = datetime.time(h_s, m_s)
                state["temp_end_time"] = datetime.time(h_e, m_e)
            else:
                state["temp_start_time"] = datetime.time(9, 0)
                state["temp_end_time"] = datetime.time(10, 0)
        else:
            page.dialog.title = ft.Text("新增行程")
            tf_title.value = ""
            sw_all_day.value = False
            dd_reminder.value = "none"
            tf_desc.value = ""
            # 新增時重置為藍色
            state["temp_color"] = "blue"
            state["temp_start_time"] = datetime.time(9, 0)
            state["temp_end_time"] = datetime.time(10, 0)
        
        btn_start_time.text = state["temp_start_time"].strftime("%H:%M")
        btn_end_time.text = state["temp_end_time"].strftime("%H:%M")
        row_time_picker.visible = not sw_all_day.value
        tf_title.error_text = None
        
        # 渲染顏色選擇器
        render_color_picker()
        
        page.dialog.open = True
        page.update()

    def close_dialog(e):
        page.dialog.open = False
        page.update()

    def save_event(e):
        if not tf_title.value:
            tf_title.error_text = "請輸入標題"
            tf_title.update()
            return

        date_str = state["selected_date"]
        new_event = {
            "title": tf_title.value,
            "is_all_day": sw_all_day.value,
            "start_time": state["temp_start_time"].strftime("%H:%M"),
            "end_time": state["temp_end_time"].strftime("%H:%M"),
            "reminder": dd_reminder.value,
            "description": tf_desc.value,
            "color": state["temp_color"], # 儲存顏色
            "done": False 
        }

        if state["editing_index"] >= 0:
            repo.update_event(date_str, state["editing_index"], new_event)
        else:
            repo.add_event(date_str, new_event)
        
        render_events()
        render_calendar()
        close_dialog(e)

    page.dialog = ft.AlertDialog(
        content=ft.Column(
            [
                tf_title, 
                ft.Text("標籤顏色:", size=12, color=ft.colors.GREY),
                color_picker_row, # 加入顏色選擇列
                ft.Divider(),
                sw_all_day, 
                row_time_picker, 
                dd_reminder, 
                tf_desc
            ],
            tight=True, scroll=ft.ScrollMode.AUTO
        ),
        actions=[
            ft.TextButton("取消", on_click=close_dialog),
            ft.ElevatedButton("儲存", on_click=save_event),
        ],
    )

    def show_actions_sheet(index):
        def on_edit_click(e):
            page.close_bottom_sheet()
            show_edit_dialog(index)
            
        def on_delete_click(e):
            page.close_bottom_sheet()
            repo.delete_event(state["selected_date"], index)
            render_events()
            render_calendar()

        page.bottom_sheet = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.ListTile(leading=ft.Icon(ft.icons.EDIT), title=ft.Text("編輯"), on_click=on_edit_click),
                        ft.ListTile(leading=ft.Icon(ft.icons.DELETE), title=ft.Text("刪除"), on_click=on_delete_click),
                    ], tight=True,
                ), padding=10,
            ),
        )
        page.bottom_sheet.open = True
        page.update()

    # 10. 組裝主畫面
    def prev_month(e):
        if state["current_month"] == 1:
            state["current_month"] = 12
            state["current_year"] -= 1
        else:
            state["current_month"] -= 1
        render_calendar()

    def next_month(e):
        if state["current_month"] == 12:
            state["current_month"] = 1
            state["current_year"] += 1
        else:
            state["current_month"] += 1
        render_calendar()

    # 主題切換邏輯
    def toggle_theme(e):
        is_light = page.theme_mode == ft.ThemeMode.LIGHT
        page.theme_mode = ft.ThemeMode.DARK if is_light else ft.ThemeMode.LIGHT
        
        # 同步切換背景色
        page.bgcolor = ft.colors.BLACK if page.theme_mode == ft.ThemeMode.DARK else ft.colors.WHITE
        
        page.client_storage.set("theme_mode", "dark" if page.theme_mode == ft.ThemeMode.DARK else "light")
        
        # 更新按鈕圖示
        theme_icon.icon = ft.icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE
        
        # 先重繪內容，最後再一次性 update
        render_calendar() 

    theme_icon = ft.IconButton(
        ft.icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE,
        on_click=toggle_theme
    )

    page.appbar = ft.AppBar(
        leading=ft.IconButton(ft.icons.CHEVRON_LEFT, on_click=prev_month),
        title=current_month_text, center_title=True,
        actions=[
            ft.IconButton(ft.icons.CHEVRON_RIGHT, on_click=next_month),
            theme_icon # 加入主題切換按鈕
        ],
        # 移除固定背景，改用 Surface Variant 或預設
        bgcolor=None, 
    )

    event_header = ft.Container(
        content=selected_date_text, padding=ft.padding.only(left=20, top=10, bottom=5)
    )

    fab_button = ft.FloatingActionButton(
        icon=ft.icons.ADD, on_click=lambda _: show_edit_dialog(-1), bgcolor=ft.colors.BLUE,
    )

    main_content = ft.Column(
        [ft.Container(calendar_grid, padding=10), ft.Divider(height=1, thickness=1), event_header, event_list_view],
        expand=True, spacing=0
    )

    page.add(ft.Stack([
        ft.Container(content=main_content, expand=True),
        ft.Container(content=fab_button, right=20, bottom=20),
    ], expand=True))

    render_calendar()
    render_events()

if __name__ == "__main__":
    ft.app(target=main)