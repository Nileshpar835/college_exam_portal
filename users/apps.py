from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    # Give this app a unique label to avoid collisions with any other 'users' app
    label = 'users'
