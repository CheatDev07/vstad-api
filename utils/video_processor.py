import subprocess
import os
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    @staticmethod
    def get_video_duration(file_path: str) -> Optional[float]:
        """Get video duration in seconds using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1:noescapevalues=1',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            duration = float(result.stdout.strip())
            return duration
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return None
    
    @staticmethod
    def get_video_metadata(file_path: str) -> dict:
        """Get comprehensive video metadata"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,r_frame_rate,codec_name',
                '-show_entries', 'format=duration',
                '-of', 'json',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            import json
            data = json.loads(result.stdout)
            
            metadata = {
                'duration': float(data['format'].get('duration', 0)),
                'width': None,
                'height': None,
                'fps': None,
                'codec': None,
            }
            
            if data['streams']:
                stream = data['streams'][0]
                metadata['width'] = stream.get('width')
                metadata['height'] = stream.get('height')
                metadata['codec'] = stream.get('codec_name')
                
                # Calculate FPS
                if 'r_frame_rate' in stream:
                    parts = stream['r_frame_rate'].split('/')
                    if len(parts) == 2:
                        metadata['fps'] = float(parts[0]) / float(parts[1])
            
            return metadata
        except Exception as e:
            logger.error(f"Error getting video metadata: {e}")
            return {}
    
    @staticmethod
    def generate_thumbnail(video_path: str, output_path: str, timestamp: str = "00:00:01") -> bool:
        """Generate thumbnail from video at specific timestamp"""
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', timestamp,
                '-vframes', '1',
                '-vf', 'scale=320:180',
                '-y',
                output_path
            ]
            subprocess.run(cmd, capture_output=True, timeout=10)
            return os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return False
    
    @staticmethod
    def validate_video_file(file_path: str, allowed_formats: list) -> Tuple[bool, str]:
        """Validate video file format and integrity"""
        try:
            # Check file extension
            ext = Path(file_path).suffix.lower().lstrip('.')
            if ext not in allowed_formats:
                return False, f"Invalid format. Allowed: {', '.join(allowed_formats)}"
            
            # Verify video is readable with ffmpeg
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_type',
                '-of', 'csv=p=0',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if 'video' not in result.stdout:
                return False, "File is not a valid video"
            
            return True, "Video is valid"
        except Exception as e:
            return False, str(e)

# Global instance
video_processor = VideoProcessor()
