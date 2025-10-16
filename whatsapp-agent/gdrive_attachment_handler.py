"""
Google Drive Attachment Handler with Local Caching
Handles downloading and caching files from Google Drive URLs
"""

import os
import re
import json
import hashlib
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GDriveCacheManager:
    """Manages local cache of downloaded Google Drive files"""
    
    def __init__(self, cache_dir: str = "gdrive_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict[str, str]:
        """Load cache index from JSON file"""
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache index: {e}")
                return {}
        return {}
    
    def _save_cache_index(self):
        """Save cache index to JSON file"""
        try:
            with open(self.cache_index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def _get_url_hash(self, url: str) -> str:
        """Generate hash for URL to use as cache key"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_cached_file(self, url: str) -> Optional[Path]:
        """Get cached file path if exists"""
        url_hash = self._get_url_hash(url)
        if url_hash in self.cache_index:
            cached_path = Path(self.cache_index[url_hash])
            if cached_path.exists():
                logger.debug(f"  -> Using cached file for URL: {url[:50]}...")
                return cached_path
            else:
                # Remove invalid cache entry
                logger.debug(f"  -> Cache entry invalid, removing: {cached_path}")
                del self.cache_index[url_hash]
                self._save_cache_index()
        return None
    
    def add_to_cache(self, url: str, file_path: Path) -> Path:
        """Add downloaded file to cache"""
        url_hash = self._get_url_hash(url)
        self.cache_index[url_hash] = str(file_path)
        self._save_cache_index()
        logger.debug(f"  -> Added to cache: {file_path.name}")
        return file_path
    
    def clear_cache(self):
        """Clear all cached files"""
        try:
            for file_path in self.cache_dir.glob("*"):
                if file_path != self.cache_index_file:
                    file_path.unlink()
            self.cache_index = {}
            self._save_cache_index()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")


class GDriveAttachmentHandler:
    """Handles Google Drive file downloads with caching"""
    
    def __init__(self, cache_dir: str = "gdrive_cache"):
        self.cache_manager = GDriveCacheManager(cache_dir)
    
    def _extract_file_id(self, url: str) -> Optional[str]:
        """Extract file ID from various Google Drive URL formats"""
        patterns = [
            r'/file/d/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)',
            r'/d/([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _get_direct_download_url(self, file_id: str) -> str:
        """Convert file ID to direct download URL"""
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    def _get_file_extension(self, url: str, headers: dict) -> str:
        """Determine file extension from URL or content type"""
        # Try to get from URL
        url_lower = url.lower()
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.mp4', '.doc', '.docx']:
            if ext in url_lower:
                return ext[1:]  # Remove the dot
        
        # Try to get from content-type header
        content_type = headers.get('content-type', '').lower()
        ext_map = {
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp',
            'application/pdf': 'pdf',
            'video/mp4': 'mp4',
        }
        
        for ct, ext in ext_map.items():
            if ct in content_type:
                return ext
        
        return 'jpg'  # Default to jpg
    
    def download_file(self, url: str) -> Optional[Path]:
        """Download file from Google Drive URL with caching"""
        # Check cache first
        cached_file = self.cache_manager.get_cached_file(url)
        if cached_file:
            return cached_file
        
        try:
            # Extract file ID
            file_id = self._extract_file_id(url)
            if not file_id:
                logger.error(f"  -> Could not extract file ID from URL: {url}")
                return None
            
            # Get direct download URL
            download_url = self._get_direct_download_url(file_id)
            
            # Download file
            logger.debug(f"  -> Downloading file from Google Drive: {file_id}")
            
            # Create a session to handle redirects and cookies
            session = requests.Session()
            response = session.get(download_url, stream=True, timeout=30)
            
            # Handle Google Drive virus scan warning
            if 'download_warning' in response.text or 'confirm=' in response.text:
                # Extract confirmation token
                for key, value in response.cookies.items():
                    if key.startswith('download_warning'):
                        download_url = f"{download_url}&confirm={value}"
                        response = session.get(download_url, stream=True, timeout=30)
                        break
            
            response.raise_for_status()
            
            # Determine file extension
            extension = self._get_file_extension(url, response.headers)
            
            # Save to cache directory
            file_name = f"{file_id}.{extension}"
            file_path = self.cache_manager.cache_dir / file_name
            
            # Download in chunks
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.debug(f"  -> File downloaded successfully: {file_path.name}")
            
            # Add to cache
            return self.cache_manager.add_to_cache(url, file_path)
            
        except Exception as e:
            logger.error(f"  -> Failed to download file from {url}: {e}")
            return None
    
    def download_multiple(self, urls: List[str]) -> List[Path]:
        """Download multiple files and return list of local paths"""
        downloaded_files = []
        for i, url in enumerate(urls):
            url = url.strip()
            if not url:
                continue
            logger.debug(f"  -> Processing attachment {i+1}/{len(urls)}")
            file_path = self.download_file(url)
            if file_path:
                downloaded_files.append(file_path)
            else:
                logger.warning(f"  -> Failed to download attachment {i+1}: {url[:50]}...")
        return downloaded_files
    
    def parse_attachments_from_message(self, message: str) -> Tuple[str, List[str]]:
        """
        Parse attachments from message text
        Expected format: "Your message text Attachments: [url1, url2, url3]"
        Returns: (clean_message, list_of_urls)
        """
        attachment_pattern = r'Attachments:\s*\[(.*?)\]'
        match = re.search(attachment_pattern, message, re.IGNORECASE | re.DOTALL)
        
        if match:
            # Extract URLs
            urls_string = match.group(1)
            urls = [url.strip() for url in urls_string.split(',') if url.strip()]
            
            # Remove attachments section from message
            clean_message = re.sub(attachment_pattern, '', message, flags=re.IGNORECASE | re.DOTALL).strip()
            
            return clean_message, urls
        
        return message, []
    
    def get_file_type(self, file_path: Path) -> str:
        """
        Determine file type for WhatsApp attachment
        Returns: 'image', 'video', 'document'
        """
        ext = file_path.suffix.lower()
        
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        video_exts = ['.mp4', '.avi', '.mov', '.mkv']
        
        if ext in image_exts:
            return 'image'
        elif ext in video_exts:
            return 'video'
        else:
            return 'document'
