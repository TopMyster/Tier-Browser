# isle_browser.py

import sys
import os
import json
import re
import webbrowser
from PyQt6.QtCore import Qt, QUrl, QSize, QPoint, QTimer, QEvent
from PyQt6.QtGui import (
    QPalette, QColor, QKeySequence, QFont, QShortcut
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLineEdit, QDialog, QLabel,
    QListWidget, QListWidgetItem, QTextEdit, QScrollArea, QStackedLayout,
    QMessageBox, QRadioButton, QButtonGroup, QFrame, QSpacerItem, QSizePolicy
)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    print("\n--- ERROR: PyQt6-WebEngine is not installed or accessible. ---")
    print("Please install it using: pip install PyQt6-WebEngine")
    print("Exiting application.")
    sys.exit(1)

TAB_HEIGHT = 49
BOTTOM_BAR_DEFAULT = 56
BAR_WIDTH = 660
BAR_HEIGHT = 64
FLOAT_BAR_RADIUS = 24
CONFIG_FILE = "islebrowser_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
            return {}
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"Error saving config file: {e}")

def get_youtube_embed_url(url):
    match = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w\-]+)", url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}?autoplay=1"
    return None

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

class MiniPlayer(QDialog):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mini Player")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(400, 225)
        layout = QVBoxLayout()
        self.webview = QWebEngineView()
        layout.addWidget(self.webview)
        self.setLayout(layout)
        embed_url = get_youtube_embed_url(url)
        if embed_url:
            self.webview.setUrl(QUrl(embed_url))
        else:
            self.webview.setUrl(QUrl(url))

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

class SketchBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setMinimumSize(400, 300)
        self.bg_color = QColor("#232323")
        self.pen_color = QColor("#fff")
        self.drawing = False
        self.last_point = QPoint()
        self.paths = []
        self.current_path = []
        self.pen_width = 3

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedWidth(80)
        self.clear_btn.setStyleSheet("margin: 8px;")
        self.clear_btn.clicked.connect(self.clear_board)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.clear_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(0)
        self.setLayout(layout)

    def clear_board(self):
        self.paths = []
        self.current_path = []
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QPen
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)
        pen = QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        for path in self.paths:
            if len(path) > 1:
                for i in range(1, len(path)):
                    painter.drawLine(path[i-1], path[i])
        if len(self.current_path) > 1:
            for i in range(1, len(self.current_path)):
                painter.drawLine(self.current_path[i-1], self.current_path[i])

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.current_path = [event.position().toPoint()]
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.current_path.append(event.position().toPoint())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            self.paths.append(list(self.current_path))
            self.current_path = []
            self.update()

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
            self.sketch = SketchBoard()
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
            match = re.match(r"https?://www\.google\.com/search\?q=([^&]+)", url_str)
            if match:
                return QUrl.fromPercentEncoding(match.group(1).encode())
            return self.webview.title() if self.webview.title() else "New Tab"
        return "New Tab"

    def url(self):
        if hasattr(self, "webview") and not self.is_home:
            url_str = self.webview.url().toString()
            match = re.match(r"https?://www\.google\.com/search\?q=([^&]+)", url_str)
            if match:
                return QUrl.fromPercentEncoding(match.group(1).encode())
            return url_str
        return ""

    def is_video_playing(self, callback):
        if not hasattr(self, "webview") or self.is_home:
            callback(False)
            return
        js = """
        (function() {
            var v = document.querySelector('video');
            return !!(v && !v.paused && !v.ended && v.readyState > 2);
        })();
        """
        self.webview.page().runJavaScript(js, callback)

    def _on_url_changed(self, url):
        if self._url_callback:
            self._url_callback(url)

    def _on_title_changed(self, title):
        if self._title_callback:
            self._title_callback(title)

    def set_title_callback(self, cb):
        self._title_callback = cb

    def set_url_callback(self, cb):
        self._url_callback = cb

    def set_page_load_callback(self, cb):
        self._page_load_callback = cb

    def _on_page_load(self):
        if self._page_load_callback:
            self._page_load_callback()

