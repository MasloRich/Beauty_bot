# bot/handlers/__init__.py
from .client_handlers import router as client_router
from .admin_handlers import router as admin_router
from .master_handlers import router as master_router

__all__ = ['client_router', 'admin_router', 'master_router']