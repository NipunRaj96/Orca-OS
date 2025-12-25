"""
File Organization Engine for Orca OS.
Intelligently organizes files into folders.
"""

import logging
import shutil
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .analyzer import FileAnalyzer

logger = logging.getLogger(__name__)


class FileOrganizer:
    """Organizes files intelligently."""
    
    def __init__(self):
        """Initialize file organizer."""
        self.analyzer = FileAnalyzer()
        self.organization_history = []
    
    def organize_directory(
        self,
        directory: str,
        strategy: str = 'category',
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Organize files in a directory."""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return {'error': f'Directory not found: {directory}'}
            
            # Analyze directory first
            analysis = self.analyzer.analyze_directory(directory)
            if 'error' in analysis:
                return analysis
            
            # Organize based on strategy
            if strategy == 'category':
                return self._organize_by_category(dir_path, analysis, dry_run)
            elif strategy == 'type':
                return self._organize_by_type(dir_path, analysis, dry_run)
            elif strategy == 'date':
                return self._organize_by_date(dir_path, analysis, dry_run)
            else:
                return {'error': f'Unknown strategy: {strategy}'}
        
        except Exception as e:
            logger.error(f"Error organizing directory: {e}")
            return {'error': str(e)}
    
    def _organize_by_category(
        self,
        dir_path: Path,
        analysis: Dict[str, Any],
        dry_run: bool
    ) -> Dict[str, Any]:
        """Organize files by category."""
        categories = analysis.get('categories', {})
        actions = []
        created_folders = set()
        
        for category, files in categories.items():
            if not files:
                continue
            
            # Create category folder
            category_folder = dir_path / category.capitalize()
            if category_folder not in created_folders:
                if not dry_run:
                    category_folder.mkdir(exist_ok=True)
                created_folders.add(category_folder)
                actions.append({
                    'action': 'create_folder',
                    'path': str(category_folder),
                    'category': category
                })
            
            # Move files
            for file_info in files:
                file_path = Path(file_info['path'])
                dest_path = category_folder / file_path.name
                
                # Skip if already in correct location
                if file_path.parent == category_folder:
                    continue
                
                # Check for name conflicts
                if dest_path.exists():
                    # Add timestamp to filename
                    stem = file_path.stem
                    suffix = file_path.suffix
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_path = category_folder / f"{stem}_{timestamp}{suffix}"
                
                if not dry_run:
                    try:
                        shutil.move(str(file_path), str(dest_path))
                        actions.append({
                            'action': 'move',
                            'from': str(file_path),
                            'to': str(dest_path),
                            'success': True
                        })
                    except Exception as e:
                        actions.append({
                            'action': 'move',
                            'from': str(file_path),
                            'to': str(dest_path),
                            'success': False,
                            'error': str(e)
                        })
                else:
                    actions.append({
                        'action': 'move',
                        'from': str(file_path),
                        'to': str(dest_path),
                        'dry_run': True
                    })
        
        return {
            'strategy': 'category',
            'dry_run': dry_run,
            'total_files': analysis.get('total_files', 0),
            'categories_created': len(created_folders),
            'files_moved': len([a for a in actions if a['action'] == 'move']),
            'actions': actions,
            'summary': f"Organized {len([a for a in actions if a['action'] == 'move'])} files into {len(created_folders)} category folders"
        }
    
    def _organize_by_type(
        self,
        dir_path: Path,
        analysis: Dict[str, Any],
        dry_run: bool
    ) -> Dict[str, Any]:
        """Organize files by file type/extension."""
        files = analysis.get('files', [])
        type_groups = {}
        
        # Group by extension
        for file_info in files:
            ext = file_info.get('extension', 'no_extension')
            if ext not in type_groups:
                type_groups[ext] = []
            type_groups[ext].append(file_info)
        
        actions = []
        created_folders = set()
        
        for ext, file_list in type_groups.items():
            if not file_list:
                continue
            
            # Create type folder
            folder_name = ext[1:].upper() if ext else 'NoExtension'
            type_folder = dir_path / folder_name
            if type_folder not in created_folders:
                if not dry_run:
                    type_folder.mkdir(exist_ok=True)
                created_folders.add(type_folder)
                actions.append({
                    'action': 'create_folder',
                    'path': str(type_folder),
                    'type': ext
                })
            
            # Move files
            for file_info in file_list:
                file_path = Path(file_info['path'])
                dest_path = type_folder / file_path.name
                
                if file_path.parent == type_folder:
                    continue
                
                if dest_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_path = type_folder / f"{stem}_{timestamp}{suffix}"
                
                if not dry_run:
                    try:
                        shutil.move(str(file_path), str(dest_path))
                        actions.append({
                            'action': 'move',
                            'from': str(file_path),
                            'to': str(dest_path),
                            'success': True
                        })
                    except Exception as e:
                        actions.append({
                            'action': 'move',
                            'from': str(file_path),
                            'to': str(dest_path),
                            'success': False,
                            'error': str(e)
                        })
                else:
                    actions.append({
                        'action': 'move',
                        'from': str(file_path),
                        'to': str(dest_path),
                        'dry_run': True
                    })
        
        return {
            'strategy': 'type',
            'dry_run': dry_run,
            'total_files': len(files),
            'folders_created': len(created_folders),
            'files_moved': len([a for a in actions if a['action'] == 'move']),
            'actions': actions,
            'summary': f"Organized {len([a for a in actions if a['action'] == 'move'])} files by type into {len(created_folders)} folders"
        }
    
    def _organize_by_date(
        self,
        dir_path: Path,
        analysis: Dict[str, Any],
        dry_run: bool
    ) -> Dict[str, Any]:
        """Organize files by date (year/month)."""
        files = analysis.get('files', [])
        date_groups = {}
        
        # Group by year-month
        for file_info in files:
            try:
                modified = datetime.fromisoformat(file_info.get('modified', ''))
                year_month = modified.strftime('%Y-%m')
                if year_month not in date_groups:
                    date_groups[year_month] = []
                date_groups[year_month].append(file_info)
            except:
                # Use current date if can't parse
                year_month = datetime.now().strftime('%Y-%m')
                if year_month not in date_groups:
                    date_groups[year_month] = []
                date_groups[year_month].append(file_info)
        
        actions = []
        created_folders = set()
        
        for year_month, file_list in date_groups.items():
            if not file_list:
                continue
            
            # Create date folder
            date_folder = dir_path / year_month
            if date_folder not in created_folders:
                if not dry_run:
                    date_folder.mkdir(exist_ok=True)
                created_folders.add(date_folder)
                actions.append({
                    'action': 'create_folder',
                    'path': str(date_folder),
                    'date': year_month
                })
            
            # Move files
            for file_info in file_list:
                file_path = Path(file_info['path'])
                dest_path = date_folder / file_path.name
                
                if file_path.parent == date_folder:
                    continue
                
                if dest_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_path = date_folder / f"{stem}_{timestamp}{suffix}"
                
                if not dry_run:
                    try:
                        shutil.move(str(file_path), str(dest_path))
                        actions.append({
                            'action': 'move',
                            'from': str(file_path),
                            'to': str(dest_path),
                            'success': True
                        })
                    except Exception as e:
                        actions.append({
                            'action': 'move',
                            'from': str(file_path),
                            'to': str(dest_path),
                            'success': False,
                            'error': str(e)
                        })
                else:
                    actions.append({
                        'action': 'move',
                        'from': str(file_path),
                        'to': str(dest_path),
                        'dry_run': True
                    })
        
        return {
            'strategy': 'date',
            'dry_run': dry_run,
            'total_files': len(files),
            'folders_created': len(created_folders),
            'files_moved': len([a for a in actions if a['action'] == 'move']),
            'actions': actions,
            'summary': f"Organized {len([a for a in actions if a['action'] == 'move'])} files by date into {len(created_folders)} folders"
        }
    
    def preview_organization(self, directory: str, strategy: str = 'category') -> Dict[str, Any]:
        """Preview organization without actually moving files."""
        return self.organize_directory(directory, strategy, dry_run=True)

