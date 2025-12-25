"""
File Analysis Engine for Orca OS.
Detects file types, categories, and patterns.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
import mimetypes
import hashlib

logger = logging.getLogger(__name__)


class FileAnalyzer:
    """Analyzes files for organization."""
    
    def __init__(self):
        """Initialize file analyzer."""
        self.file_extensions = {
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'},
            'videos': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'},
            'audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'},
            'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'},
            'code': {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs'},
            'data': {'.json', '.xml', '.csv', '.yaml', '.yml', '.toml', '.ini'},
            'executables': {'.exe', '.app', '.deb', '.rpm', '.dmg', '.pkg'},
        }
    
    def analyze_directory(self, directory: str) -> Dict[str, Any]:
        """Analyze all files in a directory."""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return {'error': f'Directory not found: {directory}'}
            
            files = []
            categories = defaultdict(list)
            file_types = defaultdict(int)
            total_size = 0
            duplicates = []
            
            # Scan directory
            for item in dir_path.iterdir():
                if item.is_file():
                    file_info = self._analyze_file(item)
                    files.append(file_info)
                    
                    # Categorize
                    category = file_info.get('category', 'other')
                    categories[category].append(file_info)
                    
                    # Count types
                    file_type = file_info.get('type', 'unknown')
                    file_types[file_type] += 1
                    
                    # Size
                    total_size += file_info.get('size', 0)
                    
                    # Check for duplicates (by name and size)
                    duplicates.extend(self._check_duplicates(item, files))
            
            return {
                'directory': str(dir_path),
                'total_files': len(files),
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'categories': dict(categories),
                'file_types': dict(file_types),
                'files': files,
                'duplicates': list(set(duplicates)),
                'organization_suggestions': self._generate_suggestions(categories, file_types)
            }
        except Exception as e:
            logger.error(f"Error analyzing directory: {e}")
            return {'error': str(e)}
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file."""
        try:
            stat = file_path.stat()
            ext = file_path.suffix.lower()
            
            # Determine category
            category = self._categorize_file(ext, file_path.name)
            
            # Determine type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            file_type = mime_type or 'unknown'
            
            # Get file age
            from datetime import datetime
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            age_days = (datetime.now() - modified_time).days
            
            return {
                'name': file_path.name,
                'path': str(file_path),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'extension': ext,
                'category': category,
                'type': file_type,
                'modified': modified_time.isoformat(),
                'age_days': age_days,
                'is_important': self._is_important_file(file_path.name, ext)
            }
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {
                'name': file_path.name,
                'path': str(file_path),
                'error': str(e)
            }
    
    def _categorize_file(self, extension: str, filename: str) -> str:
        """Categorize file by extension and name."""
        filename_lower = filename.lower()
        
        # Check by extension
        for category, exts in self.file_extensions.items():
            if extension in exts:
                return category
        
        # Check by filename patterns
        if any(word in filename_lower for word in ['image', 'photo', 'picture', 'img']):
            return 'images'
        if any(word in filename_lower for word in ['video', 'movie', 'film']):
            return 'videos'
        if any(word in filename_lower for word in ['audio', 'music', 'sound', 'song']):
            return 'audio'
        if any(word in filename_lower for word in ['doc', 'document', 'pdf', 'text']):
            return 'documents'
        if any(word in filename_lower for word in ['code', 'script', 'program']):
            return 'code'
        
        return 'other'
    
    def _is_important_file(self, filename: str, extension: str) -> bool:
        """Determine if file is important (AI-powered heuristic)."""
        filename_lower = filename.lower()
        
        # Important patterns
        important_keywords = [
            'important', 'critical', 'backup', 'save', 'final', 'master',
            'config', 'settings', 'password', 'key', 'certificate'
        ]
        
        if any(keyword in filename_lower for keyword in important_keywords):
            return True
        
        # Important extensions
        important_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
        if extension in important_extensions:
            return True
        
        return False
    
    def _check_duplicates(self, file_path: Path, existing_files: List[Dict[str, Any]]) -> List[str]:
        """Check for duplicate files (by name)."""
        duplicates = []
        filename = file_path.name.lower()
        
        for existing in existing_files:
            if existing['name'].lower() == filename and existing['path'] != str(file_path):
                duplicates.append(existing['path'])
                duplicates.append(str(file_path))
        
        return duplicates
    
    def _generate_suggestions(self, categories: Dict, file_types: Dict) -> List[str]:
        """Generate organization suggestions."""
        suggestions = []
        
        # Suggest organizing by category
        if len(categories) > 3:
            suggestions.append(f"Organize {len(categories)} different file categories into folders")
        
        # Suggest organizing large files
        total_files = sum(len(files) for files in categories.values())
        if total_files > 20:
            suggestions.append(f"Many files ({total_files}) - consider organizing by category")
        
        # Suggest organizing by type
        if len(file_types) > 5:
            suggestions.append(f"Multiple file types detected - organize by type")
        
        return suggestions

