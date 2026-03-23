from .settings import *  # noqa: F403


# Use SQLite for tests so developers don't need Postgres running.
DATABASES = {  # noqa: F405
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Avoid external services during tests.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

# Celery: execute tasks locally when used.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

