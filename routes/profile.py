# from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
# from sqlalchemy.orm import Session
# from database import get_db
# from models import User
# from schemas import UserResponse, UserProfileUpdate
# from security import get_current_user
# from minio_client import minio_client
# import uuid
# import os
# from datetime import datetime

# router = APIRouter(prefix="/api/profile", tags=["Profile"])

# # Define a separate bucket for profile images
# PROFILE_IMAGE_BUCKET = "profile-images"

# def ensure_profile_bucket():
#     """Ensure profile images bucket exists"""
#     try:
#         if not minio_client.client.bucket_exists(PROFILE_IMAGE_BUCKET):
#             minio_client.client.make_bucket(PROFILE_IMAGE_BUCKET)
#     except Exception as e:
#         print(f"Error creating profile bucket: {e}")

# # Ensure bucket exists on startup
# ensure_profile_bucket()

# # @router.get("/me", response_model=UserResponse)
# # def get_profile(current_user: User = Depends(get_current_user)):
# #     """Get current user's profile"""
# #     return current_user

# # @router.get("/{user_id}", response_model=UserResponse)
# # def get_user_profile(user_id: int, db: Session = Depends(get_db)):
# #     """Get another user's profile"""
# #     user = db.query(User).filter(User.id == user_id).first()
# #     if not user:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="User not found"
# #         )
# #     return user

# @router.put("/me/update", response_model=UserResponse)
# def update_profile(
#     profile_data: UserProfileUpdate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Update user profile information"""
#     # Check if new username is unique (if being changed)
#     if profile_data.username and profile_data.username != current_user.username:
#         existing_user = db.query(User).filter(User.username == profile_data.username).first()
#         if existing_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Username already taken"
#             )
    
#     # Update fields
#     if profile_data.full_name is not None:
#         current_user.full_name = profile_data.full_name
#     if profile_data.bio is not None:
#         current_user.bio = profile_data.bio
#     if profile_data.username is not None:
#         current_user.username = profile_data.username
    
#     current_user.updated_at = datetime.utcnow()
#     db.commit()
#     db.refresh(current_user)
    
#     return current_user

# @router.post("/me/upload-profile-image")
# def upload_profile_image(
#     file: UploadFile = File(...),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Upload user profile image"""
#     # Validate file
#     allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
#     file_ext = os.path.splitext(file.filename)[1].lower()
    
#     if file_ext not in allowed_extensions:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
#         )
    
#     # Validate file size (max 5MB)
#     max_size = 5 * 1024 * 1024
#     contents = file.file.read()
#     if len(contents) > max_size:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="File size exceeds 5MB limit"
#         )
    
#     try:
#         # Generate unique filename
#         file_name = f"user_{current_user.id}_{uuid.uuid4()}{file_ext}"
        
#         # Upload to MinIO
#         from io import BytesIO
#         file_bytes = BytesIO(contents)
#         minio_client.client.put_object(
#             PROFILE_IMAGE_BUCKET,
#             file_name,
#             file_bytes,
#             len(contents),
#             content_type=file.content_type
#         )
        
#         # Update user profile image
#         current_user.profile_image = file_name
#         current_user.updated_at = datetime.utcnow()
#         db.commit()
#         db.refresh(current_user)
        
#         # Get presigned URL
#         from datetime import timedelta
#         profile_image_url = minio_client.client.get_presigned_download_url(
#             PROFILE_IMAGE_BUCKET,
#             file_name,
#             expires=timedelta(days=365)
#         )
        
#         return {
#             "message": "Profile image uploaded successfully",
#             "profile_image": file_name,
#             "profile_image_url": profile_image_url,
#             "user": current_user
#         }
    
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error uploading profile image: {str(e)}"
#         )

# @router.get("/me/profile-image-url")
# def get_profile_image_url(current_user: User = Depends(get_current_user)):
#     """Get presigned URL for user's profile image"""
#     if not current_user.profile_image:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User has no profile image"
#         )
    
#     try:
#         from datetime import timedelta
#         profile_image_url = minio_client.client.get_presigned_download_url(
#             PROFILE_IMAGE_BUCKET,
#             current_user.profile_image,
#             expires=timedelta(days=365)
#         )
#         return {
#             "profile_image": current_user.profile_image,
#             "profile_image_url": profile_image_url
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error getting profile image URL: {str(e)}"
#         )

# @router.delete("/me/profile-image")
# def delete_profile_image(
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Delete user's profile image"""
#     if not current_user.profile_image:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User has no profile image"
#         )
    
#     try:
#         # Delete from MinIO
#         minio_client.client.remove_object(PROFILE_IMAGE_BUCKET, current_user.profile_image)
        
#         # Update user
#         current_user.profile_image = None
#         current_user.updated_at = datetime.utcnow()
#         db.commit()
#         db.refresh(current_user)
        
#         return {"message": "Profile image deleted successfully"}
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error deleting profile image: {str(e)}"
#         )


from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserResponse, UserProfileUpdate
from security import get_current_user
from minio_client import minio_client
import uuid
import os
from datetime import datetime

# Profile image storage configuration
PROFILE_IMAGE_DIR = Path("/app/profile_images")
PROFILE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.post("/me/upload-profile-image")
def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user profile image to local volume"""
    # Validate file extension
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024
    contents = file.file.read()
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    try:
        # Delete old profile image if exists
        if current_user.profile_image:
            old_image_path = PROFILE_IMAGE_DIR / current_user.profile_image
            if old_image_path.exists():
                old_image_path.unlink()
        
        # Generate unique filename
        file_name = f"user_{current_user.id}_{uuid.uuid4()}{file_ext}"
        file_path = PROFILE_IMAGE_DIR / file_name
        
        # Save file to volume
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Update user profile image in database
        current_user.profile_image = file_name
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Profile image uploaded successfully",
            "profile_image": file_name,
            "profile_image_url": f"/api/users/profile-image/{file_name}",
            "user": current_user
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading profile image: {str(e)}"
        )

@router.get("/profile-image/{filename}")
def get_profile_image(filename: str):
    """Serve profile image from local volume"""
    file_path = PROFILE_IMAGE_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile image not found"
        )
    
    # Security check: ensure file is within profile images directory
    if not str(file_path.resolve()).startswith(str(PROFILE_IMAGE_DIR.resolve())):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return FileResponse(file_path)

@router.delete("/me/profile-image")
def delete_profile_image(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user profile image"""
    if not current_user.profile_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile image to delete"
        )
    
    try:
        # Delete file from volume
        file_path = PROFILE_IMAGE_DIR / current_user.profile_image
        if file_path.exists():
            file_path.unlink()
        
        # Update database
        current_user.profile_image = None
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Profile image deleted successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile image: {str(e)}"
        )