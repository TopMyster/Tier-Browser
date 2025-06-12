# isle_browser.py

import sys
import os
import json
import re
from PyQt6.QtCore import Qt, QUrl, QSize, QPoint, QTimer, QEvent, QRect, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPalette, QColor, QKeySequence, QFont, QShortcut, QRegion, QPainterPath, QIcon, QPainter
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLineEdit, QDialog, QLabel,
    QTextEdit, QScrollArea, QStackedLayout,
    QRadioButton, QButtonGroup, QFrame, QSpacerItem, QSizePolicy
)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    print("\n--- ERROR: PyQt6-WebEngine is not installed or accessible. ---")
    print("Please install it using: pip install PyQt6-WebEngine")
    print("Exiting application.")
    sys.exit(1)

TAB_HEIGHT = 49
BAR_WIDTH = 660
BAR_HEIGHT = 64
CONFIG_FILE = "islebrowser_config.json"
WINDOW_RADIUS = 18  # All corners same radius

def load_config():
    # If config file does not exist, return default config with vertical tab mode
    if not os.path.exists(CONFIG_FILE):
        return {
            "tab_mode": "vertical",
            "light_mode": False
        }
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {
            "tab_mode": "vertical",
            "light_mode": False
        }

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"Error saving config file: {e}")

class NotesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type your notes here...")
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        self.setStyleSheet("background: #232323; color: white; font-size: 16px;")
        self.text_edit.setStyleSheet("background: #232323; color: white; font-size: 16px;")

class HomePage(QWidget):
    def __init__(self, light_mode=False):
        super().__init__()
        self.label = QLabel("Isle", self)
        font = QFont()
        font.setPointSize(48)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sublabel = QLabel("The browser you deserve", self)
        subfont = QFont()
        subfont.setPointSize(18)
        subfont.setBold(False)
        self.sublabel.setFont(subfont)
        self.sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sublabel.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sublabel, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        self.setLayout(layout)
        self.set_light_mode(light_mode)

    def set_light_mode(self, light_mode):
        if light_mode:
            self.setStyleSheet("background: #f0f0f0;")
            self.label.setStyleSheet("color: black; background: transparent;")
            self.sublabel.setStyleSheet("color: #232323; background: transparent;")
        else:
            self.setStyleSheet("background: #181818;")
            self.label.setStyleSheet("color: white; background: transparent;")
            self.sublabel.setStyleSheet("color: #bbbbbb; background: transparent;")

class BrowserTab(QWidget):
    def __init__(self, url=None, sketch=False, notes=False, parent=None, light_mode=False):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.stack = QStackedLayout()
        self.is_notes = notes
        self.is_sketch = sketch
        self.light_mode = light_mode
        if notes:
            self.notes_widget = NotesWidget()
            self.stack.addWidget(self.notes_widget)
        elif sketch:
            self.sketch = QWidget()  # Placeholder for SketchBoard
            self.stack.addWidget(self.sketch)
        else:
            self.webview = QWebEngineView()
            self.home = HomePage(light_mode=self.light_mode)
            self.stack.addWidget(self.home)
            self.stack.addWidget(self.webview)
        self.layout.addLayout(self.stack)
        self.setLayout(self.layout)
        self.is_home = not (sketch or notes)
        if not (sketch or notes):
            self.webview.urlChanged.connect(self._on_url_changed)
            self.webview.titleChanged.connect(self._on_title_changed)
            self.webview.loadFinished.connect(self._on_page_load)
        self._title_callback = None
        self._url_callback = None
        self._page_load_callback = None

        if not (sketch or notes):
            if url:
                self.setUrl(QUrl(url))
            else:
                self.setUrl(QUrl("about:blank"))
                self.show_home()

    def setUrl(self, url):
        if hasattr(self, "webview"):
            if isinstance(url, str):
                url = QUrl(url)
            if url.toString() == "about:blank":
                self.show_home()
            else:
                self.webview.setUrl(url)
                self.stack.setCurrentWidget(self.webview)
                self.is_home = False

    def show_home(self):
        if hasattr(self, "webview"):
            self.stack.setCurrentWidget(self.home)
            self.is_home = True

    def back(self):
        if hasattr(self, "webview") and not self.is_home:
            self.webview.back()

    def forward(self):
        if hasattr(self, "webview") and not self.is_home:
            self.webview.forward()

    def reload(self):
        if hasattr(self, "webview") and not self.is_home:
            self.webview.reload()

    def history(self):
        if hasattr(self, "webview"):
            return self.webview.history()
        return None

    def title(self):
        if self.is_notes:
            return "Notes"
        if self.is_sketch:
            return "Sketch"
        if self.is_home:
            return "New Tab"
        if hasattr(self, "webview"):
            url_str = self.webview.url().toString()
            # Show only the query for Google search
            match = re.match(r"https?://www\.google\.com/search\?q=([^&]+)", url_str)
            if match:
                return QUrl.fromPercentEncoding(match.group(1).encode())
            return self.webview.title() if self.webview.title() else "New Tab"
        return "New Tab"

    def url(self):
        if hasattr(self, "webview") and not self.is_home:
            url_str = self.webview.url().toString()
            # Show only the query for Google search
            match = re.match(r"https?://www\.google\.com/search\?q=([^&]+)", url_str)
            if match:
                return QUrl.fromPercentEncoding(match.group(1).encode())
            return url_str
        return ""

    def set_title_callback(self, cb):
        self._title_callback = cb

    def set_url_callback(self, cb):
        self._url_callback = cb

    def set_page_load_callback(self, cb):
        self._page_load_callback = cb

    def _on_url_changed(self, url):
        if self._url_callback:
            self._url_callback(url)

    def _on_title_changed(self, title):
        if self._title_callback:
            self._title_callback(title)

    def _on_page_load(self):
        if self._page_load_callback:
            self._page_load_callback()

