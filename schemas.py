# from pydantic import BaseModel, EmailStr, Field
# from datetime import datetime
# from typing import Optional

# # User Schemas
# class UserCreate(BaseModel):
#     username: str = Field(..., min_length=3, max_length=50)
#     email: EmailStr
#     password: str = Field(..., min_length=8)
#     full_name: Optional[str] = None

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# class UserResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#     full_name: Optional[str]
#     profile_image: Optional[str]
#     bio: Optional[str]=None
#     is_active: bool
#     role: str
#     created_at: datetime
    
#     class Config:
#         from_attributes = True


# class UserProfileUpdate(BaseModel):
#     full_name: Optional[str] = Field(None, max_length=255)
#     bio: Optional[str] = Field(None, max_length=500)
#     username: Optional[str] = Field(None, min_length=3, max_length=50)

# class TokenResponse(BaseModel):
#     access_token: str
#     user_data: UserResponse
#     token_type: str = "bearer"

# # Video Schemas
# class VideoCreate(BaseModel):
#     title: str = Field(..., min_length=1, max_length=255)
#     description: Optional[str] = Field(None, max_length=1000)
#     is_public: bool = True

# class VideoUpdate(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     is_public: Optional[bool] = None

# class VideoResponse(BaseModel):
#     id: int
#     title: str
#     description: Optional[str]
#     file_name: str
#     file_size: int
#     duration: Optional[float]
#     video_url:str
#     width: Optional[int]
#     height: Optional[int]
#     view_count: int
#     like_count: int
#     comment_count: int
#     share_count: int
#     is_public: bool
#     is_processed: bool
#     thumbnail_path: Optional[str]
#     created_at: datetime
#     uploader: UserResponse
    
#     class Config:
#         from_attributes = True

# class VideoListResponse(BaseModel):
#     total: int
#     skip: int
#     limit: int
#     videos: list[VideoResponse]

# class UploadProgress(BaseModel):
#     video_id: int
#     uploaded_bytes: int
#     total_bytes: int
#     percentage: float

# class LikeResponse(BaseModel):
#     id: int
#     user_id: int
#     video_id: int
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# class CommentCreate(BaseModel):
#     content: str = Field(..., min_length=1, max_length=500)

# class CommentResponse(BaseModel):
#     id: int
#     user_id: int
#     video_id: int
#     content: str
#     created_at: datetime
#     user: UserResponse
    
#     class Config:
#         from_attributes = True

# class ShareResponse(BaseModel):
#     id: int
#     user_id: int
#     video_id: int
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# class FavoriteResponse(BaseModel):
#     id: int
#     user_id: int
#     video_id: int
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# class PlaylistCreate(BaseModel):
#     title: str = Field(..., min_length=1, max_length=255)
#     description: Optional[str] = Field(None, max_length=1000)
#     is_public: bool = True

# class PlaylistUpdate(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     is_public: Optional[bool] = None

# class PlaylistResponse(BaseModel):
#     id: int
#     creator_id: int
#     title: str
#     description: Optional[str]
#     is_public: bool
#     created_at: datetime
#     updated_at: datetime
    
#     class Config:
#         from_attributes = True

# class PlaylistDetailResponse(PlaylistResponse):
#     videos: list[VideoResponse]



from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    profile_image: Optional[str]
    bio: Optional[str]=None
    is_active: bool
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    username: Optional[str] = Field(None, min_length=3, max_length=50)

class TokenResponse(BaseModel):
    access_token: str
    user_data: UserResponse
    token_type: str = "bearer"

# Video Schemas
class VideoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_public: bool = True

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class VideoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    file_name: str
    file_size: int
    video_url:Optional[str]=None
    duration: Optional[float]
    width: Optional[int]
    height: Optional[int]
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    is_public: bool
    is_processed: bool
    thumbnail_path: Optional[str]
    created_at: datetime
    uploader: UserResponse
    
    class Config:
        from_attributes = True

class VideoListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    videos: list[VideoResponse] = None

class UploadProgress(BaseModel):
    video_id: int
    uploaded_bytes: int
    total_bytes: int
    percentage: float

class LikeResponse(BaseModel):
    id: int
    user_id: int
    video_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

class CommentResponse(BaseModel):
    id: int
    user_id: int
    video_id: int
    content: str
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True

class ShareResponse(BaseModel):
    id: int
    user_id: int
    video_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    video_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlaylistCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_public: bool = True

class PlaylistUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class PlaylistResponse(BaseModel):
    id: int
    creator_id: int
    title: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PlaylistDetailResponse(PlaylistResponse):
    videos: list[VideoResponse]

class LikeDetailResponse(BaseModel):
    """Detailed like response with video information"""
    id: int
    user_id: int
    video_id: int
    created_at: datetime
    video: VideoResponse
    
    class Config:
        from_attributes = True

class CommentDetailResponse(BaseModel):
    """Detailed comment response"""
    id: int
    user_id: int
    video_id: int
    content: str
    created_at: datetime
    user: UserResponse
    video: VideoResponse
    
    class Config:
        from_attributes = True

class ShareDetailResponse(BaseModel):
    """Detailed share response with video information"""
    id: int
    user_id: int
    video_id: int
    created_at: datetime
    video: VideoResponse
    
    class Config:
        from_attributes = True

class FavoriteDetailResponse(BaseModel):
    """Detailed favorite response with video information"""
    id: int
    user_id: int
    video_id: int
    created_at: datetime
    video: VideoResponse
    
    class Config:
        from_attributes = True

class VideoSearchResponse(BaseModel):
    """Video search result"""
    id: int
    title: str
    description: Optional[str]
    file_name: str
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    created_at: datetime
    uploader: UserResponse
    
    class Config:
        from_attributes = True

class VideoSearchListResponse(BaseModel):
    """Search results with pagination"""
    total: int
    skip: int
    limit: int
    query: str
    videos: list[VideoSearchResponse]
