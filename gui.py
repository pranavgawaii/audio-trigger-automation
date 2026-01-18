from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget, QLabel, 
                             QVBoxLayout, QGraphicsOpacityEffect)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QColor, QPainter, QRadialGradient, QBrush, QPen
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QRectF, QTimer, pyqtProperty, QSequentialAnimationGroup, QPointF
import sys
from voice_launcher import VoiceLauncher

import subprocess
import random

class PulseOrb(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(80, 80) # Increased size for rings
        self._color = QColor("#007AFF")
        self._pulse_scale = 0.8
        self._rotation = 0.0
        self._anim_group = None
        self._is_breathing = False 

    @pyqtProperty(float)
    def pulse_scale(self):
        return self._pulse_scale

    @pulse_scale.setter
    def pulse_scale(self, value):
        self._pulse_scale = value
        self.update()

    @pyqtProperty(float)
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.update()

    def set_color(self, hex_color):
        self._color = QColor(hex_color)
        self.update()

    def start_pulse(self):
        self._is_breathing = True
        if self._anim_group and self._anim_group.state() == QPropertyAnimation.State.Running:
            return
            
        self._anim_group = QSequentialAnimationGroup(self) # Actually ParallelGroup needed, but we can just star 2 anims
        
        # Pulse Animation
        anim_pulse = QPropertyAnimation(self, b"pulse_scale")
        anim_pulse.setDuration(1200)
        anim_pulse.setStartValue(0.8)
        anim_pulse.setEndValue(1.0)
        anim_pulse.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim_pulse.setLoopCount(-1) 
        anim_pulse.setKeyValues([(0.0, 0.8), (0.5, 0.95), (1.0, 0.8)])
        
        # Rotation Animation
        anim_rot = QPropertyAnimation(self, b"rotation")
        anim_rot.setDuration(2000)
        anim_rot.setStartValue(0.0)
        anim_rot.setEndValue(360.0)
        anim_rot.setLoopCount(-1)
        
        # We need to store them to stop later
        self._anims = [anim_pulse, anim_rot]
        for a in self._anims:
            a.start()

    def stop_pulse(self):
        self._is_breathing = False
        if hasattr(self, '_anims'):
            for a in self._anims:
                a.stop()
        self._pulse_scale = 0.8
        self._rotation = 0.0
        self.update()

    def set_audio_level(self, level):
        if self._is_breathing:
            if hasattr(self, '_anims'):
                # Pause pulse but keep rotation? Or pause both?
                # Let's pause pulse only
                self._anims[0].pause() # Index 0 is pulse
            
            target_scale = 0.8 + (level * 0.7)
            self._pulse_scale = target_scale
            self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = QPointF(self.rect().center())
        max_radius = min(self.width(), self.height()) / 2.0
        
        # 1. Draw Core Pulse
        current_radius = max_radius * 0.7 * self._pulse_scale # 70% of size is core
        
        gradient = QRadialGradient(center.x(), center.y(), current_radius)
        gradient.setColorAt(0.0, self._color) 
        c_transparent = QColor(self._color)
        c_transparent.setAlpha(0)
        gradient.setColorAt(1.0, c_transparent)
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, current_radius, current_radius)
        
        # Solid Core
        core_radius = max_radius * 0.3
        painter.setBrush(self._color)
        painter.drawEllipse(center, core_radius, core_radius)
        
        # 2. Draw Sci-Fi Rings
        # Save state to rotate canvas
        painter.save()
        painter.translate(center)
        painter.rotate(self._rotation)
        
        pen_color = QColor(self._color)
        pen_color.setAlpha(200)
        painter.setPen(Qt.PenStyle.SolidLine)
        
        # Outer Ring (Broken)
        ring_radius = max_radius * 0.85
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(pen_color)
        
        # Draw 3 arcs
        # drawPie/drawArc expects rectangle
        rect = QRectF(-ring_radius, -ring_radius, ring_radius*2, ring_radius*2)
        # Using drawArc with a Pen would be lines. Using drawPie is wedges.
        # Let's use Pen for Arcs.
        pen = QPen(pen_color)
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Angles are in 1/16th of a degree
        painter.drawArc(rect, 0 * 16, 60 * 16)
        painter.drawArc(rect, 120 * 16, 60 * 16)
        painter.drawArc(rect, 240 * 16, 60 * 16)
        
        # Inner Ring (Reverse Rotation - simplified by just static relative to outer or diff speed)
        # For simple effect, just another ring offset
        painter.rotate(45) # Offset
        inner_rect = QRectF(-ring_radius*0.7, -ring_radius*0.7, ring_radius*1.4, ring_radius*1.4)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawEllipse(inner_rect)
        
        painter.restore()

class HUDOverlay(QWidget):
    # ... (Keep existing init) ...
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.layout.setContentsMargins(0, 25, 20, 0)
        self.setLayout(self.layout)
        
        self.orb = PulseOrb()
        self.layout.addWidget(self.orb)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
    
    # ... (Keep existing methods show/hide/update) ...
    def show_listening(self):
        self.orb.set_color("#007AFF")
        self.orb.start_pulse()
        self.show()
        self.animate_fade(0.0, 1.0)

    def show_success(self):
        self.orb.stop_pulse()
        self.orb.set_color("#34C759")
        self.orb.pulse_scale = 1.0 
        QTimer.singleShot(1500, self.hide_orb)

    def hide_orb(self):
        self.orb.stop_pulse()
        self.animate_fade(1.0, 0.0, hide_after=True)
    
    def update_volume(self, level):
        self.orb.set_audio_level(level)

    def animate_fade(self, start, end, hide_after=False):
        try:
            if self.anim: self.anim.stop()
        except AttributeError: pass

        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        if hide_after:
            self.anim.finished.connect(self.hide)
        self.anim.start()

