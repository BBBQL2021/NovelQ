# NovelQ - 摸鱼阅读器
# Author: BBBQL2021
# License: GNU General Public License v3.0

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class ReadingProgress:
    file_path: str
    position: int
    chapter_index: int

@dataclass
class BookmarkItem:
    position: int
    text: str
    note: Optional[str] = None
    created_time: str = None

@dataclass
class UserPreferences:
    font_family: str = 'Microsoft YaHei'
    font_size: int = 12
    line_spacing: float = 1.5
    theme: str = 'light'
    auto_scroll_interval: int = 50
    novels_dir: str = ''  # 默认小说文件夹路径

class SettingsManager:
    def __init__(self, app_name: str = '小说阅读器'):
        self.app_name = app_name
        self.settings_dir = os.path.join(os.path.expanduser('~'), '.reader_settings')
        self.settings_file = os.path.join(self.settings_dir, 'settings.json')
        self.progress_dir = os.path.join(self.settings_dir, 'progress')
        self.bookmarks_dir = os.path.join(self.settings_dir, 'bookmarks')
        
        # 确保目录存在
        os.makedirs(self.settings_dir, exist_ok=True)
        os.makedirs(self.progress_dir, exist_ok=True)
        os.makedirs(self.bookmarks_dir, exist_ok=True)
        
        # 加载设置
        self.preferences = self.load_preferences()
        self.reading_progress: Dict[str, ReadingProgress] = {}
        self.bookmarks: Dict[str, list[BookmarkItem]] = {}
        
    def load_preferences(self) -> UserPreferences:
        """加载用户偏好设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserPreferences(**data)
            except Exception:
                return UserPreferences()
        return UserPreferences()
    
    def save_preferences(self) -> None:
        """保存用户偏好设置"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.preferences), f, ensure_ascii=False, indent=2)
            
    def get_progress_file(self, file_path: str) -> str:
        """获取进度文件路径"""
        file_hash = str(hash(file_path))
        return os.path.join(self.progress_dir, f'{file_hash}.json')
    
    def save_reading_progress(self, progress: ReadingProgress) -> None:
        """保存阅读进度"""
        progress_file = self.get_progress_file(progress.file_path)
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(progress), f, ensure_ascii=False, indent=2)
        self.reading_progress[progress.file_path] = progress
        
    def load_reading_progress(self, file_path: str) -> Optional[ReadingProgress]:
        """加载阅读进度"""
        progress_file = self.get_progress_file(file_path)
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                progress = ReadingProgress(**data)
                self.reading_progress[file_path] = progress
                return progress
            except Exception:
                return None
        return None
    
    def get_bookmark_file(self, file_path: str) -> str:
        """获取书签文件路径"""
        file_hash = str(hash(file_path))
        return os.path.join(self.bookmarks_dir, f'{file_hash}.json')
    
    def save_bookmarks(self, file_path: str, bookmarks: list[BookmarkItem]) -> None:
        """保存书签"""
        bookmark_file = self.get_bookmark_file(file_path)
        with open(bookmark_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(b) for b in bookmarks], f, ensure_ascii=False, indent=2)
        self.bookmarks[file_path] = bookmarks
        
    def load_bookmarks(self, file_path: str) -> list[BookmarkItem]:
        """加载书签"""
        bookmark_file = self.get_bookmark_file(file_path)
        if os.path.exists(bookmark_file):
            try:
                with open(bookmark_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                bookmarks = [BookmarkItem(**item) for item in data]
                self.bookmarks[file_path] = bookmarks
                return bookmarks
            except Exception:
                return []
        return []
    
    def add_bookmark(self, file_path: str, bookmark: BookmarkItem) -> None:
        """添加书签"""
        bookmarks = self.load_bookmarks(file_path)
        bookmarks.append(bookmark)
        self.save_bookmarks(file_path, bookmarks)
        
    def remove_bookmark(self, file_path: str, position: int) -> None:
        """删除书签"""
        bookmarks = self.load_bookmarks(file_path)
        bookmarks = [b for b in bookmarks if b.position != position]
        self.save_bookmarks(file_path, bookmarks)