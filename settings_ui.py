from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QSlider, QPushButton, QGroupBox, QMessageBox, QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt
import config

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis Command Center")
        self.setFixedSize(500, 600) # Slightly wider
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
            }
            QTabWidget::pane {
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                background: #1E1E1E;
            }
            QTabBar::tab {
                background: #2D2D2D;
                color: #888;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #007AFF;
                color: white;
            }
            QGroupBox {
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                margin-top: 20px;
                font-weight: bold;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #007AFF;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #2D2D2D;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 8px;
                color: white;
            }
            QPushButton {
                background-color: #3A3A3A;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton#PrimaryBtn {
                background-color: #007AFF;
            }
            QPushButton#PrimaryBtn:hover {
                background-color: #0062CC;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3A3A3A;
                height: 8px;
                background: #2D2D2D;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007AFF;
                border: 1px solid #007AFF;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(main_layout)
        
        # === Header ===
        header = QLabel("JARVIS SYSTEMS")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #007AFF; letter-spacing: 2px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # === Tabs ===
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- TAB 1: DASHBOARD ---
        self.dash_tab = QWidget()
        dash_layout = QVBoxLayout()
        self.dash_tab.setLayout(dash_layout)
        
        # Microphone Control
        mic_group = QGroupBox("Control")
        mic_layout = QHBoxLayout()
        self.mic_btn = QPushButton("Microphone: ON")
        self.mic_btn.setObjectName("PrimaryBtn")
        self.mic_btn.setCheckable(True)
        self.mic_btn.setChecked(True)
        self.mic_btn.setStyleSheet("background-color: #34C759; color: white; border: none; padding: 10px;")
        self.mic_btn.toggled.connect(self.update_mic_style)
        mic_layout.addWidget(self.mic_btn)

        self.test_btn = QPushButton("Test Action")
        self.test_btn.setStyleSheet("background-color: #5856D6; color: white; border: none; padding: 10px;")
        mic_layout.addWidget(self.test_btn)
        
        mic_group.setLayout(mic_layout)
        dash_layout.addWidget(mic_group)

        # Sensitivity
        audio_group = QGroupBox("Sensors")
        audio_layout = QVBoxLayout()
        audio_layout.addWidget(QLabel("Clap Sensitivity (500-5000):"))
        audio_layout.addWidget(QLabel("Lower = More Sensitive to noise.", objectName="desc"))
        
        slider_layout = QHBoxLayout()
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(100, 5000)
        self.threshold_slider.setValue(int(config.CLAP_THRESHOLD))
        self.threshold_label = QLabel(str(config.CLAP_THRESHOLD))
        self.threshold_label.setStyleSheet("font-weight: bold; width: 40px;")
        self.threshold_slider.valueChanged.connect(lambda v: self.threshold_label.setText(str(v)))
        slider_layout.addWidget(self.threshold_slider)
        slider_layout.addWidget(self.threshold_label)
        audio_layout.addLayout(slider_layout)
        audio_group.setLayout(audio_layout)
        dash_layout.addWidget(audio_group)

        # Log
        log_group = QGroupBox("System Log")
        log_layout = QVBoxLayout()
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("font-family: monospace; font-size: 11px; background-color: #111;")
        self.log_console.setPlaceholderText("Initializing systems...")
        log_layout.addWidget(self.log_console)
        log_group.setLayout(log_layout)
        dash_layout.addWidget(log_group)
        
        self.tabs.addTab(self.dash_tab, "Dashboard")
        
        # --- TAB 2: ENGINE (ADVANCED) ---
        self.engine_tab = QWidget()
        engine_layout = QVBoxLayout()
        self.engine_tab.setLayout(engine_layout)
        
        wake_group = QGroupBox("Neuro-Linguistic Engine")
        wake_layout = QVBoxLayout()
        wake_layout.setSpacing(10)
        
        wake_layout.addWidget(QLabel("Access Key (Required):"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Paste Porcupine Key")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setText(config.PORCUPINE_ACCESS_KEY)
        self.key_input.setToolTip("Your API Key from PicoVoice Console")
        wake_layout.addWidget(self.key_input)
        
        wake_layout.addWidget(QLabel("Wake Word Model:"))
        self.wake_combo = QComboBox()
        self.wake_combo.addItems(config.AVAILABLE_WAKE_WORDS)
        current_wake = config.DEFAULT_WAKE_WORD.lower()
        index = self.wake_combo.findText(current_wake)
        if index >= 0: self.wake_combo.setCurrentIndex(index)
        wake_layout.addWidget(self.wake_combo)
        
        # Explanation Label
        info_label = QLabel(
            "Note: The Access Key is your license to use the voice engine.\n"
            "The Wake Word is the name Jarvis listens for."
        )
        info_label.setStyleSheet("color: #888; font-size: 11px; font-style: italic;")
        info_label.setWordWrap(True)
        wake_layout.addWidget(info_label)
        
        wake_group.setLayout(wake_layout)
        engine_layout.addWidget(wake_group)
        engine_layout.addStretch()
        
        self.tabs.addTab(self.engine_tab, "Engine Config")
        
        # === Save Button (Global) ===
        self.save_btn = QPushButton("Save & Reboot Systems")
        self.save_btn.setObjectName("PrimaryBtn")
        self.save_btn.clicked.connect(self.save_settings)
        main_layout.addWidget(self.save_btn)

    def update_mic_style(self, checked):
        if checked:
            self.mic_btn.setText("Microphone: ON")
            self.mic_btn.setStyleSheet("background-color: #34C759; color: white; border: none; padding: 10px;")
        else:
            self.mic_btn.setText("Microphone: OFF")
            self.mic_btn.setStyleSheet("background-color: #FF3B30; color: white; border: none; padding: 10px;")

    def log(self, message):
        """Append message to console"""
        self.log_console.append(message)
        # Scroll to bottom
        sb = self.log_console.verticalScrollBar()
        sb.setValue(sb.maximum())
        
    def save_settings(self):
        # 1. Update In-Memory Config
        new_conf = config._config_data.copy()
        
        # Update Key
        new_conf["porcupine_access_key"] = self.key_input.text().strip()
        
        # Update Wake Word
        new_conf["system"]["wake_word"] = self.wake_combo.currentText()
        
        # Update Threshold
        new_conf["audio"]["clap_threshold"] = self.threshold_slider.value()
        
        # 2. Save to JSON
        config.save_config(new_conf)
        
        # 3. Reload Module
        config.reload()
        
        QMessageBox.information(self, "Saved", "Settings saved successfully!\nRun './start_gui.sh' again if you changed the Wake Word engine.")
        self.close()