class TabBar(QWidget):
    def __init__(self, get_tab_titles, get_current_tab, on_select_tab, on_close_tab, parent=None):
        super().__init__(parent)
        self.get_tab_titles = get_tab_titles
        self.get_current_tab = get_current_tab
        self.on_select_tab = on_select_tab
        self.on_close_tab = on_close_tab

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
        self.vertical_tabs_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: #fff;
                border-radius: 16px;
                font-size: 16px;
                margin-top: 4px;
                margin-bottom: 4px;
                border: none;
            }
            QPushButton:hover {
                background: rgba(33, 150, 243, 0.2);
                color: #2196f3;
            }
        """)
        self.vertical_tabs_btn.setVisible(False)
        self.vertical_tabs_btn.installEventFilter(self)
        self.vertical_tabs_btn.clicked.connect(self._on_tabs_btn_clicked)

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

    def update_tabs(self):
        while self.tabs_layout.count():
            item = self.tabs_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.tab_buttons = []
        tab_titles = self.get_tab_titles()
        current_index = self.get_current_tab()
        max_tab_width = 180
        for i, title in enumerate(tab_titles):
            btn = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(8, 0, 8, 0)
            btn_layout.setSpacing(4)

            dot = QLabel("●")
            dot.setStyleSheet(f"color: {'#2196f3' if i == current_index else '#888'}; font-size: 16px; background: transparent; padding: 0px; margin: 0px;")
            dot.setContentsMargins(0, 0, 0, 0)
            btn_layout.addWidget(dot)

            label = QLabel(title if title else "New Tab")
            font = QFont()
            font.setBold(i == current_index)
            font.setPointSize(15)
            label.setFont(font)
            label_text_color = "#2196f3" if i == current_index else "white"
            label.setStyleSheet(f"color: {label_text_color}; background: transparent; padding: 0px; margin: 0px;")
            label.setContentsMargins(0, 0, 0, 0)
            btn_layout.addWidget(label)

            close_btn = QPushButton("×")
            close_font = QFont()
            close_font.setBold(True)
            close_font.setPointSize(18)
            close_btn.setFont(close_font)
            close_btn.setStyleSheet(
                """
                QPushButton {
                    background: transparent;
                    color: #cccccc;
                    border: none;
                    font-size: 20px;
                    padding: 0 4px;
                    margin-left: 2px;
                    margin-right: 0px;
                }
                QPushButton:hover {
                    color: #fff;
                    background: rgba(255,0,0,0.5);
                    border-radius: 12px;
                }
                """
            )
            close_btn.setFixedSize(32, 32)
            close_btn.clicked.connect(lambda checked=False, idx=i: self.on_close_tab(idx))
            btn_layout.addWidget(close_btn)
            btn.setLayout(btn_layout)
            btn.setFixedHeight(40)
            btn.setFixedWidth(max_tab_width)
            btn.setStyleSheet(f"""
                background: rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                margin-top: 4px;
                margin-bottom: 4px;
                {'background: rgba(33, 150, 243, 0.18);' if i == current_index else ''}
                border: none;
            """)
            def make_tab_press(idx):
                def tab_press(event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        self.on_select_tab(idx)
                return tab_press
            btn.mousePressEvent = make_tab_press(i)
            self.tabs_layout.addWidget(btn)
            self.tab_buttons.append(btn)

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
        self.vertical_tab_popup = QFrame(self, Qt.WindowType.Popup)
        self.vertical_tab_popup.setStyleSheet("""
            QFrame {
                background: #232323;
                border-radius: 20px;
                border: 1px solid #444;
                padding: 0px;
            }
        """)
        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0, 8, 0, 8)
        vlayout.setSpacing(0)
        tab_titles = self.get_tab_titles()
        current_index = self.get_current_tab()
        for i, title in enumerate(tab_titles):
            tab_btn = QWidget()
            tab_btn_layout = QHBoxLayout()
            tab_btn_layout.setContentsMargins(12, 2, 12, 2)
            tab_btn_layout.setSpacing(8)
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {'#2196f3' if i == current_index else '#888'}; font-size: 16px; background: transparent;")
            tab_btn_layout.addWidget(dot)
            label = QLabel(title if title else "New Tab")
            font = QFont()
            font.setBold(i == current_index)
            font.setPointSize(15)
            label.setFont(font)
            label.setStyleSheet(f"color: {'#2196f3' if i == current_index else 'white'}; background: transparent;")
            tab_btn_layout.addWidget(label)
            tab_btn_layout.addStretch(1)
            close_btn = QPushButton("×")
            close_font = QFont()
            close_font.setBold(True)
            close_font.setPointSize(18)
            close_btn.setFont(close_font)
            close_btn.setStyleSheet(
                """
                QPushButton {
                    background: transparent;
                    color: #cccccc;
                    border: none;
                    font-size: 20px;
                    padding: 0 4px;
                }
                QPushButton:hover {
                    color: #fff;
                    background: rgba(255,0,0,0.5);
                    border-radius: 12px;
                }
                """
            )
            close_btn.setFixedSize(32, 32)
            close_btn.clicked.connect(lambda checked=False, idx=i: self.on_close_tab(idx))
            tab_btn_layout.addWidget(close_btn)
            tab_btn.setLayout(tab_btn_layout)
            tab_btn.setFixedHeight(40)
            tab_btn.setStyleSheet(f"""
                background: {'rgba(33, 150, 243, 0.18);' if i == current_index else 'rgba(255,255,255,0.04)'};
                border-radius: 16px;
                margin: 2px 0;
                border: none;
            """)
            def make_tab_press(idx):
                def tab_press(event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        self.on_select_tab(idx)
                        self.hide_vertical_tab_popup()
                        self._popup_opened_by_click = False
                return tab_press
            tab_btn.mousePressEvent = make_tab_press(i)
            vlayout.addWidget(tab_btn)
        vlayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.vertical_tab_popup.setLayout(vlayout)
        self.vertical_tab_popup.setMouseTracking(True)
        self.vertical_tab_popup.installEventFilter(self)
        self.vertical_tab_popup.enterEvent = self._popup_enter
        self.vertical_tab_popup.leaveEvent = self._popup_leave

        btn_rect = self.vertical_tabs_btn.rect()
        btn_global = self.vertical_tabs_btn.mapToGlobal(btn_rect.topLeft())
        popup_width = 320
        popup_height = self.vertical_tab_popup.sizeHint().height()
        self.vertical_tab_popup.setFixedWidth(popup_width)
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

class SettingsDialog(QDialog):
    def __init__(self, parent, bottom_bar_height, current_bg_color):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedSize(340, 320)
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(18)

        # Detect dark mode
        is_dark_mode = QColor(current_bg_color).name().lower() in ["#181818", "#232323", "#18191a", "#000000"]

        # If dark mode, make all widgets in settings white
        if is_dark_mode:
            self.setStyleSheet("""
                QDialog {
                    background: #232323;
                }
                QLabel, QRadioButton, QPushButton {
                    color: white;
                    background: #232323;
                }
                QRadioButton::indicator {
                    background: white;
                    border: 1px solid #bbb;
                }
                QRadioButton::indicator:checked {
                    background: #2196f3;
                }
            """)
        else:
            self.setStyleSheet("")

        color_label = QLabel("Theme Color")
        color_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 4px;")
        layout.addWidget(color_label)

        self.color_buttons_layout = QHBoxLayout()
        self.dark_color_btn = QPushButton("Dark")
        self.dark_color_btn.setStyleSheet("""
            QPushButton {
                background-color: #181818; color: white; border-radius: 8px; padding: 8px 18px; font-size: 15px;
            }
            QPushButton:checked, QPushButton:pressed {
                background-color: #232323;
            }
        """)
        self.dark_color_btn.clicked.connect(lambda: self.parent()._update_background_color("#181818"))

        self.light_color_btn = QPushButton("Light")
        self.light_color_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0; color: #232323; border-radius: 8px; padding: 8px 18px; font-size: 15px;
            }
            QPushButton:checked, QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        self.light_color_btn.clicked.connect(lambda: self.parent()._update_background_color("#f0f0f0"))

        self.color_buttons_layout.addWidget(self.dark_color_btn)
        self.color_buttons_layout.addWidget(self.light_color_btn)
        layout.addLayout(self.color_buttons_layout)

        tab_mode_label = QLabel("Tab Layout")
        tab_mode_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px; margin-bottom: 4px;")
        layout.addWidget(tab_mode_label)
        self.tab_mode_group = QButtonGroup(self)
        self.horizontal_radio = QRadioButton("Horizontal Tabs (scrollable)")
        self.vertical_radio = QRadioButton("Vertical Tabs (Tabs button)")
        self.horizontal_radio.setStyleSheet("font-size: 15px; margin-bottom: 2px;")
        self.vertical_radio.setStyleSheet("font-size: 15px; margin-bottom: 2px;")
        self.tab_mode_group.addButton(self.horizontal_radio)
        self.tab_mode_group.addButton(self.vertical_radio)

        layout.addWidget(self.horizontal_radio)
        layout.addWidget(self.vertical_radio)

        current_mode = self.parent().config.get("tab_mode", "horizontal")
        if current_mode == "vertical":
            self.vertical_radio.setChecked(True)
        else:
            self.horizontal_radio.setChecked(True)

        self.tab_mode_group.buttonClicked.connect(self.on_tab_mode_changed)

        layout.addStretch(1)

        self.credit_btn = QPushButton("Credit")
        self.credit_btn.setStyleSheet("""
            QPushButton {
                background: #2196f3; color: white; border-radius: 8px; font-size: 15px; padding: 8px 18px;
            }
            QPushButton:hover {
                background: #1976d2;
            }
        """)
        layout.addWidget(self.credit_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.credit_btn.clicked.connect(self.open_credit_link)

        self.setLayout(layout)

        self.dark_color_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.light_color_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def open_credit_link(self):
        webbrowser.open("https://github.com/TopMyster/FluxBrowser/blob/main/README.md")

    def on_tab_mode_changed(self, btn):
        mode = "horizontal" if self.horizontal_radio.isChecked() else "vertical"
        self.parent().config["tab_mode"] = mode
        save_config(self.parent().config)
        self.parent().tab_bar.set_tab_mode(mode)
        self.parent().floating_bar.tab_bar.set_tab_mode(mode)
        # Save immediately so it persists on restart
        save_config(self.parent().config)

class HistoryDialog(QDialog):
    def __init__(self, parent, history_list):
        super().__init__(parent)
        self.setWindowTitle("Search History")
        self.setModal(True)
        self.setFixedSize(500, 400)
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        for url in reversed(history_list):
            item = QListWidgetItem(url)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
        self.list_widget.itemDoubleClicked.connect(self.open_url)
        self.selected_url = None

    def open_url(self, item):
        self.selected_url = item.text()
        self.accept()

class FloatingBar(QWidget):
    def __init__(self, parent, get_tab_titles, get_current_tab, on_select_tab, on_close_tab, on_new_tab, on_back, on_forward, on_search, on_settings, get_can_go_back, get_can_go_forward):
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
            backdrop-filter: blur(24px);
        """)

        nav_search_layout = QHBoxLayout(self.nav_search_background)
        nav_search_layout.setContentsMargins(8, 0, 8, 0)
        nav_search_layout.setSpacing(0)

        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(36, 36)
        self.plus_btn.setStyleSheet("background: transparent; color: white; font-size: 24px; border: none; margin:0; padding:0;")
        self.plus_btn.clicked.connect(on_new_tab)

        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(36, 36)
        self.back_btn.setStyleSheet("background: transparent; color: white; font-size: 24px; border: none; margin:0; padding:0;")
        self.back_btn.clicked.connect(on_back)

        self.forward_btn = QPushButton(">")
        self.forward_btn.setFixedSize(36, 36)
        self.forward_btn.setStyleSheet("background: transparent; color: white; font-size: 24px; border: none; margin:0; padding:0;")
        self.forward_btn.clicked.connect(on_forward)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search or enter URL...")
        self.search_bar.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border: none; border-radius: 12px; padding: 4px 8px; font-size: 16px; min-width: 60px; max-width: 180px;")
        self.search_bar.setFixedHeight(32)
        self.search_bar.returnPressed.connect(on_search)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setStyleSheet("background: transparent; color: white; font-size: 20px; border: none;")
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
            on_close_tab=on_close_tab
        )
        self.tab_bar.setFixedHeight(BAR_HEIGHT - 16)
        self.tab_bar.setStyleSheet(f"""
            background: rgba(50, 50, 50, 0.7);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(24px);
        """)

        nav_search_layout.addWidget(self.tab_bar.vertical_tabs_btn)
        self.tab_bar.vertical_tabs_btn.setVisible(self.tab_bar.tab_mode == "vertical")

        main_layout.addWidget(self.nav_search_background, stretch=1)
        main_layout.addWidget(self.tab_bar, stretch=0)
        self.setLayout(main_layout)

        self.get_can_go_back = get_can_go_back
        self.get_can_go_forward = get_can_go_forward

    def update_nav_buttons(self, text_color="white"):
        can_go_back = self.get_can_go_back()
        can_go_forward = self.get_can_go_forward()
        self.back_btn.setEnabled(can_go_back)
        self.forward_btn.setEnabled(can_go_forward)

        self.back_btn.setStyleSheet(
            f"background: transparent; color: {text_color}; font-size: 24px; border: none; margin:0; padding:0;" + (f"; opacity: 0.5;" if not can_go_back else "")
        )
        self.forward_btn.setStyleSheet(
            f"background: transparent; color: {text_color}; font-size: 24px; border: none; margin:0; padding:0;" + (f"; opacity: 0.5;" if not can_go_forward else "")
        )
        self.plus_btn.setStyleSheet(f"background: transparent; color: {text_color}; font-size: 24px; border: none; margin:0; padding:0;")
        self.settings_btn.setStyleSheet(f"background: transparent; color: {text_color}; font-size: 20px; border: none;")

class IsleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isle Browser")
        self.setGeometry(100, 100, 1350, 800)
        self.config = load_config()
        self.mode = "dynamic"
        self.history_list = []
        self.bottom_bar_height = self.config.get("bottom_bar_height", BOTTOM_BAR_DEFAULT)
        self._auto_hide_delay = 1200

        self.central_widget = QWidget()
        self.central_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.central_widget.setAutoFillBackground(True)

        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)

        self.tabs = []
        self.tab_titles = []
        self.current_tab = 0

        self.webview_container = QWidget()
        self.webview_layout = QVBoxLayout()
        self.webview_layout.setContentsMargins(0, 0, 0, 0)
        self.webview_layout.setSpacing(0)
        self.webview_container.setLayout(self.webview_layout)
        self.v_layout.addWidget(self.webview_container)

        self.controls_bar = QWidget()
        self.controls_bar.setFixedHeight(self.bottom_bar_height)
        self.controls_bar.setStyleSheet("background: transparent; border-radius: 20px;")

        bar_layout = QHBoxLayout()
        bar_layout.setContentsMargins(18, 4, 18, 4)
        bar_layout.setSpacing(10)

        self.controls_nav_search_background = QWidget(self.controls_bar)
        self.controls_nav_search_background.setFixedHeight(self.bottom_bar_height - 8)
        self.controls_nav_search_background.setStyleSheet("""
            background: rgba(50, 50, 50, 0.7);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(24px);
        """)

        controls_nav_search_layout = QHBoxLayout(self.controls_nav_search_background)
        controls_nav_search_layout.setContentsMargins(8, 0, 8, 0)
        controls_nav_search_layout.setSpacing(0)

        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(36, 36)
        self.plus_btn.setStyleSheet("background: transparent; color: white; font-size: 24px; border: none; margin:0; padding:0;")
        self.plus_btn.clicked.connect(self.add_tab_from_button)

        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(36, 36)
        self.back_btn.setStyleSheet("background: transparent; color: white; font-size: 24px; border: none; margin:0; padding:0;")
        self.back_btn.clicked.connect(self.go_back)

        self.forward_btn = QPushButton(">")
        self.forward_btn.setFixedSize(36, 36)
        self.forward_btn.setStyleSheet("background: transparent; color: white; font-size: 24px; border: none; margin:0; padding:0;")
        self.forward_btn.clicked.connect(self.go_forward)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search or enter URL...")
        self.search_bar.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border: none; border-radius: 12px; padding: 4px 8px; font-size: 16px; min-width: 60px; max-width: 180px;")
        self.search_bar.setFixedHeight(32)
        self.search_bar.returnPressed.connect(self.do_search)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setStyleSheet("background: transparent; color: white; font-size: 20px; border: none;")
        self.settings_btn.clicked.connect(self.show_settings)

        controls_nav_search_layout.addWidget(self.plus_btn)
        controls_nav_search_layout.addWidget(self.back_btn)
        controls_nav_search_layout.addWidget(self.forward_btn)
        controls_nav_search_layout.addSpacing(4)
        controls_nav_search_layout.addWidget(self.search_bar, stretch=1)
        controls_nav_search_layout.addSpacing(2)
        controls_nav_search_layout.addWidget(self.settings_btn)

        self.tab_bar = TabBar(
            get_tab_titles=lambda: self.tab_titles,
            get_current_tab=lambda: self.current_tab,
            on_select_tab=self.switch_tab,
            on_close_tab=self.close_tab
        )
        self.tab_bar.setFixedHeight(self.bottom_bar_height - 8)
        self.tab_bar.setStyleSheet(f"""
            background: rgba(50, 50, 50, 0.7);
            border-radius: 15px;
            backdrop-filter: blur(30px);
        """)
        self.tab_bar.set_tab_mode(self.config.get("tab_mode", "horizontal"))

        controls_nav_search_layout.addWidget(self.tab_bar.vertical_tabs_btn)
        self.tab_bar.vertical_tabs_btn.setVisible(self.tab_bar.tab_mode == "vertical")

        bar_layout.addWidget(self.controls_nav_search_background, stretch=1)
        bar_layout.addWidget(self.tab_bar, stretch=0)
        self.controls_bar.setLayout(bar_layout)
        self.v_layout.addWidget(self.controls_bar)
        self.central_widget.setLayout(self.v_layout)
        self.setCentralWidget(self.central_widget)

        self.floating_bar = FloatingBar(
            self,
            get_tab_titles=lambda: self.tab_titles,
            get_current_tab=lambda: self.current_tab,
            on_select_tab=self.switch_tab,
            on_close_tab=self.close_tab,
            on_new_tab=self.add_tab_from_button,
            on_back=self.go_back,
            on_forward=self.go_forward,
            on_search=self.do_search_dynamic,
            on_settings=self.show_settings,
            get_can_go_back=lambda: self.can_go_back() if self.tabs else False,
            get_can_go_forward=lambda: self.can_go_forward() if self.tabs else False
        )
        self.floating_bar.tab_bar.set_tab_mode(self.config.get("tab_mode", "horizontal"))
        self.floating_bar.hide()

        self.tab_buttons_bottom = []
        self.add_tab(None)
        self.apply_mode()
        self.update_tab_ui()

        self.shortcut_newtab_mac = QShortcut(QKeySequence("Meta+T"), self)
        self.shortcut_newtab_mac.activated.connect(self.add_tab_from_button)
        self.shortcut_newtab_win = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcut_newtab_win.activated.connect(self.add_tab_from_button)

        self.search_bar.textChanged.connect(self.update_search_bar_color)
        self.floating_bar.search_bar.textChanged.connect(self.update_search_bar_color)

        # Restore tab mode from config
        tab_mode = self.config.get("tab_mode", "horizontal")
        self.tab_bar.set_tab_mode(tab_mode)
        self.floating_bar.tab_bar.set_tab_mode(tab_mode)

    def update_search_bar_color(self, text):
        if text.startswith("ch/"):
            color = "#98ff98"
        elif text.startswith("isle/"):
            color = "#2196f3"
        else:
            color = "rgba(255,255,255,0.2)"
        self.search_bar.setStyleSheet(
            f"background: {color}; color: white; border: none; border-radius: 12px; padding: 4px 8px; font-size: 16px; min-width: 60px; max-width: 180px;"
        )
        self.floating_bar.search_bar.setStyleSheet(
            f"background: {color}; color: white; border: none; border-radius: 12px; padding: 4px 8px; font-size: 16px; min-width: 60px; max-width: 180px;"
        )

    def resizeEvent(self, event):
        self.update_tab_ui()
        self.position_floating_bar()
        super().resizeEvent(event)

    def position_floating_bar(self):
        bar_width = self.floating_bar.width()
        bar_height = self.floating_bar.height()
        x = (self.width() - bar_width) // 2
        y = self.height() - bar_height - 32
        self.floating_bar.move(x, y)
        self.floating_bar.raise_()

    def add_tab_from_button(self):
        self.add_tab(None)
        self.floating_bar.search_bar.setFocus()

    def do_search(self):
        text = self.search_bar.text().strip()
        self.handle_special_search(text)
        self.search_bar.clear()
        self.update_search_bar_color("")

    def do_search_dynamic(self):
        text = self.floating_bar.search_bar.text().strip()
        self.handle_special_search(text)
        self.floating_bar.search_bar.clear()
        self.update_search_bar_color("")

    def handle_special_search(self, text):
        if text.startswith("ch/"):
            query = text[3:].strip()
            if query:
                url = f"https://chat.openai.com/?q={QUrl.toPercentEncoding(query).data().decode()}"
                self.load_url_in_current_tab(url)
        elif text == "isle/sketch":
            self.show_sketch_tab()
        elif text == "isle/notes":
            self.show_notes_tab()
        elif text.startswith("isle/"):
            pass
        else:
            self.load_url_in_current_tab(text)

    def load_url_in_current_tab(self, url_string):
        if not self.tabs:
            self.add_tab(url_string)
            return

        current_tab_widget = self.tabs[self.current_tab]
        if current_tab_widget.is_notes or current_tab_widget.is_sketch:
            self.add_tab(url_string)
            return

        if not re.match(r'^[a-zA-Z]+://', url_string):
            if '.' in url_string and ' ' not in url_string:
                url_string = 'http://' + url_string
            else:
                url_string = 'https://www.google.com/search?q=' + QUrl.toPercentEncoding(url_string).data().decode()

        url = QUrl(url_string)
        current_tab_widget.setUrl(url)
        self.add_to_history(url_string)
        self.update_tab_ui()

    def add_to_history(self, url):
        if url and url not in self.history_list:
            self.history_list.append(url)

    def add_tab(self, url=None, is_sketch=False, is_notes=False):
        light_mode = self.palette().color(QPalette.ColorRole.Window).name().lower() == "#f0f0f0"
        new_tab = BrowserTab(url=url, sketch=is_sketch, notes=is_notes, light_mode=light_mode)
        self.tabs.append(new_tab)
        self.tab_titles.append(new_tab.title())
        self.webview_layout.addWidget(new_tab)
        new_tab.set_title_callback(lambda title, index=len(self.tabs) - 1: self._update_tab_title(index, title))
        new_tab.set_url_callback(lambda url, index=len(self.tabs) - 1: self._on_tab_url_changed(index, url))
        new_tab.set_page_load_callback(self._on_current_page_load)
        self.switch_tab(len(self.tabs) - 1)
        self.update_tab_ui()

        if hasattr(new_tab, 'webview'):
            new_tab.webview.page().setBackgroundColor(self.palette().color(QPalette.ColorRole.Window))

    def _update_tab_title(self, index, title):
        if 0 <= index < len(self.tab_titles):
            self.tab_titles[index] = title if title else "New Tab"
            self.update_tab_ui()

    def _on_tab_url_changed(self, index, url):
        if index == self.current_tab:
            self.update_address_bar(url.toString())
            self.update_nav_buttons()
            self.add_to_history(url.toString())

    def _on_current_page_load(self):
        if self.current_tab < len(self.tabs) and hasattr(self.tabs[self.current_tab], 'webview'):
            current_tab_widget = self.tabs[self.current_tab]
            if current_tab_widget.is_home:
                self.update_address_bar("")
            else:
                self.update_address_bar(current_tab_widget.url())
            self.update_nav_buttons()

    def update_address_bar(self, url_text):
        self.search_bar.setText(url_text)
        self.floating_bar.search_bar.setText(url_text)

    def switch_tab(self, index):
        if 0 <= index < len(self.tabs):
            if self.current_tab < len(self.tabs) and self.tabs[self.current_tab] is not None:
                self.tabs[self.current_tab].hide()

            self.current_tab = index
            self.tabs[self.current_tab].show()
            if self.tabs[self.current_tab].parentWidget() != self.webview_container:
                 self.webview_layout.addWidget(self.tabs[self.current_tab])

            current_tab_url = self.tabs[self.current_tab].url()

            if self.tabs[self.current_tab].is_home:
                self.search_bar.setText("")
                self.floating_bar.search_bar.setText("")
            else:
                self.search_bar.setText(current_tab_url)
                self.floating_bar.search_bar.setText(current_tab_url)

            self.setWindowTitle("Isle Browser")
            self.update_tab_ui()
            self.update_nav_buttons()

            if hasattr(self.tabs[self.current_tab], 'webview'):
                self.tabs[self.current_tab].webview.page().setBackgroundColor(self.palette().color(QPalette.ColorRole.Window))

    def close_tab(self, index):
        if len(self.tabs) == 1:
            QApplication.quit()
            return

        tab_to_close = self.tabs.pop(index)
        self.tab_titles.pop(index)
        tab_to_close.deleteLater()

        if self.current_tab == index:
            if index > 0:
                self.switch_tab(index - 1)
            else:
                self.switch_tab(0)
        elif self.current_tab > index:
            self.current_tab -= 1
            self.update_tab_ui()
        else:
            self.update_tab_ui()

        if self.current_tab < len(self.tabs):
            self.update_address_bar(self.tabs[self.current_tab].url())
        else:
            self.update_address_bar("")

        self.update_nav_buttons()

    def update_tab_ui(self):
        self.tab_bar.update_tabs()
        self.floating_bar.tab_bar.update_tabs()

    def go_back(self):
        if self.current_tab < len(self.tabs):
            self.tabs[self.current_tab].back()

    def go_forward(self):
        if self.current_tab < len(self.tabs):
            self.tabs[self.current_tab].forward()

    def can_go_back(self):
        if self.current_tab < len(self.tabs) and hasattr(self.tabs[self.current_tab], 'webview') and not self.tabs[self.current_tab].is_home:
            return self.tabs[self.current_tab].webview.history().canGoBack()
        return False

    def can_go_forward(self):
        if self.current_tab < len(self.tabs) and hasattr(self.tabs[self.current_tab], 'webview') and not self.tabs[self.current_tab].is_home:
            return self.tabs[self.current_tab].webview.history().canGoForward()
        return False

    def update_nav_buttons(self, text_color="white"):
        can_go_back = self.can_go_back()
        can_go_forward = self.can_go_forward()
        self.back_btn.setEnabled(can_go_back)
        self.forward_btn.setEnabled(can_go_forward)

        self.back_btn.setStyleSheet(
            f"background: transparent; color: {text_color}; font-size: 24px; border: none; margin:0; padding:0;" + (f"; opacity: 0.5;" if not can_go_back else "")
        )
        self.forward_btn.setStyleSheet(
            f"background: transparent; color: {text_color}; font-size: 24px; border: none; margin:0; padding:0;" + (f"; opacity: 0.5;" if not can_go_forward else "")
        )
        self.plus_btn.setStyleSheet(f"background: transparent; color: {text_color}; font-size: 24px; border: none; margin:0; padding:0;")
        self.settings_btn.setStyleSheet(f"background: transparent; color: {text_color}; font-size: 20px; border: none;")

        self.floating_bar.update_nav_buttons(text_color)

    def show_settings(self):
        current_bg_color = self.palette().color(QPalette.ColorRole.Window).name()
        dialog = SettingsDialog(self, self.bottom_bar_height, current_bg_color)
        dialog.exec()

    def _update_bottom_bar_size(self):
        self.controls_bar.setFixedHeight(self.bottom_bar_height)
        self.controls_nav_search_background.setFixedHeight(self.bottom_bar_height - 8)
        self.tab_bar.setFixedHeight(self.bottom_bar_height - 8)
        self.config["bottom_bar_height"] = self.bottom_bar_height
        save_config(self.config)

    def apply_mode(self):
        self._update_background_color("#181818")
        self.controls_bar.hide()
        self.floating_bar.show()
        self.position_floating_bar()

    def _update_background_color(self, hex_color=None):
        if hex_color is None:
            hex_color = self.palette().color(QPalette.ColorRole.Window).name()

        base_color = QColor(hex_color)
        luminance = (0.299 * base_color.red() + 0.587 * base_color.green() + 0.114 * base_color.blue()) / 255

        if luminance > 0.5:
            text_color = "black"
            bar_bg_rgba = f"rgba(200, 200, 200, 0.7)"
            bar_border_rgba = "rgba(0, 0, 0, 0.1)"
            light_mode = True
        else:
            text_color = "white"
            bar_bg_rgba = f"rgba(50, 50, 50, 0.7)"
            bar_border_rgba = "rgba(255, 255, 255, 0.2)"
            light_mode = False

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, base_color)
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text_color))
        self.setPalette(palette)
        self.setStyleSheet(f"background: {base_color.name()};")

        self.controls_bar.setStyleSheet("background: transparent;")
        self.controls_nav_search_background.setStyleSheet(f"""
            background: {bar_bg_rgba};
            border-radius: 20px;
            border: 1px solid {bar_border_rgba};
            backdrop-filter: blur(24px);
        """)
        self.tab_bar.setStyleSheet(f"""
            background: {bar_bg_rgba};
            border-radius: 20px;
            backdrop-filter: blur(24px);
        """)

        self.search_bar.setStyleSheet(f"background: rgba(255,255,255,0.2); color: {text_color}; border: none; border-radius: 12px; padding: 4px 8px; font-size: 16px; min-width: 60px; max-width: 180px;")
        self.update_nav_buttons(text_color)

        self.floating_bar.nav_search_background.setStyleSheet(f"""
            background: {bar_bg_rgba};
            border-radius: 20px;
            border: 1px solid {bar_border_rgba};
            backdrop-filter: blur(24px);
        """)
        self.floating_bar.tab_bar.setStyleSheet(f"""
            background: {bar_bg_rgba};
            border-radius: 20px;
            backdrop-filter: blur(24px);
        """)
        self.floating_bar.search_bar.setStyleSheet(f"background: rgba(255,255,255,0.2); color: {text_color}; border: none; border-radius: 12px; padding: 4px 8px; font-size: 16px; min-width: 60px; max-width: 180px;")
        self.floating_bar.update_nav_buttons(text_color)

        for tab in self.tabs:
            if hasattr(tab, 'webview'):
                tab.webview.page().setBackgroundColor(base_color)
            if hasattr(tab, 'home'):
                tab.home.set_light_mode(light_mode)

    def show_history_dialog(self):
        history_dialog = HistoryDialog(self, self.history_list)
        if history_dialog.exec() == QDialog.DialogCode.Accepted:
            selected_url = history_dialog.selected_url
            if selected_url:
                self.load_url_in_current_tab(selected_url)

    def show_notes_tab(self):
        self.add_tab(is_notes=True)

    def show_sketch_tab(self):
        self.add_tab(is_sketch=True)

    def open_mini_player(self):
        if self.current_tab < len(self.tabs) and hasattr(self.tabs[self.current_tab], 'webview') and not self.tabs[self.current_tab].is_home:
            current_url = self.tabs[self.current_tab].url()
            if current_url:
                mini_player = MiniPlayer(current_url, self)
                mini_player.exec()

    def closeEvent(self, event):
        self.config["mode"] = self.mode
        self.config["bottom_bar_height"] = self.bottom_bar_height
        # Save tab mode on close
        self.config["tab_mode"] = self.tab_bar.tab_mode
        save_config(self.config)
        super().closeEvent(event)

if __name__ == "__main__":
    print("Starting Isle Browser application...")
    app = QApplication(sys.argv)
    app.setApplicationName("Isle Browser")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    app.setStyleSheet("""
        QPushButton {
            border: none;
            padding: 8px 12px;
            border-radius: 8px;
            background-color: #555;
            color: white;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #666;
        }
        QPushButton:pressed {
            background-color: #444;
        }
        QPushButton:disabled {
            background-color: #333;
            color: #888;
        }
    """)

    window = IsleBrowser()
    window.show()
    print("Isle Browser window created and shown.")
    sys.exit(app.exec())
