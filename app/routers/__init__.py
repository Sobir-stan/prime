# Package initializer for app.routers
# Explicitly import router modules so they are available when imported from app.routers
from . import login, register, clicker, rating, skins

__all__ = ["login", "register", "clicker", "rating", "skins"]

