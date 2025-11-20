# from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query
# from fastapi.responses import FileResponse, StreamingResponse
# from sqlalchemy.orm import Session
# from sqlalchemy import desc
# from database import get_db
# from models import User, Video
# from schemas import VideoCreate, VideoResponse, VideoListResponse, VideoUpdate
# from security import get_current_user
# from minio_client import minio_client
# from utils import video_processor
# from config import settings
# import os
# import uuid
# from pathlib import Path
# import io

# router = APIRouter(prefix="/api/videos", tags=["Videos"])

# TEMP_UPLOAD_DIR = "./temp_uploads"
# os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

# @router.post("/upload", response_model=VideoResponse)
# async def upload_video(
#     file: UploadFile = File(...),
#     title: str = Query(..., min_length=1, max_length=255),
#     description: str = Query(None, max_length=1000),
#     is_public: bool = Query(True),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Upload a video file"""
    
#     # Validate file extension
#     file_ext = Path(file.filename).suffix.lower().lstrip('.')
#     if file_ext not in settings.ALLOWED_VIDEO_FORMATS:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid video format. Allowed: {', '.join(settings.ALLOWED_VIDEO_FORMATS)}"
#         )
    
#     # Read file and check size
#     file_content = await file.read()
#     file_size = len(file_content)
    
#     if file_size > settings.MAX_VIDEO_SIZE_MB_MB:
#         raise HTTPException(
#             status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
#             detail=f"File size exceeds maximum allowed size of {settings.MAX_VIDEO_SIZE_MB_MB / 1024 / 1024 / 1024}GB"
#         )
    
#     # Save temporarily to validate
#     temp_file_path = os.path.join(TEMP_UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
#     with open(temp_file_path, "wb") as temp_file:
#         temp_file.write(file_content)
    
#     # Validate video file
#     is_valid, validation_msg = video_processor.validate_video_file(temp_file_path, settings.ALLOWED_VIDEO_FORMATS)
#     if not is_valid:
#         os.remove(temp_file_path)
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=validation_msg
#         )
    
#     # Get video metadata
#     metadata = video_processor.get_video_metadata(temp_file_path)
    
#     # Generate unique object name for MinIO
#     object_name = f"videos/{current_user.id}/{uuid.uuid4()}_{file.filename}"
    
#     # Upload to MinIO
#     success = minio_client.upload_fileobj(
#         io.BytesIO(file_content),
#         object_name,
#         file_size
#     )
    
#     if not success:
#         os.remove(temp_file_path)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to upload video to storage"
#         )
    
#     # Generate thumbnail
#     thumbnail_name = None
#     thumbnail_temp = os.path.join(TEMP_UPLOAD_DIR, f"thumb_{uuid.uuid4()}.jpg")
#     if video_processor.generate_thumbnail(temp_file_path, thumbnail_temp):
#         with open(thumbnail_temp, "rb") as thumb_file:
#             thumb_content = thumb_file.read()
#         thumbnail_name = f"thumbnails/{current_user.id}/{uuid.uuid4()}.jpg"
#         minio_client.upload_fileobj(io.BytesIO(thumb_content), thumbnail_name, len(thumb_content))
#         os.remove(thumbnail_temp)

#     video_url = minio_client.get_object_url(object_name)
    
#     # Save to database
#     db_video = Video(
#         title=title,
#         description=description,
#         uploader_id=current_user.id,
#         file_name=file.filename,
#         file_size=file_size,
#         file_path=object_name,
#         video_url = video_url,
#         duration=metadata.get('duration'),
#         width=metadata.get('width'),
#         height=metadata.get('height'),
#         fps=metadata.get('fps'),
#         codec=metadata.get('codec'),
#         thumbnail_path=thumbnail_name,
#         is_public=is_public,
#         is_processed=True
#     )
    
#     db.add(db_video)
#     db.commit()
#     db.refresh(db_video)
    
#     # Cleanup temporary file
#     os.remove(temp_file_path)
    
#     return db_video

# @router.get("/", response_model=VideoListResponse)
# def list_videos(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(10, ge=1, le=100),
#     db: Session = Depends(get_db)
# ):
#     """List all public videos with pagination"""
#     total = db.query(Video).filter(Video.is_public == True).count()
#     videos = db.query(Video).filter(
#         Video.is_public == True
#     ).order_by(desc(Video.created_at)).offset(skip).limit(limit).all()
    
#     return VideoListResponse(total=total, skip=skip, limit=limit, videos=videos)

# @router.get("/my-videos", response_model=VideoListResponse)
# def list_my_videos(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(10, ge=1, le=100),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """List current user's videos"""
#     total = db.query(Video).filter(Video.uploader_id == current_user.id).count()
#     videos = db.query(Video).filter(
#         Video.uploader_id == current_user.id
#     ).order_by(desc(Video.created_at)).offset(skip).limit(limit).all()
    
