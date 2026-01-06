import flet as ft
from auth_service import AuthService

def show_login_dialog(page: ft.Page, auth_service: AuthService, on_login_success):
    email_tf = ft.TextField(label="Email", width=300)
    pass_tf = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
    error_text = ft.Text(color=ft.colors.RED, size=12)

    def handle_sign_in(e):
        error_text.value = "Signing in..."
        page.update()
        success, msg = auth_service.sign_in(email_tf.value, pass_tf.value)
        if success:
            page.dialog.open = False
            page.update()
            on_login_success()
        else:
            error_text.value = f"Login failed: {msg}"
            page.update()

    def handle_sign_up(e):
        error_text.value = "Signing up..."
        page.update()
        success, msg = auth_service.sign_up(email_tf.value, pass_tf.value)
        if success:
            # Check if user needs to confirm email
            if auth_service.user and auth_service.user.identities and len(auth_service.user.identities) > 0:
                 # Usually if email confirmation is on, user won't be logged in fully or needs to check email.
                 # But assuming default setting or "auto confirm" for dev/testing if set.
                 # If Supabase project requires email confirmation, this might be tricky.
                 # We will assume success leads to login or instructions.
                 pass
            page.dialog.open = False
            page.update()
            on_login_success()
        else:
            error_text.value = f"Signup failed: {msg}"
            page.update()

    # Define content inside a function or reusable component
    content = ft.Column([
        ft.Text("登入 / 註冊", size=20, weight=ft.FontWeight.BOLD),
        email_tf,
        pass_tf,
        error_text,
        ft.Row([
            ft.ElevatedButton("登入", on_click=handle_sign_in),
            ft.OutlinedButton("註冊", on_click=handle_sign_up)
        ], alignment=ft.MainAxisAlignment.CENTER)
    ], tight=True, width=320, alignment=ft.MainAxisAlignment.CENTER)

    page.dialog = ft.AlertDialog(
        content=content,
        modal=True,
    )
    page.dialog.open = True
    page.update()
