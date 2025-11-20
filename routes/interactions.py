from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from database import get_db
from models import User, Video, Like, Comment, Share, Favorite, Playlist
from schemas import (
    LikeResponse, CommentCreate, CommentResponse, ShareResponse, FavoriteResponse,
    LikeDetailResponse, CommentDetailResponse, ShareDetailResponse, FavoriteDetailResponse,
    VideoSearchResponse, VideoSearchListResponse
)
from security import get_current_user

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])

# ============= LIKES =============
@router.post("/videos/{video_id}/like", response_model=LikeResponse)
def like_video(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Like a video"""
    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    # Check if already liked
    existing_like = db.query(Like).filter(
        (Like.user_id == current_user.id) & (Like.video_id == video_id)
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already liked this video")
    
    # Create like
    like = Like(user_id=current_user.id, video_id=video_id)
    video.like_count += 1
    db.add(like)
    db.commit()
    db.refresh(like)
    
    return like

@router.delete("/videos/{video_id}/like")
def unlike_video(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Unlike a video"""
    like = db.query(Like).filter(
        (Like.user_id == current_user.id) & (Like.video_id == video_id)
    ).first()
    
    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")
    
    video = db.query(Video).filter(Video.id == video_id).first()
    video.like_count = max(0, video.like_count - 1)
    db.delete(like)
    db.commit()
    
    return {"message": "Video unliked successfully"}

@router.get("/videos/{video_id}/likes", response_model=list[LikeResponse])
def get_video_likes(video_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Get likes for a video"""
    likes = db.query(Like).filter(Like.video_id == video_id).offset(skip).limit(limit).all()
    return likes

@router.get("/user/liked-videos", response_model=list[LikeDetailResponse])
def get_user_liked_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all videos liked by current user with full details"""
    likes = db.query(Like).filter(
        Like.user_id == current_user.id
    ).order_by(desc(Like.created_at)).offset(skip).limit(limit).all()
    
    return likes

# ============= COMMENTS =============
@router.post("/videos/{video_id}/comments", response_model=CommentResponse)
def create_comment(video_id: int, comment_data: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add a comment to a video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    comment = Comment(
        user_id=current_user.id,
        video_id=video_id,
        content=comment_data.content
    )
    video.comment_count += 1
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment

@router.get("/videos/{video_id}/comments", response_model=list[CommentResponse])
def get_video_comments(video_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Get comments for a video"""
    comments = db.query(Comment).filter(Comment.video_id == video_id).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
    return comments

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a comment (only comment owner or admin)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment")
    
    video = db.query(Video).filter(Video.id == comment.video_id).first()
    video.comment_count = max(0, video.comment_count - 1)
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}

# Add endpoint to get user's commented videos with full details
@router.get("/user/commented-videos", response_model=list[CommentDetailResponse])
def get_user_commented_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all videos commented by current user with full details"""
    comments = db.query(Comment).filter(
        Comment.user_id == current_user.id
    ).order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()
    
    return comments

# ============= SHARES =============
@router.post("/videos/{video_id}/share", response_model=ShareResponse)
def share_video(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Share a video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    share = Share(user_id=current_user.id, video_id=video_id)
    video.share_count += 1
    db.add(share)
    db.commit()
    db.refresh(share)
    
    return share

@router.get("/videos/{video_id}/shares", response_model=list[ShareResponse])
def get_video_shares(video_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Get shares for a video"""
    shares = db.query(Share).filter(Share.video_id == video_id).offset(skip).limit(limit).all()
    return shares

@router.get("/user/shared-videos", response_model=list[ShareDetailResponse])
def get_user_shared_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all videos shared by current user with full details"""
    shares = db.query(Share).filter(
        Share.user_id == current_user.id
    ).order_by(desc(Share.created_at)).offset(skip).limit(limit).all()
    
    return shares

# ============= FAVORITES =============
@router.post("/videos/{video_id}/favorite", response_model=FavoriteResponse)
def favorite_video(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add video to favorites"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    existing_favorite = db.query(Favorite).filter(
        (Favorite.user_id == current_user.id) & (Favorite.video_id == video_id)
    ).first()
    
    if existing_favorite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already in favorites")
    
    favorite = Favorite(user_id=current_user.id, video_id=video_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return favorite

@router.delete("/videos/{video_id}/favorite")
def unfavorite_video(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Remove video from favorites"""
    favorite = db.query(Favorite).filter(
        (Favorite.user_id == current_user.id) & (Favorite.video_id == video_id)
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not in favorites")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "Removed from favorites"}

# @router.get("/user/favorites", response_model=list[int])
# def get_user_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """Get user's favorite video IDs"""
#     favorites = db.query(Favorite.video_id).filter(Favorite.user_id == current_user.id).all()
#     return [fav[0] for fav in favorites]

@router.get("/user/favorite-videos", response_model=list[FavoriteDetailResponse])
def get_user_favorite_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all favorite videos of current user with full details"""
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).order_by(desc(Favorite.created_at)).offset(skip).limit(limit).all()
    
    return favorites

# ============= SEARCH =============
@router.get("/search/videos", response_model=VideoSearchListResponse)
def search_videos(
    q: str = Query(..., min_length=1, max_length=255),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search videos by title or description"""
    # Search in both title and description, case-insensitive
    search_query = f"%{q}%"
    
    total = db.query(Video).filter(
        Video.is_public == True,
        or_(
            Video.title.ilike(search_query),
            Video.description.ilike(search_query)
        )
    ).count()
    
    videos = db.query(Video).filter(
        Video.is_public == True,
        or_(
            Video.title.ilike(search_query),
            Video.description.ilike(search_query)
        )
    ).order_by(desc(Video.created_at)).offset(skip).limit(limit).all()
    
    return VideoSearchListResponse(
        total=total,
        skip=skip,
        limit=limit,
        query=q,
        videos=videos
    )

@router.get("/trending/videos", response_model=list[VideoSearchResponse])
def get_trending_videos(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get trending videos sorted by like count"""
    videos = db.query(Video).filter(
        Video.is_public == True
    ).order_by(desc(Video.like_count), desc(Video.view_count)).limit(limit).all()
    
    return videos

# ============= PLATFORM STATS =============
@router.get("/stats/likes")
def get_platform_likes_count(db: Session = Depends(get_db)):
    """Get total likes across all videos"""
    total_likes = db.query(Like).count()
    return {"total_likes": total_likes}

@router.get("/stats/comments")
def get_platform_comments_count(db: Session = Depends(get_db)):
    """Get total comments across all videos"""
    total_comments = db.query(Comment).count()
    return {"total_comments": total_comments}

@router.get("/stats/videos")
def get_platform_videos_count(db: Session = Depends(get_db)):
    """Get total videos on platform"""
    total_videos = db.query(Video).count()
    return {"total_videos": total_videos}

@router.get("/stats/overview")
def get_platform_overview(db: Session = Depends(get_db)):
    """Get complete platform statistics"""
    return {
        "total_videos": db.query(Video).count(),
        "total_likes": db.query(Like).count(),
        "total_comments": db.query(Comment).count(),
        "total_shares": db.query(Share).count(),
        "total_users": db.query(User).count(),
        "total_playlists": db.query(Playlist).count(),
    }
