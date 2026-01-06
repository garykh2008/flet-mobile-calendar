import flet as ft
from supabase import Client
import datetime

class SupabaseEventRepository:
    def __init__(self, page: ft.Page, supabase_client: Client):
        self.page = page
        self.supabase = supabase_client
        # Cache for performance, similar to local repo, but needs syncing
        # For simplicity in V1, we might fetch from network on date change or update
        # But to keep UI responsive, we can cache.
        # Let's use a simple dictionary cache like the original repo
        self._cache = {}
        # Note: In a real app, we should handle cache invalidation or realtime updates.

    def load_events(self, date_str: str = None):
        """
        Loads events from Supabase.
        If date_str is provided, loads for that date (and maybe surrounding).
        For now, let's load all events for the user to populate the cache initially or on demand.
        Ideally we query by range (month).
        """
        try:
            # Loading *all* events might be heavy later, but okay for start.
            # Let's filter by month if possible, but the original repo structure relies on
            # `get_events` returning a list from memory.
            # To minimize refactoring, we can fetch all events on init or lazy load.
            response = self.supabase.table("events").select("*").execute()
            data = response.data

            # Rebuild cache: { "YYYY-MM-DD": [event1, event2, ...] }
            self._cache = {}
            for row in data:
                d_str = row["date"]
                if d_str not in self._cache:
                    self._cache[d_str] = []

                # Convert Supabase row back to app's expected dict format
                event_dict = {
                    "id": row["id"], # Keep ID for updates
                    "title": row["title"],
                    "is_all_day": row["is_all_day"],
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "reminder": row["reminder"],
                    "description": row["description"],
                    "color": row["color"]
                }
                self._cache[d_str].append(event_dict)

        except Exception as e:
            print(f"Error loading events: {e}")
            # Optionally show snackbar

    def get_events(self, date_str: str) -> list:
        # If we want to be chatty, we could fetch here if not in cache.
        # For now, assume load_events is called periodically or at start.
        if not self._cache:
             self.load_events()

        # Sort by start time for consistent display
        events = self._cache.get(date_str, [])
        # Simple sort: All day first, then by time
        events.sort(key=lambda x: (not x.get("is_all_day", False), x.get("start_time", "")))
        return events

    def add_event(self, date_str: str, event_data: dict):
        try:
            # Prepare data for Supabase
            row = {
                "user_id": self.supabase.auth.get_user().user.id,
                "date": date_str,
                "title": event_data["title"],
                "is_all_day": event_data["is_all_day"],
                "start_time": event_data["start_time"],
                "end_time": event_data["end_time"],
                "reminder": event_data["reminder"],
                "description": event_data["description"],
                "color": event_data["color"]
            }

            res = self.supabase.table("events").insert(row).execute()

            # Update Cache with returned data (which includes ID)
            if res.data:
                new_row = res.data[0]
                if date_str not in self._cache:
                    self._cache[date_str] = []

                # Update event_data with ID
                event_data["id"] = new_row["id"]
                self._cache[date_str].append(event_data)

        except Exception as e:
            print(f"Error adding event: {e}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"新增失敗: {e}"))
            self.page.snack_bar.open = True
            self.page.update()

    def update_event(self, date_str: str, index: int, event_data: dict):
        # We need the ID to update in Supabase
        # The 'index' from UI is the index in the list returned by get_events
        # We need to make sure we have the correct event ID.
        try:
            current_list = self._cache.get(date_str, [])
            if not (0 <= index < len(current_list)):
                return

            old_event = current_list[index]
            event_id = old_event.get("id")

            if not event_id:
                print("Error: Event ID missing for update")
                return

            update_row = {
                "title": event_data["title"],
                "is_all_day": event_data["is_all_day"],
                "start_time": event_data["start_time"],
                "end_time": event_data["end_time"],
                "reminder": event_data["reminder"],
                "description": event_data["description"],
                "color": event_data["color"]
            }

            self.supabase.table("events").update(update_row).eq("id", event_id).execute()

            # Update cache
            event_data["id"] = event_id # Keep ID
            self._cache[date_str][index] = event_data

        except Exception as e:
            print(f"Error updating event: {e}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"更新失敗: {e}"))
            self.page.snack_bar.open = True
            self.page.update()

    def delete_event(self, date_str: str, index: int):
        try:
            current_list = self._cache.get(date_str, [])
            if not (0 <= index < len(current_list)):
                return

            event = current_list[index]
            event_id = event.get("id")

            if not event_id:
                 # If local only (maybe migration issue), just remove from cache
                 del self._cache[date_str][index]
                 return

            self.supabase.table("events").delete().eq("id", event_id).execute()

            # Update cache
            del self._cache[date_str][index]

        except Exception as e:
            print(f"Error deleting event: {e}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"刪除失敗: {e}"))
            self.page.snack_bar.open = True
            self.page.update()
