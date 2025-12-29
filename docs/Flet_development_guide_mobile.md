# Flet 全方位開發指南 (行動端與桌面端整合版)

本文件整合了專案結構、API 查詢原則、桌面端開發經驗以及行動端適配的實戰筆記。旨在提供一套標準化的 Flet 開發流程。

---

## 1. 專案初始化與結構

推薦的 Flet 專案結構：

```
your_flet_project/
├── docs/
│   ├── FLET_API_REF.md           # 本地 Flet 版本生成的 API 參考
│   ├── Flet_development_guide_mobile.md # 本文件
│   └── ...
├── tools/
│   └── generate_flet_api_ref.py  # 用於更新 FLET_API_REF.md
├── main.py                       # 主應用程式入口
└── README.md
```

**初始化建議：**
每次開始新專案或升級 Flet 版本後，運行 `python tools/generate_flet_api_ref.py` 以確保 `FLET_API_REF.md` 反映當前環境，這能大幅減少 API 誤用。

---

## 2. API 查詢與驗證流程 (核心原則)

Flet API 變動頻繁 (特別是從 0.2x 到 0.80+)，嚴格遵循以下流程：

1.  **優先查閱本地 `FLET_API_REF.md`**：最準確的來源，反映當前安裝版本。
2.  **反射檢查 (Inspection)**：
    當遇到 `AttributeError` 或行為不明時，直接用 Python 檢查：
    ```python
    import flet as ft
    import inspect
    print(inspect.signature(ft.Tabs.__init__)) # 檢查參數
    print(dir(ft.Tabs)) # 檢查屬性
    ```
3.  **參考官方文件**：作為輔助，但需注意版本差異。

---

## 3. 行動端開發指南 (Mobile Specifics)

本節紀錄在開發手機 App (Android/iOS) 時的關鍵適配經驗，特別是針對 Flet 0.25.x 環境。

### 3.1 環境相容性 (Version Compatibility)
*   **問題**：執行 `flet run --android` 時出現 `KeyError: 'bytes'` 或 `ImportError`。
*   **原因**：電腦端 Flet 版本 (如 0.80.0) 太新，與手機端 Flet App (如 0.27.x) 通訊協定不相容。
*   **解決**：降級電腦端 Flet 至穩定版。
    ```bash
    pip install flet==0.25.2
    ```

### 3.2 佈局與 UI 適配
*   **避開狀態列 (Safe Area)**：
    *   **推薦**：使用 `ft.AppBar`，系統會自動處理狀態列高度。
    *   **替代**：使用 `ft.SafeArea` 包裹主內容。
    *   **強制**：若上述失效，手動給容器加 Padding：`padding=ft.padding.only(top=35)`。

*   **懸浮按鈕 (FAB) 遮擋問題**：
    *   **問題**：使用 `Stack` 佈局時，若 Container 使用 `alignment` 對齊，可能導致透明層覆蓋全螢幕，攔截點擊。
    *   **解決**：使用 `right`, `bottom` 屬性精確定位。
    ```python
    # 正確：僅佔據右下角
    ft.Container(content=fab_button, right=20, bottom=20)
    ```

*   **Row 佈局高度陷阱**：
    *   **問題**：在 `Column` 中使用 `Row(vertical_alignment=ft.CrossAxisAlignment.STRETCH)` 可能導致內容消失（高度計算為 0）。
    *   **解決**：改用 `Container` 的 `border` 屬性來實現垂直線條效果。

---

## 4. 控制項與語法差異 (API Differences)

### 4.1 Text 裝飾線
*   **0.25.x 寫法**：`decoration` 必須透過 `style` 參數傳遞。
    ```python
    ft.Text("內容", style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH))
    ```
*   **新版寫法**：部分新版可能支援直接參數，但 `style` 寫法最通用。

### 4.2 事件處理與閉包 (Closures)
*   **問題**：在迴圈中綁定事件 (如 `on_click`)，所有按鈕都指向最後一個索引。
*   **解決**：使用 `control.data` 屬性儲存索引，並定義共用處理函數。
    ```python
    def handle_click(e):
        idx = e.control.data
        # 處理邏輯...

    ft.IconButton(..., on_click=handle_click, data=i)
    ```

### 4.3 啟動與非同步
*   **Flet 0.25.x**：推薦使用同步 `def main(page)` 配合 `ft.app(target=main)`。
*   **Flet 0.80+**：推薦使用 `async def main(page)` 配合 `ft.run(main)`。

---

## 5. 資料與架構 (Best Practices)

### 5.1 Repository Pattern (倉儲模式)
*   **目的**：將 UI 顯示與資料存取邏輯分離，方便未來遷移至雲端。
*   **實作**：
    *   建立 `EventRepository` 類別，封裝 `client_storage` 操作。
    *   UI 層只呼叫 `repo.add()`, `repo.get()`，不直接碰觸儲存細節。

### 5.2 資料持久化
*   使用 `page.client_storage` 可將資料存在手機本地，App 重啟後依然保留。

---

*文件最後更新日期：2025-12-29*