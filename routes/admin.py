from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Video, Playlist, UserRole, Comment, Like, Share, Favorite
from schemas import UserResponse, VideoResponse, PlaylistResponse
from security import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ============= ADMIN VERIFICATION =============
def verify_admin(current_user: User = Depends(get_current_user)):
    """Verify that current user is an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# ============= USER MANAGEMENT =============
@router.get("/users", response_model=list[UserResponse])
def list_all_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """List all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_details(user_id: int, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Get user details (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, role: str, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Update user role (admin only)"""
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.role = UserRole(role)
    db.commit()
    
    return {"message": f"User {user_id} role updated to {role}"}

@router.put("/users/{user_id}/status")
def toggle_user_status(user_id: int, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Activate/deactivate user account (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    
    status_msg = "activated" if user.is_active else "deactivated"
    return {"message": f"User {user_id} has been {status_msg}"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Delete user account (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Delete all user's interactions first
    db.query(Like).filter(Like.user_id == user_id).delete()
    db.query(Comment).filter(Comment.user_id == user_id).delete()
    db.query(Share).filter(Share.user_id == user_id).delete()
    db.query(Favorite).filter(Favorite.user_id == user_id).delete()
    
    # Delete user's videos
    videos = db.query(Video).filter(Video.uploader_id == user_id).all()
    for video in videos:
        db.query(Like).filter(Like.video_id == video.id).delete()
        db.query(Comment).filter(Comment.video_id == video.id).delete()
        db.query(Share).filter(Share.video_id == video.id).delete()
        db.query(Favorite).filter(Favorite.video_id == video.id).delete()
        db.delete(video)
    
    # Delete user's playlists
    db.query(Playlist).filter(Playlist.creator_id == user_id).delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user_id} and all related data deleted"}

# ============= VIDEO MANAGEMENT =============
@router.get("/videos", response_model=list[VideoResponse])
def list_all_videos(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """List all videos (admin only)"""
    videos = db.query(Video).offset(skip).limit(limit).all()
    return videos

@router.delete("/videos/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Delete a video (admin only)"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    # Delete all interactions
    db.query(Like).filter(Like.video_id == video_id).delete()
    db.query(Comment).filter(Comment.video_id == video_id).delete()
    db.query(Share).filter(Share.video_id == video_id).delete()
    db.query(Favorite).filter(Favorite.video_id == video_id).delete()
    
    db.delete(video)
    db.commit()
    
    return {"message": f"Video {video_id} and all related data deleted"}

@router.put("/videos/{video_id}/status")
def toggle_video_status(video_id: int, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Toggle video public/private status (admin only)"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    video.is_public = not video.is_public
    db.commit()
    
    status_msg = "public" if video.is_public else "private"
    return {"message": f"Video {video_id} is now {status_msg}"}

# ============= PLAYLIST MANAGEMENT =============
@router.get("/playlists", response_model=list[PlaylistResponse])
def list_all_playlists(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """List all playlists (admin only)"""
    playlists = db.query(Playlist).offset(skip).limit(limit).all()
    return playlists

@router.delete("/playlists/{playlist_id}")
def delete_playlist(playlist_id: int, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Delete a playlist (admin only)"""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    
    db.delete(playlist)
    db.commit()
    
    return {"message": f"Playlist {playlist_id} deleted"}

# ============= PLATFORM MODERATION =============
@router.get("/content/flagged-comments")
def get_flagged_comments(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Get comments that might need review"""
    comments = db.query(Comment).offset(skip).limit(limit).all()
    return comments

@router.delete("/comments/{comment_id}")
def admin_delete_comment(comment_id: int, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Admin delete a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    video = db.query(Video).filter(Video.id == comment.video_id).first()
    if video:
        video.comment_count = max(0, video.comment_count - 1)
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted by admin"}

# ============= ADMIN STATS =============
@router.get("/stats/overview")
def admin_platform_stats(db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Get comprehensive platform statistics (admin only)"""
    return {
        "total_users": db.query(User).count(),
        "total_admin_users": db.query(User).filter(User.role == UserRole.ADMIN).count(),
        "total_regular_users": db.query(User).filter(User.role == UserRole.USER).count(),
        "total_videos": db.query(Video).count(),
        "total_public_videos": db.query(Video).filter(Video.is_public == True).count(),
        "total_private_videos": db.query(Video).filter(Video.is_public == False).count(),
        "total_likes": db.query(Like).count(),
        "total_comments": db.query(Comment).count(),
        "total_shares": db.query(Share).count(),
        "total_favorites": db.query(Favorite).count(),
        "total_playlists": db.query(Playlist).count(),
    }

@router.get("/stats/user/{user_id}")
def user_activity_stats(user_id: int, db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    """Get user activity statistics"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {
        "user_id": user_id,
        "username": user.username,
        "videos_uploaded": db.query(Video).filter(Video.uploader_id == user_id).count(),
        "comments_made": db.query(Comment).filter(Comment.user_id == user_id).count(),
        "likes_given": db.query(Like).filter(Like.user_id == user_id).count(),
        "shares_made": db.query(Share).filter(Share.user_id == user_id).count(),
        "favorites_count": db.query(Favorite).filter(Favorite.user_id == user_id).count(),
        "playlists_created": db.query(Playlist).filter(Playlist.creator_id == user_id).count(),
    }
