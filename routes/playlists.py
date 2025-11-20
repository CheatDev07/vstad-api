from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Playlist, Video
from schemas import PlaylistCreate, PlaylistUpdate, PlaylistResponse, PlaylistDetailResponse
from security import get_current_user

router = APIRouter(prefix="/api/playlists", tags=["Playlists"])

@router.post("", response_model=PlaylistResponse)
def create_playlist(playlist_data: PlaylistCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new playlist"""
    playlist = Playlist(
        creator_id=current_user.id,
        title=playlist_data.title,
        description=playlist_data.description,
        is_public=playlist_data.is_public
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    
    return playlist

@router.get("/{playlist_id}", response_model=PlaylistDetailResponse)
def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    """Get playlist details with videos"""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    
    if not playlist.is_public:
        # Need to check if current user is the creator
        current_user = Depends(get_current_user)
        if current_user.id != playlist.creator_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access private playlist")
    
    return playlist

@router.get("/user/{user_id}")
def get_user_playlists(user_id: int, db: Session = Depends(get_db)):
    """Get all playlists created by a user"""
    playlists = db.query(Playlist).filter(Playlist.creator_id == user_id).all()
    return playlists

@router.put("/{playlist_id}", response_model=PlaylistResponse)
def update_playlist(playlist_id: int, playlist_data: PlaylistUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update playlist details"""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    
    if playlist.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this playlist")
    
    if playlist_data.title:
        playlist.title = playlist_data.title
    if playlist_data.description is not None:
        playlist.description = playlist_data.description
    if playlist_data.is_public is not None:
        playlist.is_public = playlist_data.is_public
    
    db.commit()
    db.refresh(playlist)
    
    return playlist

@router.delete("/{playlist_id}")
def delete_playlist(playlist_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a playlist"""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    
    if playlist.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this playlist")
    
    db.delete(playlist)
    db.commit()
    
    return {"message": "Playlist deleted successfully"}

@router.post("/{playlist_id}/videos/{video_id}")
def add_video_to_playlist(playlist_id: int, video_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add a video to a playlist"""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    
    if playlist.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this playlist")
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    if video in playlist.videos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Video already in playlist")
    
    playlist.videos.append(video)
    db.commit()
    
    return {"message": "Video added to playlist"}

@router.delete("/{playlist_id}/videos/{video_id}")
def remove_video_from_playlist(playlist_id: int, video_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Remove a video from a playlist"""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    
    if playlist.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this playlist")
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    if video not in playlist.videos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Video not in playlist")
    
    playlist.videos.remove(video)
    db.commit()
    
    return {"message": "Video removed from playlist"}