#     return VideoListResponse(total=total, skip=skip, limit=limit, videos=videos)

# @router.get("/{video_id}", response_model=VideoResponse)
# def get_video(video_id: int, db: Session = Depends(get_db)):
#     """Get video details"""
#     video = db.query(Video).filter(Video.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
#     if not video.is_public:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Video is private")
    
#     # Increment view count
#     video.view_count += 1
#     db.commit()
    
#     return video

# @router.put("/{video_id}", response_model=VideoResponse)
# def update_video(
#     video_id: int,
#     video_update: VideoUpdate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Update video metadata"""
#     video = db.query(Video).filter(Video.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
#     if video.uploader_id != current_user.id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this video")
    
#     if video_update.title:
#         video.title = video_update.title
#     if video_update.description is not None:
#         video.description = video_update.description
#     if video_update.is_public is not None:
#         video.is_public = video_update.is_public
    
#     db.commit()
#     db.refresh(video)
#     return video

# @router.delete("/{video_id}")
# def delete_video(
#     video_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Delete video"""
#     video = db.query(Video).filter(Video.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
#     if video.uploader_id != current_user.id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this video")
    
#     # Delete from MinIO
#     minio_client.delete_file(video.file_path)
#     if video.thumbnail_path:
#         minio_client.delete_file(video.thumbnail_path)
    
#     # Delete from database
#     db.delete(video)
#     db.commit()
    
#     return {"message": "Video deleted successfully"}

# # @router.get("/{video_id}/download")
# # def download_video(
# #     video_id: int,
# #     current_user: User = Depends(get_current_user),
# #     db: Session = Depends(get_db)
# # ):
# #     """Download video (only uploader can download)"""
# #     video = db.query(Video).filter(Video.id == video_id).first()
# #     if not video:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
# #     if video.uploader_id != current_user.id:
# #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to download this video")
    
# #     # Get download URL from MinIO
# #     url = minio_client.get_object_url_download(video.file_path, expiration=3600)
# #     if not url:
# #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate download URL")
    
# #     return {"download_url": url}

# @router.get("/{video_id}/stream")
# def stream_video(video_id: int, db: Session = Depends(get_db)):
#     """Stream video (public access with range requests)"""
#     video = db.query(Video).filter(Video.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
#     if not video.is_public:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Video is private")
    
#     # Get stream URL from MinIO
#     url = minio_client.get_object_url(video.file_path, expiration=3600)
#     if not url:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate stream URL")
    
#     return {"stream_url": url}



from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import User, Video
from schemas import VideoCreate, VideoResponse, VideoListResponse, VideoUpdate
from security import get_current_user
from minio_client import minio_client
from utils import video_processor
from config import settings
import os
import uuid
from pathlib import Path
import io

router = APIRouter(prefix="/api/videos", tags=["Videos"])

TEMP_UPLOAD_DIR = "./temp_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Query(..., min_length=1, max_length=255),
    description: str = Query(None, max_length=1000),
    is_public: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a video file"""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in settings.ALLOWED_VIDEO_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid video format. Allowed: {', '.join(settings.ALLOWED_VIDEO_FORMATS)}"
        )
    
    # Read file and check size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.MAX_VIDEO_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_VIDEO_SIZE_MB / 1024 / 1024 / 1024}GB"
        )
    
    # Save temporarily to validate
    temp_file_path = os.path.join(TEMP_UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(file_content)
    
    # Validate video file
    is_valid, validation_msg = video_processor.validate_video_file(temp_file_path, settings.ALLOWED_VIDEO_FORMATS)
    if not is_valid:
        os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation_msg
        )
    
    # Get video metadata
    metadata = video_processor.get_video_metadata(temp_file_path)
    
    # Generate unique object name for MinIO
    object_name = f"videos/{current_user.id}/{uuid.uuid4()}_{file.filename}"
    
    # Upload to MinIO
    success = minio_client.upload_fileobj(
        io.BytesIO(file_content),
        object_name,
        file_size
    )
    
    if not success:
        os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload video to storage"
        )
    
    # Generate thumbnail
    thumbnail_name = None
    thumbnail_temp = os.path.join(TEMP_UPLOAD_DIR, f"thumb_{uuid.uuid4()}.jpg")
    if video_processor.generate_thumbnail(temp_file_path, thumbnail_temp):
        with open(thumbnail_temp, "rb") as thumb_file:
            thumb_content = thumb_file.read()
        thumbnail_name = f"thumbnails/{current_user.id}/{uuid.uuid4()}.jpg"
        minio_client.upload_fileobj(io.BytesIO(thumb_content), thumbnail_name, len(thumb_content))
        os.remove(thumbnail_temp)

    video_url = minio_client.get_object_url(object_name)
    
    # Save to database
    db_video = Video(
        title=title,
        description=description,
        uploader_id=current_user.id,
        file_name=file.filename,
        video_url=video_url,
        file_size=file_size,
        file_path=object_name,
        duration=metadata.get('duration'),
        width=metadata.get('width'),
        height=metadata.get('height'),
        fps=metadata.get('fps'),
        codec=metadata.get('codec'),
        thumbnail_path=thumbnail_name,
        is_public=is_public,
        is_processed=True
    )
    
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    
    # Cleanup temporary file
    os.remove(temp_file_path)
    
    return db_video

@router.get("/", response_model=VideoListResponse)
def list_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all public videos with pagination"""
    total = db.query(Video).filter(Video.is_public == True).count()
    videos = db.query(Video).filter(
        Video.is_public == True
    ).order_by(desc(Video.created_at)).offset(skip).limit(limit).all()

    videos_response = []
    for v in videos:
        if not v.video_url:
            v.video_url = minio_client.get_object_url(v.file_name)
        videos_response.append(v)
        
    return VideoListResponse(total=total, skip=skip, limit=limit, videos=videos_response)

