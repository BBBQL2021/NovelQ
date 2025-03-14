# NovelQ - 摸鱼阅读器
# Author: BBBQL2021
# License: GNU General Public License v3.0

import sys
import os
import chardet
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QMenuBar, QStatusBar, QToolBar, QFileDialog, QSizePolicy,
                             QComboBox, QSlider, QSpinBox, QLabel, QHBoxLayout, QDialog, QDialogButtonBox)
from PyQt6.QtGui import QAction, QKeySequence, QShortcut, QIcon, QCursor
from PyQt6.QtCore import Qt
from reader_view import ReaderView
from settings import SettingsManager

class AdjustmentDialog(QDialog):
    def __init__(self, parent=None, title="调整", value=0, min_value=0, max_value=100, step=1):
        super().__init__(parent)
        self.setWindowTitle(title)
        
        layout = QVBoxLayout(self)
        
        # 创建水平布局用于放置标签和数值输入框
        input_layout = QHBoxLayout()
        
        # 添加标签
        self.label = QLabel(f"{title}值:")
        input_layout.addWidget(self.label)
        
        # 添加数值输入框
        self.spin_box = QSpinBox()
        self.spin_box.setRange(min_value, max_value)
        self.spin_box.setValue(value)
        self.spin_box.setSingleStep(step)
        input_layout.addWidget(self.spin_box)
        
        # 添加滑块
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_value, max_value)
        self.slider.setValue(value)
        self.slider.setSingleStep(step)
        
        # 连接滑块和数值输入框
        self.slider.valueChanged.connect(self.spin_box.setValue)
        self.spin_box.valueChanged.connect(self.slider.setValue)
        
        # 添加到主布局
        layout.addLayout(input_layout)
        layout.addWidget(self.slider)
        
        # 添加确定和取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_value(self):
        return self.spin_box.value()

class ReaderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("摸鱼阅读器")
        # 设置更小的最小尺寸，允许窗口更自由地缩放
        self.setMinimumSize(200, 150)
        self.current_file = None
        # 设置应用图标 - 使用绝对路径确保任务栏图标正确显示
        import os
        icon_path = os.path.abspath('ikun.ico')
        self.setWindowIcon(QIcon(icon_path))
        
        # 设置窗口样式
        self.setStyleSheet("""QMainWindow {
                border: none;
                background-color: #FFFFFF;
            }
            QMenuBar {
                background-color: #FFFFFF;
                color: #000000;
                border: none;
            }
            QMenuBar::item:selected {
                background-color: #E8E8E8;
            }
            QToolBar {
                background-color: #FFFFFF;
                border: none;
                padding: 2px;
            }
            QStatusBar {
                background-color: #FFFFFF;
                color: #000000;
                border: none;
            }
            QMenu {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #E8E8E8;
            }
            QMenu::item:selected {
                background-color: #E8E8E8;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #FFFFFF;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #1E90FF;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
        
        # 确保窗口可以自由调整大小
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 初始化设置管理器
        self.settings_manager = SettingsManager()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(central_widget)
        
        # 创建阅读视图
        self.reader_view = ReaderView(self)
        self.main_layout.addWidget(self.reader_view)
        
        # 初始化UI组件
        self.init_ui()
        
        # 初始化快捷键
        self.init_shortcuts()
        
        # 初始化无边框模式状态
        self.frameless_mode = False
        
        # 用于跟踪鼠标事件的变量
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_edge = None
        self.resize_start_geometry = None
        
    def init_shortcuts(self):
        """初始化快捷键"""
        # 添加ESC键退出无边框模式的快捷键
        self.esc_shortcut = QShortcut(QKeySequence('Esc'), self)
        self.esc_shortcut.activated.connect(lambda: self.toggle_frameless_mode(False) if self.frameless_mode else None)
        
    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于无边框模式下的窗口移动和调整大小"""
        if not self.frameless_mode:
            super().mousePressEvent(event)
            return
            
        # 窗口边缘的检测范围（像素）
        edge_size = 8
        pos = event.position()
        x, y = pos.x(), pos.y()
        width, height = self.width(), self.height()
        
        # 更新鼠标样式
        cursor_pos = QCursor.pos()
        self.update_cursor_shape(cursor_pos)
        
        # 检测是否在窗口边缘，用于调整大小
        if x <= edge_size and y <= edge_size:  # 左上角
            self.resizing = True
            self.resize_edge = 'top-left'
        elif x >= width - edge_size and y <= edge_size:  # 右上角
            self.resizing = True
            self.resize_edge = 'top-right'
        elif x <= edge_size and y >= height - edge_size:  # 左下角
            self.resizing = True
            self.resize_edge = 'bottom-left'
        elif x >= width - edge_size and y >= height - edge_size:  # 右下角
            self.resizing = True
            self.resize_edge = 'bottom-right'
        elif x <= edge_size:  # 左边
            self.resizing = True
            self.resize_edge = 'left'
        elif x >= width - edge_size:  # 右边
            self.resizing = True
            self.resize_edge = 'right'
        elif y <= edge_size:  # 上边
            self.resizing = True
            self.resize_edge = 'top'
        elif y >= height - edge_size:  # 下边
            self.resizing = True
            self.resize_edge = 'bottom'
        else:  # 窗口内部，用于移动窗口
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
        if self.resizing:
            self.resize_start_geometry = self.geometry()
            
    def update_cursor_shape(self, pos):
        """根据鼠标位置更新光标形状"""
        if not self.frameless_mode:
            return
            
        edge_size = 8
        x = pos.x() - self.x()
        y = pos.y() - self.y()
        width = self.width()
        height = self.height()
        
        if x <= edge_size and y <= edge_size:  # 左上角
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif x >= width - edge_size and y <= edge_size:  # 右上角
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif x <= edge_size and y >= height - edge_size:  # 左下角
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif x >= width - edge_size and y >= height - edge_size:  # 右下角
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif x <= edge_size or x >= width - edge_size:  # 左右边
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif y <= edge_size or y >= height - edge_size:  # 上下边
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，实现窗口移动和调整大小"""
        if not self.frameless_mode:
            super().mouseMoveEvent(event)
            return
            
        # 更新鼠标样式
        cursor_pos = QCursor.pos()
        self.update_cursor_shape(cursor_pos)
            
        if self.dragging:
            # 移动窗口
            self.move(event.globalPosition().toPoint() - self.drag_position)
        elif self.resizing:
            # 调整窗口大小
            new_geo = self.geometry()
            pos = event.globalPosition().toPoint()
            
            if 'left' in self.resize_edge:
                width_diff = self.resize_start_geometry.left() - pos.x()
                if self.resize_start_geometry.width() + width_diff >= self.minimumWidth():
                    new_geo.setLeft(pos.x())
                    
            if 'right' in self.resize_edge:
                new_geo.setRight(pos.x())
                
            if 'top' in self.resize_edge:
                height_diff = self.resize_start_geometry.top() - pos.y()
                if self.resize_start_geometry.height() + height_diff >= self.minimumHeight():
                    new_geo.setTop(pos.y())
                    
            if 'bottom' in self.resize_edge:
                new_geo.setBottom(pos.y())
                
            self.setGeometry(new_geo)
            
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件，重置拖动和调整大小状态"""
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        super().mouseReleaseEvent(event)
        
    def toggle_frameless_mode(self, enter_mode=None):
        """切换无边框模式"""
        if enter_mode is not None:
            self.frameless_mode = enter_mode
        else:
            self.frameless_mode = not self.frameless_mode
            
        if self.frameless_mode:
            # 保存当前窗口状态和几何信息
            self.previous_state = self.windowState()
            self.previous_geometry = self.geometry()
            # 设置无边框和保持在最顶层，同时保持调整大小功能
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            # 隐藏菜单栏、工具栏和状态栏
            self.menuBar().hide()
            self.toolbar.hide()
            self.statusBar().hide()
            # 确保窗口可以调整大小
            self.setMinimumSize(100, 100)
            # 设置无边框模式下的样式 - 根据当前主题设置边框颜色
            theme = self.reader_view.current_theme
            border_color = "#FFFFFF" if theme == "light" else "#1E1F22" if theme == "dark" else "#F4ECD8" if theme == "sepia" else "#E2EFDA" if theme == "green" else "#E0ECF9"
            self.setStyleSheet(f"""
                QMainWindow {{
                    border: none;
                    background-color: {border_color};
                }}
            """)
            # 如果之前是最大化状态，恢复最大化
            if self.previous_state & Qt.WindowState.WindowMaximized:
                self.showMaximized()
            else:
                self.show()
                # 恢复之前的几何信息
                self.setGeometry(self.previous_geometry)
        else:
            # 恢复窗口边框和原始最小尺寸
            self.setWindowFlags(Qt.WindowType.Window)
            self.setMinimumSize(200, 150)
            # 恢复原始样式
            self.setStyleSheet("""
                QMainWindow {
                    border: none;
                    background-color: #FFFFFF;
                }
                QMenuBar {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: none;
                }
                QMenuBar::item:selected {
                    background-color: #E8E8E8;
                }
                QToolBar {
                    background-color: #FFFFFF;
                    border: none;
                    padding: 2px;
                }
                QStatusBar {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: none;
                }
                QMenu {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #E8E8E8;
                }
                QMenu::item:selected {
                    background-color: #E8E8E8;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #999999;
                    height: 8px;
                    background: #FFFFFF;
                    margin: 2px 0;
                }
                QSlider::handle:horizontal {
                    background: #1E90FF;
                    border: 1px solid #5c5c5c;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 3px;
                }
            """)
            # 显示菜单栏、工具栏和状态栏
            self.menuBar().show()
            # 重新创建工具栏
            self.toolbar.clear()
            
            # 重新添加小说选择下拉框
            self.novel_selector = QComboBox()
            self.novel_selector.setMinimumWidth(200)
            self.novel_selector.currentIndexChanged.connect(self.on_novel_selected)
            self.toolbar.addWidget(self.novel_selector)
            self.update_novel_list()
            
            # 重新添加翻页按钮
            prev_page_action = QAction('上一页', self)
            prev_page_action.triggered.connect(self.reader_view.prev_page)
            self.toolbar.addAction(prev_page_action)
            
            next_page_action = QAction('下一页', self)
            next_page_action.triggered.connect(self.reader_view.next_page)
            self.toolbar.addAction(next_page_action)
            
            # 重新添加自动滚动按钮
            auto_scroll_action = QAction('自动滚动', self)
            auto_scroll_action.setCheckable(True)
            auto_scroll_action.triggered.connect(lambda checked: self.reader_view.toggle_auto_scroll())
            self.toolbar.addAction(auto_scroll_action)
            
            self.toolbar.show()
            self.statusBar().show()
            # 恢复之前的窗口状态
            if self.previous_state & Qt.WindowState.WindowMaximized:
                self.showMaximized()
            else:
                self.show()
                # 恢复之前的几何信息
                self.setGeometry(self.previous_geometry)
        
    def init_ui(self):
        """初始化UI组件"""
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        open_action = QAction('打开', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # 添加从默认文件夹打开的选项
        open_from_dir_action = QAction('从默认文件夹打开', self)
        open_from_dir_action.triggered.connect(self.open_from_novels_dir)
        file_menu.addAction(open_from_dir_action)
        
        # 添加设置默认文件夹的选项
        set_novels_dir_action = QAction('设置默认文件夹', self)
        set_novels_dir_action.triggered.connect(self.set_novels_dir)
        file_menu.addAction(set_novels_dir_action)
        
        # 导航菜单
        nav_menu = menubar.addMenu('导航')
        
        chapter_action = QAction('章节列表', self)
        chapter_action.triggered.connect(self.reader_view.show_chapters)
        nav_menu.addAction(chapter_action)
        
        bookmark_action = QAction('书签管理', self)
        bookmark_action.triggered.connect(self.reader_view.show_bookmarks)
        nav_menu.addAction(bookmark_action)
        
        add_bookmark_action = QAction('添加书签', self)
        add_bookmark_action.triggered.connect(self.reader_view.add_bookmark)
        nav_menu.addAction(add_bookmark_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        font_action = QAction('字体设置', self)
        font_action.triggered.connect(self.reader_view.change_font)
        view_menu.addAction(font_action)
        
        # 添加字体大小调节选项
        font_size_action = QAction('字体大小调节', self)
        font_size_action.triggered.connect(self.show_font_size_dialog)
        view_menu.addAction(font_size_action)
        
        # 添加行间距调节选项
        line_spacing_action = QAction('行间距调节', self)
        line_spacing_action.triggered.connect(self.show_line_spacing_dialog)
        view_menu.addAction(line_spacing_action)
        
        # 添加对比度调节选项
        contrast_action = QAction('对比度调节', self)
        contrast_action.triggered.connect(self.show_contrast_dialog)
        view_menu.addAction(contrast_action)
        
        # 添加亮度调节选项
        brightness_action = QAction('亮度调节', self)
        brightness_action.triggered.connect(self.show_brightness_dialog)
        view_menu.addAction(brightness_action)
        
        # 添加无边框模式选项
        frameless_action = QAction('无边框模式', self)
        frameless_action.setCheckable(True)
        frameless_action.triggered.connect(lambda checked: self.toggle_frameless_mode(checked))
        view_menu.addAction(frameless_action)
        
        # 主题子菜单
        theme_menu = view_menu.addMenu('主题')
        for theme_name in ['light', 'dark', 'sepia', 'green', 'blue']:
            theme_action = QAction(theme_name, self)
            theme_action.triggered.connect(lambda checked, tn=theme_name: self.reader_view.set_theme(tn))
            theme_menu.addAction(theme_action)
            
    def show_brightness_dialog(self):
        """显示亮度调节对话框"""
        current_opacity = int(self.windowOpacity() * 100)
        dialog = AdjustmentDialog(self, "亮度", current_opacity, 0, 100, 1)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.adjust_brightness(dialog.get_value())
            
    def create_tool_bar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # 小说选择下拉框
        self.novel_selector = QComboBox()
        self.novel_selector.setMinimumWidth(200)
        self.novel_selector.currentIndexChanged.connect(self.on_novel_selected)
        self.toolbar.addWidget(self.novel_selector)
        self.update_novel_list()
        
        # 添加翻页按钮
        prev_page_action = QAction('上一页', self)
        prev_page_action.triggered.connect(self.reader_view.prev_page)
        self.toolbar.addAction(prev_page_action)
        
        next_page_action = QAction('下一页', self)
        next_page_action.triggered.connect(self.reader_view.next_page)
        self.toolbar.addAction(next_page_action)
        
        # 自动滚动按钮
        auto_scroll_action = QAction('自动滚动', self)
        auto_scroll_action.setCheckable(True)
        auto_scroll_action.triggered.connect(lambda checked: self.reader_view.toggle_auto_scroll())
        self.toolbar.addAction(auto_scroll_action)
        
    def adjust_brightness(self, value):
        """调整亮度"""
        opacity = value / 100.0
        self.setWindowOpacity(opacity)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.statusBar().showMessage('就绪')
        
    def set_novels_dir(self):
        """设置默认小说文件夹"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择默认小说文件夹",
            self.settings_manager.preferences.novels_dir
        )
        
        if dir_path:
            self.settings_manager.preferences.novels_dir = dir_path
            self.settings_manager.save_preferences()
            self.statusBar().showMessage(f'已设置默认小说文件夹: {dir_path}')
            self.update_novel_list()
            
    def update_novel_list(self):
        """更新小说列表"""
        self.novel_selector.clear()
        novels_dir = self.settings_manager.preferences.novels_dir
        
        if novels_dir and os.path.exists(novels_dir):
            # 获取所有txt文件
            novel_files = [f for f in os.listdir(novels_dir) if f.endswith('.txt')]
            novel_files.sort()
            
            # 添加到下拉框
            self.novel_selector.addItem('选择小说...')
            for novel in novel_files:
                self.novel_selector.addItem(novel)
                
    def on_novel_selected(self, index):
        """处理小说选择事件"""
        if index <= 0:  # 忽略第一个占位项
            return
            
        novel_name = self.novel_selector.currentText()
        novels_dir = self.settings_manager.preferences.novels_dir
        
        if novels_dir and os.path.exists(novels_dir):
            file_path = os.path.join(novels_dir, novel_name)
            if os.path.exists(file_path):
                self.load_file(file_path)
    
    def open_from_novels_dir(self):
        """从默认小说文件夹打开文件"""
        novels_dir = self.settings_manager.preferences.novels_dir
        if not novels_dir or not os.path.exists(novels_dir):
            self.statusBar().showMessage('请先设置默认小说文件夹')
            self.set_novels_dir()
            return
            
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "从默认文件夹打开小说",
            novels_dir,
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_name:
            self.load_file(file_name)
    
    def open_file(self):
        """打开文件对话框"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "打开文件",
            "",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_name:
            self.load_file(file_name)
    
    def show_font_size_dialog(self):
        """显示字体大小调节对话框"""
        current_size = self.reader_view.font_size
        dialog = AdjustmentDialog(self, "字体大小", current_size, 8, 36, 1)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.reader_view.change_font_size(dialog.get_value())
    
    def show_line_spacing_dialog(self):
        """显示行间距调节对话框"""
        current_spacing = self.reader_view.line_spacing
        dialog = AdjustmentDialog(self, "行间距", current_spacing, 100, 300, 10)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.reader_view.change_line_spacing(dialog.get_value())
    
    def show_contrast_dialog(self):
        """显示对比度调节对话框"""
        current_contrast = self.reader_view.contrast_level
        dialog = AdjustmentDialog(self, "对比度", current_contrast, 50, 150, 5)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.reader_view.adjust_contrast(dialog.get_value())
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        open_action = QAction('打开', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # 添加从默认文件夹打开的选项
        open_from_dir_action = QAction('从默认文件夹打开', self)
        open_from_dir_action.triggered.connect(self.open_from_novels_dir)
        file_menu.addAction(open_from_dir_action)
        
        # 添加设置默认文件夹的选项
        set_novels_dir_action = QAction('设置默认文件夹', self)
        set_novels_dir_action.triggered.connect(self.set_novels_dir)
        file_menu.addAction(set_novels_dir_action)
        
        # 导航菜单
        nav_menu = menubar.addMenu('导航')
        
        chapter_action = QAction('章节列表', self)
        chapter_action.triggered.connect(self.reader_view.show_chapters)
        nav_menu.addAction(chapter_action)
        
        bookmark_action = QAction('书签管理', self)
        bookmark_action.triggered.connect(self.reader_view.show_bookmarks)
        nav_menu.addAction(bookmark_action)
        
        add_bookmark_action = QAction('添加书签', self)
        add_bookmark_action.triggered.connect(self.reader_view.add_bookmark)
        nav_menu.addAction(add_bookmark_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        font_action = QAction('字体设置', self)
        font_action.triggered.connect(self.reader_view.change_font)
        view_menu.addAction(font_action)
        
        # 添加字体大小调节选项
        font_size_action = QAction('字体大小调节', self)
        font_size_action.triggered.connect(self.show_font_size_dialog)
        view_menu.addAction(font_size_action)
        
        # 添加行间距调节选项
        line_spacing_action = QAction('行间距调节', self)
        line_spacing_action.triggered.connect(self.show_line_spacing_dialog)
        view_menu.addAction(line_spacing_action)
        
        # 添加对比度调节选项
        contrast_action = QAction('对比度调节', self)
        contrast_action.triggered.connect(self.show_contrast_dialog)
        view_menu.addAction(contrast_action)
        
        # 添加亮度调节选项
        brightness_action = QAction('亮度调节', self)
        brightness_action.triggered.connect(self.show_brightness_dialog)
        view_menu.addAction(brightness_action)
        
        # 添加无边框模式选项
        frameless_action = QAction('无边框模式', self)
        frameless_action.setCheckable(True)
        frameless_action.triggered.connect(lambda checked: self.toggle_frameless_mode(checked))
        view_menu.addAction(frameless_action)
        
        # 主题子菜单
        theme_menu = view_menu.addMenu('主题')
        for theme_name in ['light', 'dark', 'sepia', 'green', 'blue']:
            theme_action = QAction(theme_name, self)
            theme_action.triggered.connect(lambda checked, tn=theme_name: self.reader_view.set_theme(tn))
            theme_menu.addAction(theme_action)
            
    def load_file(self, file_name):
        """加载文件内容"""
        try:
            # 首先检测文件编码
            with open(file_name, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] if result['confidence'] > 0.7 else None
    
            # 定义常用编码列表
            encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
            if encoding:
                encodings.insert(0, encoding)
    
            # 尝试不同的编码
            content = None
            used_encoding = None
            for enc in encodings:
                try:
                    content = raw_data.decode(enc)
                    used_encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
    
            if content is None:
                raise Exception('无法识别文件编码')
    
            self.current_file = file_name  # 更新当前文件路径
            self.reader_view.set_content(content)
            self.statusBar().showMessage(f'已打开: {file_name} (编码: {used_encoding})')
            
            # 加载上次阅读进度
            progress = self.settings_manager.load_reading_progress(file_name)
            if progress:
                self.reader_view.jump_to_position(progress.position)
                self.reader_view.current_chapter_index = progress.chapter_index
                self.statusBar().showMessage(f'已恢复上次阅读位置')
                
            # 加载书签
            bookmarks = self.settings_manager.load_bookmarks(file_name)
            self.reader_view.bookmarks = bookmarks
        except Exception as e:
            self.statusBar().showMessage(f'打开文件失败: {str(e)}')
            
    def closeEvent(self, event):
        """窗口关闭事件，保存阅读进度"""
        if self.current_file:
            # 创建阅读进度对象
            from settings import ReadingProgress
            progress = ReadingProgress(
                file_path=self.current_file,
                position=self.reader_view.current_position,
                chapter_index=self.reader_view.current_chapter_index
            )
            # 保存阅读进度
            self.settings_manager.save_reading_progress(progress)
            
            # 保存书签
            if self.reader_view.bookmarks:
                self.settings_manager.save_bookmarks(
                    self.current_file,
                    self.reader_view.bookmarks
                )
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = ReaderWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()