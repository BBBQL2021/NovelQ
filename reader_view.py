# NovelQ - 摸鱼阅读器
# Author: BBBQL2021
# License: GNU General Public License v3.0

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt

class ReaderView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = "light"
        self.scrollbars_visible = True
        self.current_position = 0  # 添加current_position属性
        self.current_chapter_index = 0  # 添加current_chapter_index属性
        self.bookmarks = []  # 添加bookmarks属性
        self.font_size = 12  # 添加font_size属性，设置默认字体大小
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建文本视图
        self.text_view = QTextEdit(self)
        self.text_view.setReadOnly(True)
        self.text_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 添加到布局
        layout.addWidget(self.text_view)
        
        # 设置滚动条样式
        self.update_scrollbar_style()
    
    def update_scrollbar_style(self):
        handle_color = "#888888" if self.theme == "light" else "#666666"
        handle_hover_color = "#666666" if self.theme == "light" else "#888888"
        bg_hover_color = "#f0f0f0" if self.theme == "light" else "#333333"
        bg_color = "#ffffff" if self.theme == "light" else "#1e1e1e"
        text_color = "#000000" if self.theme == "light" else "#ffffff"
        
        # 设置基本样式和滚动条样式
        self.text_view.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")
        
        # 设置滚动条样式
        scrollbar_style = f"""
            QScrollBar:vertical {{width: 8px; background: transparent; margin: 0px; border-radius: 4px;}}
            QScrollBar::handle:vertical {{background: {handle_color}; min-height: 40px; border-radius: 4px; margin: 2px;}}
            QScrollBar::handle:vertical:hover {{background: {handle_hover_color};}}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{height: 0px;}}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{background: transparent;}}
            QScrollBar::add-page:vertical:hover, QScrollBar::sub-page:vertical:hover {{background: {bg_hover_color};}}
            QScrollBar:horizontal {{height: 8px; background: transparent; margin: 0px; border-radius: 4px;}}
            QScrollBar::handle:horizontal {{background: {handle_color}; min-width: 40px; border-radius: 4px; margin: 2px;}}
            QScrollBar::handle:horizontal:hover {{background: {handle_hover_color};}}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{width: 0px;}}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{background: transparent;}}
            QScrollBar::add-page:horizontal:hover, QScrollBar::sub-page:horizontal:hover {{background: {bg_hover_color};}}
        """
        
        # 应用滚动条样式
        self.text_view.verticalScrollBar().setStyleSheet(scrollbar_style)
        self.text_view.horizontalScrollBar().setStyleSheet(scrollbar_style)
        
        self.scrollbars_visible = True
    
    def show_chapters(self):
        # 暂时实现一个空的show_chapters方法
        pass
    def show_bookmarks(self):
        # 暂时实现一个空的show_bookmarks方法
        pass
    def add_bookmark(self):
        # 暂时实现一个空的add_bookmark方法
        pass
    def change_font(self):
        # 暂时实现一个空的change_font方法
        pass
    def prev_page(self):
        # 暂时实现一个空的prev_page方法
        pass

    def change_font_size(self, size):
        """更改文本视图的字体大小"""
        self.font_size = size
        font = self.text_view.font()
        font.setPointSize(size)
        self.text_view.setFont(font)

    def set_content(self, content):
        """设置阅读器的文本内容"""
        self.text_view.setText(content)
    def next_page(self):
        # 暂时实现一个空的next_page方法
        pass
    def set_theme(self, theme_name):
        # 设置主题并更新滚动条样式
        self.theme = theme_name
        # 直接调用update_scrollbar_style，不再单独设置文本视图样式
        self.update_scrollbar_style()
    @property
    def current_theme(self):
        """提供current_theme属性的getter方法，与main.py兼容"""
        return self.theme
        if theme_name == "dark":
            self.text_view.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        else:
            self.text_view.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.update_scrollbar_style()
