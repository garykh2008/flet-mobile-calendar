# Gemini 協作紀錄 (Project Context & Roadmap)

本文件記錄了 `flet-mobile-calendar` 專案的開發歷程、關鍵技術決策以及未來的開發規劃。由 Gemini 協助開發者 Gary 共同完成。

---

## 1. 專案現狀 (Current Status)

截至 2025-12-29，我們已完成了一個功能完整的**單機版跨平台行事曆 App**。

### ✅ 已完成功能
*   **核心功能**：月曆瀏覽、行程 CRUD (新增/修改/刪除)、全天行程支援。
*   **UI/UX 優化**：
    *   **深色模式 (Dark Mode)**：完整適配，並對日曆配色進行了微調 (使用 Indigo/Light Blue)。
    *   **顏色標籤 (Color Tags)**：行程卡片左側顯示顏色條，日曆小紅點智慧跟隨行程顏色。
    *   **行動端體驗**：使用 `AppBar` 自動避讓狀態列，FAB 按鈕使用 `Stack` 精確定位，支援長按 (Long Press) 喚出底部選單。
*   **程式架構**：
    *   實作 **Repository Pattern** (`EventRepository`)，成功將 UI 與資料存取邏輯分離。
    *   目前使用 `client_storage` 進行本地持久化。

---

## 2. 關鍵技術決策與問題解決 (Key Decisions & Solutions)

在開發過程中，我們克服了以下幾個關鍵挑戰：

### 🛠️ Flet 版本與相容性
*   **決策**：降級 Flet 至 `0.25.2`。
*   **原因**：電腦端最新的 Flet 0.80.0 (Beta) 與手機端 Google Play 商店的 Flet App (0.27.x) 通訊協定不相容，導致 `KeyError: 'bytes'`。我們選擇降級以確保能立即在手機上測試。

### 📱 佈局與互動
*   **狀態列遮擋**：最初嘗試手動 Padding，後來改用 `ft.AppBar`，這是最符合原生體驗且自動適配的方案。
*   **FAB 點擊失效**：發現 `Stack` 中如果 Container 使用 `alignment` 對齊，會產生透明遮罩擋住底層點擊。解決方案是改用 `right/bottom` 屬性精確定位。
*   **顏色條消失**：在 `Column` 中使用 `Row(vertical_alignment=STRETCH)` 導致高度計算為 0。最終改用 `Container(border=ft.border.only(left=...))` 完美解決，且效能更好。

### 💾 資料架構
*   **決策**：引入 Repository Pattern。
*   **原因**：為了替未來的「雲端同步」做準備。現在 UI 層完全不知道資料存在哪裡，未來切換到 Supabase 時只需替換 Repository 實作即可。

---

## 3. 未來路線圖 (Roadmap)

接下來的開發將聚焦於 **雲端同步** 與 **多人協作**。

### 🚀 階段一：雲端基礎 (Backend Setup)
- [ ] **Supabase 整合**：
    - 建立 Supabase 專案與資料表 (`profiles`, `events`)。
    - 安裝 `supabase-py` 套件。
    - 實作 `SupabaseEventRepository` 替換現有的 `EventRepository`。
- [ ] **使用者驗證 (Auth)**：
    - 實作登入/註冊頁面 (Email/Password 或 Google Auth)。
    - 確保使用者只能看到自己的行程。

### 🤝 階段二：共享與協作 (Sharing)
- [ ] **行事曆共享**：允許使用者將自己的行事曆授權給其他 Email 帳號查看/編輯。
- [ ] **即時更新 (Realtime)**：利用 Supabase Realtime 功能，當 A 手機修改行程，B 手機畫面自動更新。

### 🔔 階段三：進階功能 (Advanced)
- [ ] **通知系統**：
    - 研究 Flet/Flutter 的本地通知整合，或使用 FCM 雲端推播。
    - 實作「App 內定時檢查」作為過渡方案。
- [ ] **UI 精修**：
    - 加入「回到今天」按鈕。
    - 支援左右滑動切換月份。

---

## 4. 有用的指令備忘

*   **啟動 App (Android)**：
    ```bash
    flet run --android
    ```
*   **提交 Git**：
    ```bash
    git add .
    git commit -m "你的訊息"
    git push
    ```

---
*紀錄時間：2025-12-29*