from settings_ui import SettingsWindow

class AudioAutomationApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        self.settings_window = None

        self.tray_icon = QSystemTrayIcon(self)
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor("#007AFF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 16, 16)
        painter.end()
        self.tray_icon.setIcon(QIcon(pixmap))
        
        self.tray_menu = QMenu()
        self.status_action = QAction("Status: Online", self)
        self.status_action.setEnabled(False) 
        self.tray_menu.addAction(self.status_action)
        self.tray_menu.addSeparator()
        
        self.settings_action = QAction("Settings...", self)
        self.settings_action.triggered.connect(self.open_settings)
        self.tray_menu.addAction(self.settings_action)
        
        self.test_hud_action = QAction("Test HUD (Toggle)", self)
        self.test_hud_action.triggered.connect(self.toggle_test_hud)
        self.tray_menu.addAction(self.test_hud_action)
        self.tray_menu.addSeparator()

        self.quit_action = QAction("Quit Jarvis", self)
        self.quit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        self.hud = HUDOverlay()
        self.thread = VoiceLauncher()
        self.thread.wake_detected.connect(self.set_listening_state)
        # self.thread.listening_claps.connect(self.set_listening_state) # Duplicate causing double speak
        self.thread.success.connect(self.set_success_state)
        self.thread.audio_level.connect(self.hud.update_volume)
        self.thread.log_signal.connect(self.log_message)
        self.thread.start()
        
        # Initial State
        self.reset_state()
        
        # Open UI on startup so user sees something happening
        try:
            self.open_settings()
        except Exception as e:
            print(f"CRITICAL ERROR Opening Settings: {e}")
            import traceback
            traceback.print_exc()
            
        print("GUI Application Started")
        
    def create_icon(self, color):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 16, 16)
        painter.end()
        return QIcon(pixmap)

    def log_message(self, msg):
        if self.settings_window:
            self.settings_window.log(msg)

    def set_listening_state(self):
        self.log_message("State: LISTENING")
        self.tray_icon.setIcon(self.create_icon("#007AFF"))
        self.hud.show_listening()
        # Fast Response: Play pre-generated file
        self.play_local_sound("yes_sir.aiff")

    def open_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
            self.settings_window.log("Console Initialized.")
            self.settings_window.log(f"Wake Word: {config.DEFAULT_WAKE_WORD}")
            # Connect Mic Toggle
            self.settings_window.mic_btn.toggled.connect(self.toggle_microphone)
            self.settings_window.test_btn.clicked.connect(self.trigger_test_action)
        
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def toggle_microphone(self, enabled):
        if enabled:
            self.thread.resume()
            self.tray_icon.setIcon(self.create_icon("#007AFF")) # Blue
        else:
            self.thread.pause()
            self.tray_icon.setIcon(self.create_icon("#FF3B30")) # Red

    def trigger_test_action(self):
        self.log_message("Testing Double Clap Action...")
        self.thread.launch_apps()

    def set_listening_state(self):
        self.log_message("State: LISTENING")
        self.tray_icon.setIcon(self.create_icon("#007AFF"))
        self.hud.show_listening()
        # Fast Response: Play pre-generated file
        self.play_local_sound("yes_sir.aiff")

    def set_success_state(self):
        self.log_message("State: SUCCESS - Action Triggered")
        self.tray_icon.setIcon(self.create_icon("#34C759"))
        self.hud.show_success()
        # Removed verbose speech ("Executing protocol") as requested
        self.play_system_sound("Glass") 
        QTimer.singleShot(2000, self.reset_state)

    def speak(self, text):
        try:
            subprocess.Popen(["say", text])
        except Exception as e:
            print(f"Error speaking: {e}")

    def play_system_sound(self, sound_name):
        try:
            subprocess.Popen(["afplay", f"/System/Library/Sounds/{sound_name}.aiff"])
        except Exception as e:
            print(f"Error playing sound: {e}")

    def play_local_sound(self, filename):
        try:
            # Assumes file is in the current directory
            subprocess.Popen(["afplay", filename])
        except Exception as e:
            print(f"Error playing local sound: {e}")

    def reset_state(self):
        # White for proper visibility on Menu Bar (handles Dark Mode better than Black)
        self.tray_icon.setIcon(self.create_icon("#FFFFFF"))
        # Or standard gray
        self.tray_icon.setIcon(self.create_icon("#8E8E93")) # System Gray

    def open_settings(self):
        if self.settings_window:
            self.settings_window.close()
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def toggle_test_hud(self):
        if self.hud.isVisible():
            self.hud.hide_orb()
        else:
            self.hud.show_listening()

    def quit_app(self):
        print("Quitting application...")
        self.thread.stop()
        self.thread.wait()
        self.quit()

if __name__ == "__main__":
    app = AudioAutomationApp(sys.argv)
    sys.exit(app.exec())
