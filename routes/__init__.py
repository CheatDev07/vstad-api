from .auth import router as auth_router
from .videos import router as videos_router
from .interactions import router as interactions_router
from .admin import router as admin_router
from .playlists import router as playlists_router
from .profile import router as profile_router

__all__ = ["auth_router", "videos_router", "interactions_router", "admin_router", "playlists_router", "profile_router"]