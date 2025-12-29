# 📅 Flet Mobile Calendar

A beautiful, cross-platform calendar application built with **Python** and **Flet**. Designed with a mobile-first approach, featuring Material Design 3, dark mode support, and a robust architecture ready for cloud synchronization.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-v0.25.2-purple?logo=flutter&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

*   **📱 Mobile-Optimized UI**:
    *   **Safe Area Handling**: Automatically adapts to status bars and notches.
    *   **Touch Interactions**: Swipe-to-delete, Long-press context menus (Bottom Sheet).
    *   **Floating Action Button (FAB)**: Correctly positioned using Stack layout.
*   **🎨 Personalization**:
    *   **Dark Mode**: Fully supported with persistent state and optimized color palettes (Indigo accents).
    *   **Color Tags**: Organize events with visual color strips (Blue, Red, Green, Orange, Purple, Grey).
*   **🗓️ Event Management**:
    *   **Month View**: Auto-calculated calendar grid.
    *   **Detailed Editor**: Support for Title, All-day toggle, Start/End time pickers, Reminders, and Descriptions.
    *   **Smart Indicators**: Calendar dots reflect the color of the day's events.
*   **💾 Data Persistence**:
    *   Local storage using `client_storage`.
    *   **Repository Pattern**: Clean separation of data logic and UI, ready for Supabase/Firebase migration.

## 🚀 Getting Started

### Prerequisites

*   Python 3.8+
*   Android device (with USB Debugging enabled) or Emulator for mobile testing.

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/flet-mobile-calendar.git
    cd flet-mobile-calendar
    ```

2.  **Install dependencies**:
    > **Note**: This project currently uses `flet==0.25.2` for maximum compatibility with the Flet Android App on Google Play (v0.27.x).
    ```bash
    pip install -r requirements.txt
    ```

### Running the App

*   **Run on Android** (Connect your phone via USB):
    ```bash
    flet run --android
    ```

*   **Run on Desktop** (Windows/macOS/Linux):
    ```bash
    flet run
    ```

## 🏗️ Architecture

This project follows a clean **Repository Pattern** to separate UI from Data logic:

*   `main.py`: Contains the UI components (Calendar Grid, Event List, Dialogs).
*   `EventRepository` Class: Handles CRUD operations (`load`, `save`, `add`, `update`, `delete`).

This structure makes it incredibly easy to switch the backend from local storage to a cloud database (like Supabase) in the future without rewriting the UI code.

## 📚 Documentation

We have documented the specific challenges and solutions encountered during Flet mobile development (e.g., Status bar overlap, Text decoration API changes).
Check out the guide here: [Flet Mobile Development Guide](docs/Flet_development_guide_mobile.md)

## 🔜 Roadmap

- [ ] **Cloud Sync**: Integrate Supabase for multi-user sharing.
- [ ] **Notifications**: Implement local push notifications.
- [ ] **Drag & Drop**: Reschedule events by dragging them on the calendar.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