@router.get("/my-videos", response_model=VideoListResponse)
def list_my_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List current user's videos"""
    total = db.query(Video).filter(Video.uploader_id == current_user.id).count()
    videos = db.query(Video).filter(
        Video.uploader_id == current_user.id
    ).order_by(desc(Video.created_at)).offset(skip).limit(limit).all()     

    videos_response = []
    for v in videos:
        if not v.video_url:
            v.video_url = minio_client.get_object_url(v.file_name)
        videos_response.append(v)   
    
    return VideoListResponse(total=total, skip=skip, limit=limit, videos=videos)

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    """Get video details"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    if not video.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Video is private")
    
    # Increment view count
    video.view_count += 1
    db.commit()
    
    return video

@router.put("/{video_id}", response_model=VideoResponse)
def update_video(
    video_id: int,
    video_update: VideoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update video metadata"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    if video.uploader_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this video")
    
    if video_update.title:
        video.title = video_update.title
    if video_update.description is not None:
        video.description = video_update.description
    if video_update.is_public is not None:
        video.is_public = video_update.is_public
    
    db.commit()
    db.refresh(video)
    return video

@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    if video.uploader_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this video")
    
    # Delete from MinIO
    minio_client.delete_file(video.file_path)
    if video.thumbnail_path:
        minio_client.delete_file(video.thumbnail_path)
    
    # Delete from database
    db.delete(video)
    db.commit()
    
    return {"message": "Video deleted successfully"}

# @router.get("/{video_id}/download")
# def download_video(
#     video_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Download video (only uploader can download)"""
#     video = db.query(Video).filter(Video.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
#     if video.uploader_id != current_user.id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to download this video")
    
#     # Get download URL from MinIO
#     url = minio_client.get_object_url(video.file_path, expiration=3600)
#     if not url:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate download URL")
    
#     return {"download_url": url}

# @router.get("/{video_id}/stream")
# def stream_video(video_id: int, db: Session = Depends(get_db)):
#     """Stream video (public access with range requests)"""
#     video = db.query(Video).filter(Video.id == video_id).first()
#     if not video:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
#     if not video.is_public:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Video is private")
    
#     # Get stream URL from MinIO
#     url = minio_client.get_object_url(video.file_path, expiration=3600)
#     if not url:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate stream URL")
    
#     return {"stream_url": url}

@router.get("/uploader/{uploader_id}/videos", response_model=VideoListResponse)
def get_uploader_videos(
    uploader_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all public videos from a specific uploader"""
    total = db.query(Video).filter(
        Video.uploader_id == uploader_id,
        Video.is_public == True
    ).count()
    
    videos = db.query(Video).filter(
        Video.uploader_id == uploader_id,
        Video.is_public == True
    ).order_by(desc(Video.created_at)).offset(skip).limit(limit).all()
    
    return VideoListResponse(total=total, skip=skip, limit=limit, videos=videos)

@router.get("/trending/popular-this-week", response_model=VideoListResponse)
def get_popular_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get most popular videos from the last 7 days by engagement (likes + comments + shares)"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    total = db.query(Video).filter(
        Video.is_public == True,
        Video.created_at >= week_ago
    ).count()
    
    videos = db.query(Video).filter(
        Video.is_public == True,
        Video.created_at >= week_ago
    ).order_by(
        desc(Video.like_count + Video.comment_count + Video.share_count)
    ).offset(skip).limit(limit).all()
    
    return VideoListResponse(total=total, skip=skip, limit=limit, videos=videos)