class DraggableTabButton(QWidget):
    tabMoved = pyqtSignal(int, int)  # from, to

    def __init__(self, index, title, is_current, on_select, on_close, icon_color, text_color, border_color, parent=None):
        super().__init__(parent)
        self.index = index
        self.on_select = on_select
        self.on_close = on_close
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self._drag_start_pos = None

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        label = QLabel(title if title else "New Tab")
        font = QFont()
        font.setBold(is_current)
        font.setPointSize(16)
        label.setFont(font)
        if is_current:
            label.setStyleSheet("color: #2196f3; background: transparent; padding: 0px; margin: 0px;")
        else:
            label.setStyleSheet(f"color: {text_color}; background: transparent; padding: 0px; margin: 0px;")
        label.setContentsMargins(12, 0, 0, 0)
        main_layout.addWidget(label)

        close_btn = QPushButton("×")
        close_font = QFont()
        close_font.setBold(True)
        close_font.setPointSize(20)
        close_btn.setFont(close_font)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                color: {text_color};
                border: none;
                font-size: 22px;
                padding: 0 4px;
                margin-left: 8px;
                margin-right: 0px;
            }}
            QPushButton:hover {{
                color: #fff;
                background: rgba(255,0,0,0.5);
                border-radius: 12px;
            }}
            """
        )
        close_btn.setFixedSize(36, 36)
        close_btn.clicked.connect(lambda checked=False, idx=index: self.on_close(idx))
        main_layout.addWidget(close_btn)
        main_layout.setAlignment(close_btn, Qt.AlignmentFlag.AlignVCenter)

        self.setLayout(main_layout)
        self.setFixedHeight(44)
        self.setFixedWidth(240)  # Wider tabs

        if is_current:
            self.setStyleSheet(f"background: rgba(33, 150, 243, 0.10); border-radius: 0px;")
        else:
            self.setStyleSheet(f"background: transparent; border-radius: 0px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start_pos is not None and (event.position().toPoint() - self._drag_start_pos).manhattanLength() > 10:
            from PyQt6.QtCore import QMimeData
            from PyQt6.QtGui import QDrag
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(str(self.index))
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_select(self.index)
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        from_index = int(event.mimeData().text())
        to_index = self.index
        if from_index != to_index:
            self.tabMoved.emit(from_index, to_index)
        event.acceptProposedAction()

class TabBar(QWidget):
    def __init__(self, get_tab_titles, get_current_tab, on_select_tab, on_close_tab, on_reorder_tabs, get_theme, parent=None):
        super().__init__(parent)
        self.get_tab_titles = get_tab_titles
        self.get_current_tab = get_current_tab
        self.on_select_tab = on_select_tab
        self.on_close_tab = on_close_tab
        self.on_reorder_tabs = on_reorder_tabs
        self.get_theme = get_theme

        self.tab_mode = "horizontal"  # "horizontal" or "vertical"
        self.vertical_tab_popup = None
        self._popup_mouse_inside = False

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:horizontal, QScrollBar:vertical { height: 0px; width: 0px; background: transparent; }
            QScrollBar::handle:horizontal, QScrollBar::handle:vertical { background: transparent; }
        """)

        self.tabs_widget = QWidget()
        self.tabs_layout = QHBoxLayout()
        self.tabs_layout.setSpacing(8)
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs_widget.setLayout(self.tabs_layout)
        self.scroll.setWidget(self.tabs_widget)

        self.vertical_tabs_btn = QPushButton("Tabs")
        self.vertical_tabs_btn.setFixedHeight(40)
        self.vertical_tabs_btn.setFixedWidth(60)
        self.vertical_tabs_btn.setVisible(False)
        self.vertical_tabs_btn.installEventFilter(self)
        self.vertical_tabs_btn.clicked.connect(self._on_tabs_btn_clicked)
        self.update_tabs_btn_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll)
        self.setLayout(layout)
        self.tab_buttons = []
        self.update_tabs()

        self.setMouseTracking(True)
        self.scroll.setMouseTracking(True)
        self.tabs_widget.setMouseTracking(True)
        self.installEventFilter(self)

        self._popup_opened_by_click = False

    def set_tab_mode(self, mode):
        self.tab_mode = mode
        if mode == "horizontal":
            self.scroll.setVisible(True)
            self.vertical_tabs_btn.setVisible(False)
        else:
            self.scroll.setVisible(False)
            self.vertical_tabs_btn.setVisible(True)
        self.update_tabs()
        self.update_tabs_btn_style()

    def update_tabs_btn_style(self):
        light_mode = self.get_theme()
        if light_mode:
            self.vertical_tabs_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.08);
                    color: #232323;
                    border-radius: 16px;
                    font-size: 16px;
                    font-weight: bold;
                    margin-top: 4px;
                    margin-bottom: 4px;
                    border: none;
                }
                QPushButton:hover {
                    background: rgba(33, 150, 243, 0.2);
                    color: #232323;
                }
            """)
        else:
            self.vertical_tabs_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.08);
                    color: #fff;
                    border-radius: 16px;
                    font-size: 16px;
                    font-weight: bold;
                    margin-top: 4px;
                    margin-bottom: 4px;
                    border: none;
                }
                QPushButton:hover {
                    background: rgba(33, 150, 243, 0.2);
                    color: #2196f3;
                }
            """)

    def update_tabs(self):
        while self.tabs_layout.count():
            item = self.tabs_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.tab_buttons = []
        tab_titles = self.get_tab_titles()
        current_index = self.get_current_tab()
        light_mode = self.get_theme()
        icon_color = "#232323" if light_mode else "#2196f3"
        text_color = "#232323" if light_mode else "white"
        border_color = "#232323" if light_mode else "#444"
        for i, title in enumerate(tab_titles):
            btn = DraggableTabButton(
                index=i,
                title=title,
                is_current=(i == current_index),
                on_select=self.on_select_tab,
                on_close=self.on_close_tab,
                icon_color=icon_color,
                text_color=text_color,
                border_color=border_color
            )
            btn.tabMoved.connect(self._on_tab_moved)
            self.tabs_layout.addWidget(btn)
            self.tab_buttons.append(btn)
        self.update_tabs_btn_style()

    def _on_tab_moved(self, from_index, to_index):
        self.on_reorder_tabs(from_index, to_index)

    def eventFilter(self, obj, event):
        if self.tab_mode == "vertical":
            if obj == self.vertical_tabs_btn:
                if event.type() == QEvent.Type.Enter:
                    if not self._popup_opened_by_click:
                        self.show_vertical_tab_popup()
                elif event.type() == QEvent.Type.Leave:
                    QTimer.singleShot(100, self._maybe_hide_vertical_tab_popup)
            if obj == self and event.type() == QEvent.Type.Leave:
                QTimer.singleShot(100, self._maybe_hide_vertical_tab_popup)
        return super().eventFilter(obj, event)

    def _on_tabs_btn_clicked(self):
        if self.vertical_tab_popup is not None:
            self.hide_vertical_tab_popup()
            self._popup_opened_by_click = False
        else:
            self._popup_opened_by_click = True
            self.show_vertical_tab_popup()

    def show_vertical_tab_popup(self):
        if self.vertical_tab_popup is not None:
            return
        self.vertical_tab_popup = CurvedPopupFrame(self, radius=WINDOW_RADIUS, light_mode=self.get_theme())
        # Use a scroll area for the tab list, but only enable scrolling if more than 15 tabs
        tab_titles = self.get_tab_titles()
        current_index = self.get_current_tab()
        light_mode = self.get_theme()
        icon_color = "#232323" if light_mode else "#2196f3"
        text_color = "#232323" if light_mode else "white"
        border_color = "#232323" if light_mode else "#444"

        tab_list_widget = QWidget()
        vlayout = QVBoxLayout(tab_list_widget)
        vlayout.setContentsMargins(8, 8, 8, 8)
        vlayout.setSpacing(4)
        for i, title in enumerate(tab_titles):
            btn = DraggableTabButton(
                index=i,
                title=title,
                is_current=(i == current_index),
                on_select=lambda idx=i: (self.on_select_tab(idx), self.hide_vertical_tab_popup(), setattr(self, "_popup_opened_by_click", False)),
                on_close=self.on_close_tab,
                icon_color=icon_color,
                text_color=text_color,
                border_color=border_color
            )
            btn.tabMoved.connect(self._on_tab_moved)
            vlayout.addWidget(btn)
        vlayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        tab_list_widget.setLayout(vlayout)

        # Only show scroll area if more than 15 tabs
        use_scroll = len(tab_titles) > 15
        if use_scroll:
            scroll_area = QScrollArea(self.vertical_tab_popup)
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setStyleSheet("""
                QScrollArea { background: transparent; border: none; }
                QScrollBar:vertical, QScrollBar:horizontal { width: 0px; height: 0px; background: transparent; }
                QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background: transparent; }
            """)
            scroll_area.setWidget(tab_list_widget)
        else:
            scroll_area = None

        popup_layout = QVBoxLayout(self.vertical_tab_popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)
        popup_layout.setSpacing(0)
        if use_scroll:
            popup_layout.addWidget(scroll_area)
        else:
            popup_layout.addWidget(tab_list_widget)
        self.vertical_tab_popup.setLayout(popup_layout)

        # Sizing logic
        max_visible_tabs = 15
        tab_height = 44
        visible_count = min(len(tab_titles), max_visible_tabs)
        popup_height = visible_count * tab_height + 16  # 8px top/bottom margin
        popup_width = 260  # slightly wider than tab

        self.vertical_tab_popup.setFixedWidth(popup_width)
        self.vertical_tab_popup.setFixedHeight(popup_height)

        btn_rect = self.vertical_tabs_btn.rect()
        btn_global = self.vertical_tabs_btn.mapToGlobal(btn_rect.topLeft())
        self.vertical_tab_popup.move(btn_global.x() + btn_rect.width()//2 - popup_width//2, btn_global.y() - popup_height - 8)
        self.vertical_tab_popup.show()

    def _popup_enter(self, event):
        self._popup_mouse_inside = True

    def _popup_leave(self, event):
        self._popup_mouse_inside = False
        QTimer.singleShot(100, self._maybe_hide_vertical_tab_popup)

    def _maybe_hide_vertical_tab_popup(self):
        if not self._popup_mouse_inside and not self.vertical_tabs_btn.underMouse():
            self.hide_vertical_tab_popup()
            self._popup_opened_by_click = False

    def hide_vertical_tab_popup(self):
        if self.vertical_tab_popup is not None:
            self.vertical_tab_popup.hide()
            self.vertical_tab_popup.deleteLater()
            self.vertical_tab_popup = None

class CurvedPopupFrame(QFrame):
    def __init__(self, parent=None, radius=12, light_mode=False):
        super().__init__(parent, Qt.WindowType.Popup)
        self.radius = radius
        self.light_mode = light_mode
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("QFrame { background: transparent; border: none; }")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self.radius, self.radius)
        if self.light_mode:
            painter.setPen(QColor("#bbb"))
            painter.setBrush(QColor("#fff"))
        else:
            painter.setPen(QColor("#444"))
            painter.setBrush(QColor("#232323"))
        painter.drawPath(path)
        painter.setPen(QColor("#bbb") if self.light_mode else QColor("#444"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

class FloatingBar(QWidget):
    def __init__(self, parent, get_tab_titles, get_current_tab, on_select_tab, on_close_tab, on_reorder_tabs, on_new_tab, on_back, on_forward, on_search, on_settings, get_can_go_back, get_can_go_forward, get_theme):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedHeight(BAR_HEIGHT)
        self.setFixedWidth(BAR_WIDTH)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(18, 8, 18, 8)
        main_layout.setSpacing(10)

        self.nav_search_background = QWidget(self)
        self.nav_search_background.setFixedHeight(BAR_HEIGHT - 16)
        self.nav_search_background.setStyleSheet("""
            background: rgba(50, 50, 50, 0.7);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        """)

        nav_search_layout = QHBoxLayout(self.nav_search_background)
        nav_search_layout.setContentsMargins(8, 0, 8, 0)
        nav_search_layout.setSpacing(0)

        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(36, 36)
        self.plus_btn.clicked.connect(on_new_tab)

        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(36, 36)
        self.back_btn.clicked.connect(on_back)

        self.forward_btn = QPushButton(">")
        self.forward_btn.setFixedSize(36, 36)
        self.forward_btn.clicked.connect(on_forward)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search or enter URL...")
        self.search_bar.setFixedHeight(32)
        self.search_bar.returnPressed.connect(on_search)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.clicked.connect(on_settings)

        nav_search_layout.addWidget(self.plus_btn)
        nav_search_layout.addWidget(self.back_btn)
        nav_search_layout.addWidget(self.forward_btn)
        nav_search_layout.addSpacing(4)
        nav_search_layout.addWidget(self.search_bar, stretch=1)
        nav_search_layout.addSpacing(2)
        nav_search_layout.addWidget(self.settings_btn)

        self.tab_bar = TabBar(
            get_tab_titles=get_tab_titles,
            get_current_tab=get_current_tab,
            on_select_tab=on_select_tab,
            on_close_tab=on_close_tab,
            on_reorder_tabs=on_reorder_tabs,
            get_theme=get_theme
        )
        self.tab_bar.setFixedHeight(BAR_HEIGHT - 16)

        nav_search_layout.addWidget(self.tab_bar.vertical_tabs_btn)
        self.tab_bar.vertical_tabs_btn.setVisible(self.tab_bar.tab_mode == "vertical")

        main_layout.addWidget(self.nav_search_background, stretch=1)
        main_layout.addWidget(self.tab_bar, stretch=0)
        self.setLayout(main_layout)

        self.get_can_go_back = get_can_go_back
        self.get_can_go_forward = get_can_go_forward
        self.get_theme = get_theme

        self.update_theme()

    def update_nav_buttons(self):
        light_mode = self.get_theme()
        text_color = "#232323" if light_mode else "white"
        icon_color = "#232323" if light_mode else "white"
        can_go_back = self.get_can_go_back()
        can_go_forward = self.get_can_go_forward()
        self.back_btn.setEnabled(can_go_back)
        self.forward_btn.setEnabled(can_go_forward)

        self.back_btn.setStyleSheet(
            f"background: transparent; color: {icon_color}; font-size: 24px; border: none; margin:0; padding:0;" + (f" opacity: 0.5;" if not can_go_back else "")
        )
        self.forward_btn.setStyleSheet(
            f"background: transparent; color: {icon_color}; font-size: 24px; border: none; margin:0; padding:0;" + (f" opacity: 0.5;" if not can_go_forward else "")
        )
        self.plus_btn.setStyleSheet(f"background: transparent; color: {icon_color}; font-size: 24px; border: none; margin:0; padding:0;")
        self.settings_btn.setStyleSheet(f"background: transparent; color: {icon_color}; font-size: 20px; border: none;")
        self.search_bar.setStyleSheet(
            f"background: {'rgba(0,0,0,0.05)' if light_mode else 'rgba(255,255,255,0.1)'}; color: {text_color}; border: none; border-radius: 12px; padding: 4px 8px; font-size: 16px; min-width: 70px; max-width: 180px;"
        )
        self.update_theme()
        self.tab_bar.update_tabs_btn_style()

    def update_theme(self):
        light_mode = self.get_theme()
        if light_mode:
            self.nav_search_background.setStyleSheet("""
                background: rgba(255,255,255,0.7);
                border-radius: 20px;
                border: 1px solid rgba(0,0,0,0.08);
            """)
            self.tab_bar.setStyleSheet("""
                background: rgba(255,255,255,0.7);
                border-radius: 20px;
                border: 1px solid rgba(0,0,0,0.08);
            """)
        else:
            self.nav_search_background.setStyleSheet("""
                background: rgba(50, 50, 50, 0.7);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            """)
            self.tab_bar.setStyleSheet("""
                background: rgba(50, 50, 50, 0.7);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            """)

class WindowControlsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(14, 14)
        self.close_btn.setStyleSheet("QPushButton { background-color: #ff5f56; border-radius: 7px; border: none; } QPushButton:hover { background-color: #e33e41; }")
        self.close_btn.clicked.connect(self.parent_window.close)

        self.min_btn = QPushButton()
        self.min_btn.setFixedSize(14, 14)
        self.min_btn.setStyleSheet("QPushButton { background-color: #ffbd2e; border-radius: 7px; border: none; } QPushButton:hover { background-color: #e09e3e; }")
        self.min_btn.clicked.connect(self.parent_window.showMinimized)

        self.max_btn = QPushButton()
        self.max_btn.setFixedSize(14, 14)
        self.max_btn.setStyleSheet("QPushButton { background-color: #27c93f; border-radius: 7px; border: none; } QPushButton:hover { background-color: #13a10e; }")
        self.max_btn.clicked.connect(self.toggle_max_restore)

        layout.addWidget(self.close_btn)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        self.setLayout(layout)
        self.setFixedSize(self.sizeHint())

    def toggle_max_restore(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 350)
        self.config = config.copy() 
        self.parent_window = parent

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        tab_mode_label = QLabel("Tab Mode")
        layout.addWidget(tab_mode_label)
        self.tab_mode_group = QButtonGroup(self)
        self.horizontal_tabs_radio = QRadioButton("Horizontal Tabs")
        self.vertical_tabs_radio = QRadioButton("Vertical Tabs (on hover)")
        self.tab_mode_group.addButton(self.horizontal_tabs_radio)
        self.tab_mode_group.addButton(self.vertical_tabs_radio)
        if self.config.get("tab_mode", "horizontal") == "vertical":
             self.vertical_tabs_radio.setChecked(True)
        else:
             self.horizontal_tabs_radio.setChecked(True)
        layout.addWidget(self.horizontal_tabs_radio)
        layout.addWidget(self.vertical_tabs_radio)

        theme_label = QLabel("Theme")
        layout.addWidget(theme_label)
        self.theme_group = QButtonGroup(self)
        self.light_radio = QRadioButton("Light Mode")
        self.dark_radio = QRadioButton("Dark Mode")
        self.theme_group.addButton(self.light_radio)
        self.theme_group.addButton(self.dark_radio)
        if self.config.get("light_mode", False):
            self.light_radio.setChecked(True)
        else:
            self.dark_radio.setChecked(True)
        layout.addWidget(self.light_radio)
        layout.addWidget(self.dark_radio)

        layout.addStretch()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_btn = QPushButton("Save & Close")
        self.save_btn.clicked.connect(self.save_and_close)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)

        self.set_theme(self.config.get("light_mode", False))

    def set_theme(self, light_mode):
        if light_mode:
            self.setStyleSheet("""
                QDialog { background-color: #fff; color: #232323; }
                QLabel, QRadioButton { color: #232323; }
                QPushButton {
                    background-color: #232323;
                    color: #fff;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #444; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #232323; color: #fff; }
                QLabel, QRadioButton { color: #fff; }
                QPushButton {
                    background-color: #2196f3;
                    color: #fff;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #1a78c2; }
            """)

    def save_and_close(self):
        self.config["tab_mode"] = "vertical" if self.vertical_tabs_radio.isChecked() else "horizontal"
        self.config["light_mode"] = self.light_radio.isChecked()
        self.parent_window.apply_settings(self.config)
        save_config(self.config)
        self.accept()

class IsleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isle Browser")
        self.setGeometry(100, 100, 1350, 820)
        self.config = load_config()
        self.history_list = []
        self._mouse_press_pos = None
        self._mouse_move_pos = None
        
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;")
        
        self.container_widget = QWidget()
        self.container_widget.setObjectName("ContainerWidget")
        self.setCentralWidget(self.container_widget)
        
        self.v_layout = QVBoxLayout(self.container_widget)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)
        
        self.tabs = []
        self.current_tab = 0
        self.webview_container = QWidget()
        self.webview_layout = QStackedLayout()
        self.webview_layout.setContentsMargins(0, 0, 0, 0)
        self.webview_container.setLayout(self.webview_layout)
        self.v_layout.addWidget(self.webview_container)

        self.window_controls = WindowControlsWidget(self)

        self.floating_bar = FloatingBar(
            parent=self,
            get_tab_titles=lambda: [tab.title() for tab in self.tabs],
            get_current_tab=lambda: self.current_tab,
            on_select_tab=self.select_tab,
            on_close_tab=self.close_tab,
            on_reorder_tabs=self.reorder_tabs,
            on_new_tab=self.add_tab_from_button,
            on_back=self.go_back,
            on_forward=self.go_forward,
            on_search=self.search_from_bar,
            on_settings=self.show_settings,
            get_can_go_back=self.can_go_back,
            get_can_go_forward=self.can_go_forward,
            get_theme=lambda: self.config.get("light_mode", False)
        )
        
        initial_tab_mode = self.config.get("tab_mode", "horizontal")
        self.floating_bar.tab_bar.set_tab_mode(initial_tab_mode)

        self.apply_theme(self.config.get("light_mode", False))
        self.add_tab()

        QShortcut(QKeySequence("Ctrl+T"), self, self.add_tab_from_button)
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self.close_tab(self.current_tab))
        
    def add_tab(self, url=None, sketch=False, notes=False, select=True):
        light_mode = self.config.get("light_mode", False)
        tab = BrowserTab(url, sketch, notes, parent=self, light_mode=light_mode)
        self.tabs.append(tab)
        self.webview_layout.addWidget(tab)
        tab.set_url_callback(lambda url, t=tab: self.update_url(url, t))
        tab.set_title_callback(lambda title, t=tab: self.update_title(t))
        tab.set_page_load_callback(lambda: self.update_nav_buttons())
        if select:
            self.select_tab(len(self.tabs) - 1)
        self.floating_bar.tab_bar.update_tabs()
        return tab

    def add_tab_from_button(self):
        self.add_tab()

    def select_tab(self, index):
        if 0 <= index < len(self.tabs):
            self.current_tab = index
            self.webview_layout.setCurrentIndex(index)
            self.floating_bar.tab_bar.update_tabs()
            self.update_url(self.tabs[index].url(), self.tabs[index])
            self.update_title()
            self.update_nav_buttons()
    
    def close_tab(self, index):
        if 0 <= index < len(self.tabs):
            if len(self.tabs) == 1:
                self.close()
                return
            tab_to_close = self.tabs.pop(index)
            self.webview_layout.removeWidget(tab_to_close)
            tab_to_close.deleteLater()
            if self.current_tab >= index:
                self.current_tab = max(0, self.current_tab - 1)
            self.select_tab(self.current_tab)
            self.floating_bar.tab_bar.update_tabs()

    def reorder_tabs(self, from_index, to_index):
        if from_index == to_index or not (0 <= from_index < len(self.tabs)) or not (0 <= to_index < len(self.tabs)):
            return
        tab = self.tabs.pop(from_index)
        self.tabs.insert(to_index, tab)
        self.webview_layout.removeWidget(tab)
        self.webview_layout.insertWidget(to_index, tab)
        if self.current_tab == from_index:
            self.current_tab = to_index
        elif from_index < self.current_tab <= to_index:
            self.current_tab -= 1
        elif to_index <= self.current_tab < from_index:
            self.current_tab += 1
        self.floating_bar.tab_bar.update_tabs()
        self.select_tab(self.current_tab)

    def go_back(self):
        self.tabs[self.current_tab].back()
        self.update_nav_buttons()
        
    def go_forward(self):
        self.tabs[self.current_tab].forward()
        self.update_nav_buttons()
        
    def can_go_back(self):
        if not self.tabs: return False
        history = self.tabs[self.current_tab].history()
        return history.canGoBack() if history else False

    def can_go_forward(self):
        if not self.tabs: return False
        history = self.tabs[self.current_tab].history()
        return history.canGoForward() if history else False
        
    def search_from_bar(self):
        text = self.floating_bar.search_bar.text()
        # If it's a Google search, only show the query in the bar
        if text.strip() == "":
            return
        url = QUrl(text)
        if not url.scheme():
            url = QUrl(f"https://www.google.com/search?q={text}")
            self.floating_bar.search_bar.setText(text)
        self.tabs[self.current_tab].setUrl(url)
        
    def update_url(self, url, tab):
        if self.tabs[self.current_tab] == tab:
            if isinstance(url, QUrl):
                url = url.toString()
            # If it's a Google search, only show the query
            match = re.match(r"https?://www\.google\.com/search\?q=([^&]+)", url)
            if match:
                url = QUrl.fromPercentEncoding(match.group(1).encode())
            self.floating_bar.search_bar.setText(url)
        self.update_nav_buttons()
        
    def update_title(self, tab=None):
        if not self.tabs: return
        if tab is None or tab == self.tabs[self.current_tab]:
            self.floating_bar.tab_bar.update_tabs()

    def update_nav_buttons(self):
        self.floating_bar.update_nav_buttons()

    def show_settings(self):
        dialog = SettingsDialog(self.config, self)
        dialog.set_theme(self.config.get("light_mode", False))
        dialog.exec()

    def apply_settings(self, new_config):
        self.config = new_config
        self.floating_bar.tab_bar.set_tab_mode(self.config.get("tab_mode", "horizontal"))
        self.apply_theme(self.config.get("light_mode", False))
        for tab in self.tabs:
            if hasattr(tab, "home"):
                tab.home.set_light_mode(self.config.get("light_mode", False))
        self.floating_bar.update_nav_buttons()
        self.floating_bar.tab_bar.update_tabs()

    def apply_theme(self, light_mode):
        if light_mode:
            self.container_widget.setStyleSheet("""
                #ContainerWidget {
                    background-color: #f0f0f0;
                    border-radius: 18px;
                }
            """)
        else:
            self.container_widget.setStyleSheet("""
                #ContainerWidget {
                    background-color: #181818;
                    border-radius: 18px;
                }
            """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        x = (self.width() - self.floating_bar.width()) // 2
        y = self.height() - self.floating_bar.height() - 20 
        self.floating_bar.move(x, y)
        self.window_controls.move(18, 12)
        self.apply_rounded_corners()

    def apply_rounded_corners(self):
        # All corners same radius
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, WINDOW_RADIUS, WINDOW_RADIUS)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def showEvent(self, event):
        super().showEvent(event)
        self.apply_rounded_corners()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < 40:
                self._mouse_press_pos = event.globalPosition().toPoint()
                self._mouse_move_pos = event.globalPosition().toPoint()
                event.accept()
            else:
                event.ignore()

    def mouseMoveEvent(self, event):
        if self._mouse_press_pos is not None and not self.isMaximized():
            delta = event.globalPosition().toPoint() - self._mouse_move_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._mouse_move_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._mouse_press_pos = None
        self._mouse_move_pos = None
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IsleBrowser()
    window.show()
    sys.exit(app.exec())
