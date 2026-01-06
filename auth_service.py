import flet as ft
from supabase import create_client, Client
import config

class AuthService:
    def __init__(self):
        self.supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        self.user = None

    def sign_in(self, email, password):
        try:
            res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            self.user = res.user
            return True, None
        except Exception as e:
            return False, str(e)

    def sign_up(self, email, password):
        try:
            res = self.supabase.auth.sign_up({"email": email, "password": password})
            # Supabase usually logs in automatically after signup if confirmation is disabled or returns user
            self.user = res.user
            return True, None
        except Exception as e:
            return False, str(e)

    def sign_out(self):
        self.supabase.auth.sign_out()
        self.user = None

    def get_current_user(self):
        # Check if session exists (Supabase client might persist it in some environments, but here we keep it simple in memory or handle restoration)
        # For simplicity in this Flet app, we just check our local variable or try to get session
        session = self.supabase.auth.get_session()
        if session:
            self.user = session.user
            return self.user
        return None
