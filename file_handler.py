# NovelQ - 摸鱼阅读器
# Author: BBBQL2021
# License: GNU General Public License v3.0

import os
import re
import chardet
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional, Any

class FileHandler:
    def __init__(self):
        self.current_file = None
        self.content = None
        self.encoding = None
        self.file_type = None
        self.metadata = {}
        self.chapters = []
        
    def open_file(self, file_path: str) -> str:
        """打开并读取文件内容"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")
            
        self.current_file = file_path
        self.file_type = os.path.splitext(file_path)[1].lower()
        
        if self.file_type == '.txt':
            return self._read_txt(file_path)
        elif self.file_type == '.epub':
            return self._read_epub(file_path)
        elif self.file_type == '.pdf':
            return self._read_pdf(file_path)
        else:
            raise ValueError(f"不支持的文件格式：{self.file_type}")
    
    def _read_txt(self, file_path: str) -> str:
        """读取TXT文件，自动检测编码"""
        # 检测文件编码
        with open(file_path, 'rb') as f:
            raw_data = f.read(min(1024*1024, os.path.getsize(file_path)))  # 读取最多1MB用于检测编码
            result = chardet.detect(raw_data)
            self.encoding = result['encoding']
            confidence = result['confidence']
        
        # 使用检测到的编码读取文件
        try:
            if confidence > 0.7 and self.encoding:
                with open(file_path, 'r', encoding=self.encoding) as f:
                    self.content = f.read()
                return self.content
            else:
                # 如果检测的编码不可靠，尝试常用编码
                return self._try_multiple_encodings(file_path)
        except UnicodeDecodeError:
            # 如果检测的编码不正确，尝试常用编码
            return self._try_multiple_encodings(file_path)
            
    def _try_multiple_encodings(self, file_path: str) -> str:
        """尝试多种编码读取文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'utf-16', 'utf-16-le', 'utf-16-be', 'ascii']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    self.content = f.read()
                    self.encoding = encoding
                    return self.content
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"无法正确解码文件：{file_path}")
    
    def _read_epub(self, file_path: str) -> str:
        """读取EPUB文件"""
        try:
            book = epub.read_epub(file_path)
            content = []
            self.chapters = []
            chapter_index = 0
            
            # 提取元数据
            self.metadata = {
                'title': book.get_metadata('DC', 'title'),
                'creator': book.get_metadata('DC', 'creator'),
                'language': book.get_metadata('DC', 'language'),
                'publisher': book.get_metadata('DC', 'publisher'),
                'identifier': book.get_metadata('DC', 'identifier')
            }
            
            # 提取封面
            for item in book.get_items_of_type(ebooklib.ITEM_COVER):
                self.metadata['cover'] = item
            
            # 提取目录和内容
            toc = book.toc
            if toc:
                for item in toc:
                    if isinstance(item, tuple):
                        section_title, section_href = item[0].title, item[0].href
                        chapter = {
                            'title': section_title,
                            'start': len('\n'.join(content)),
                            'content': []
                        }
                        self.chapters.append(chapter)
            
            # 提取文本内容
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # 解析HTML内容
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    
                    # 移除脚本和样式
                    for script in soup(["script", "style"]):
                        script.extract()
                    
                    text = soup.get_text()
                    if text.strip():
                        content.append(text)
                        
                        # 如果没有目录，尝试从内容中识别章节
                        if not self.chapters:
                            chapter_title = self._extract_chapter_title(text)
                            if chapter_title:
                                chapter = {
                                    'title': chapter_title,
                                    'start': len('\n'.join(content[:len(content)-1])),
                                    'content': [text]
                                }
                                self.chapters.append(chapter)
                            elif len(self.chapters) > 0:
                                self.chapters[-1]['content'].append(text)
            
            self.content = '\n'.join(content)
            return self.content
        except Exception as e:
            raise ValueError(f"无法解析EPUB文件：{str(e)}")
    
    def _read_pdf(self, file_path: str) -> str:
        """读取PDF文件"""
        try:
            # 动态导入PyMuPDF，避免不必要的依赖
            import fitz
            
            doc = fitz.open(file_path)
            content = []
            self.chapters = []
            
            # 提取元数据
            self.metadata = {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'keywords': doc.metadata.get('keywords', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'page_count': len(doc)
            }
            
            # 提取目录
            toc = doc.get_toc()
            if toc:
                for level, title, page in toc:
                    chapter = {
                        'title': title,
                        'start': page,
                        'level': level,
                        'content': []
                    }
                    self.chapters.append(chapter)
            
            # 提取文本内容
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    content.append(text)
                    
                    # 如果没有目录，尝试从内容中识别章节
                    if not self.chapters:
                        chapter_title = self._extract_chapter_title(text)
                        if chapter_title:
                            chapter = {
                                'title': chapter_title,
                                'start': len('\n'.join(content[:len(content)-1])),
                                'page': page_num,
                                'content': [text]
                            }
                            self.chapters.append(chapter)
                        elif len(self.chapters) > 0:
                            self.chapters[-1]['content'].append(text)
            
            self.content = '\n'.join(content)
            return self.content
        except ImportError:
            raise ImportError("需要安装PyMuPDF库来支持PDF文件。请运行：pip install pymupdf")
        except Exception as e:
            raise ValueError(f"无法解析PDF文件：{str(e)}")
    
    def _extract_chapter_title(self, text: str) -> Optional[str]:
        """从文本中提取章节标题"""
        # 常见的章节标记模式
        patterns = [
            r'^\s*第\s*[一二三四五六七八九十百千万零\d]+\s*[章节卷集部篇]\s*[：:\s]+(.+)$',  # 中文章节（第一章：标题）
            r'^\s*Chapter\s*\d+\s*[:\s]+(.+)$',  # 英文章节（Chapter 1: Title）
            r'^\s*CHAPTER\s*\d+\s*[:\s]+(.+)$',  # 英文章节大写
            r'^\s*\d+\.\s+(.+)$'  # 数字编号（1. 标题）
        ]
        
        # 检查文本的前几行
        lines = text.split('\n')[:5]  # 只检查前5行
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    return line
        
        return None
    
    def get_chapters(self) -> List[Dict]:
        """获取章节结构"""
        if not self.content:
            return []
            
        # 如果已经解析了章节，直接返回
        if self.chapters:
            return self.chapters
            
        # 否则尝试从内容中识别章节
        chapter_patterns = [
            r'第[一二三四五六七八九十百千万零\d]+[章节卷集部篇]',  # 中文章节（第一章）
            r'Chapter\s*\d+',  # 英文章节（Chapter 1）
            r'CHAPTER\s*\d+',  # 英文章节大写
            r'\d+\.\s+\w+'  # 数字编号（1. 标题）
        ]
        
        chapters = []
        lines = self.content.split('\n')
        
        current_chapter = {'title': '开始', 'start': 0, 'content': []}
        chapters.append(current_chapter)
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是章节标题
            is_chapter = False
            for pattern in chapter_patterns:
                if re.match(pattern, line):
                    is_chapter = True
                    break
            
            if is_chapter:
                # 开始新章节
                current_chapter = {
                    'title': line,
                    'start': i,
                    'content': [line]
                }
                chapters.append(current_chapter)
            else:
                if chapters:  # 确保有章节
                    chapters[-1]['content'].append(line)
        
        self.chapters = chapters
        return chapters
    
    def get_metadata(self) -> Dict:
        """获取文件元数据"""
        return self.metadata
    
    def get_encoding(self) -> str:
        """获取文件编码"""
        return self.encoding or 'unknown'
    
    def get_file_type(self) -> str:
        """获取文件类型"""
        return self.file_type or 'unknown'
        
        # 添加最后一个章节
        if current_chapter['content']:
            chapters.append(current_chapter)
            
        return chapters