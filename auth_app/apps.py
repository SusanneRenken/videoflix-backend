"""
App configuration for the authentication app.

Ensures that Django signals are registered when the app is ready.
"""

from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    name = "auth_app"

    def ready(self):
        import auth_app.signals # noqa: F401
