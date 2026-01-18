import struct
import time
import sys
import subprocess
import os
import contextlib
import pyaudio
import pvporcupine
import config
import math
from PyQt6.QtCore import QThread, pyqtSignal

@contextlib.contextmanager
def ignore_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

class ClapDetector:
    def __init__(self, pyaudio_instance=None):
        self.chunk = config.CHUNK_SIZE
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = config.SAMPLE_RATE
        self.p = pyaudio_instance if pyaudio_instance else pyaudio.PyAudio()

    def get_loudness(self, data):
        count = len(data) // 2
        shorts = struct.unpack(f"{count}h", data)
        sum_squares = 0.0
        for sample in shorts:
            sum_squares += sample * sample
        if count == 0: return 0
        rms = (sum_squares / count) ** 0.5
        return rms

    def listen_for_claps(self, timeout=config.ACTIVE_DURATION):
        if config.DEBUG_MODE:
            print(f"[DEBUG] Listening for claps for {timeout} seconds...")

        try:
            with ignore_stderr():
                stream = self.p.open(format=self.format,
                                     channels=self.channels,
                                     rate=self.rate,
                                     input=True,
                                     frames_per_buffer=self.chunk)
        except Exception as e:
            print(f"[ERROR] Could not open audio stream for clap detection: {e}")
            return 0

        start_time = time.time()
        try:
            while (time.time() - start_time) < timeout:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                except Exception as e:
                    print(f"[ERROR] Audio read error: {e}")
                    break
                loudness = self.get_loudness(data)
                if loudness > config.CLAP_THRESHOLD:
                    if config.DEBUG_MODE:
                        print(f"[DEBUG] First clap detected! (Loudness: {loudness:.2f})")
                    return self._count_subsequent_claps(stream)
            return 0
        finally:
            with ignore_stderr():
                stream.stop_stream()
                stream.close()

    def _count_subsequent_claps(self, stream):
        clap_count = 1
        start_time = time.time()
        last_clap = start_time
        while (time.time() - start_time) < config.CLAP_INTERVAL:
            try:
                data = stream.read(self.chunk, exception_on_overflow=False)
                if self.get_loudness(data) > config.CLAP_THRESHOLD:
                    now = time.time()
                    if (now - last_clap) > 0.15: 
                        clap_count += 1
                        last_clap = now
                        if config.DEBUG_MODE:
                            print(f"[DEBUG] Subsequent clap: {clap_count}")
            except Exception:
                break
        return clap_count

    def close(self):
        pass

class VoiceLauncher(QThread):
    wake_detected = pyqtSignal()      
    listening_claps = pyqtSignal()    
    success = pyqtSignal()            
    audio_level = pyqtSignal(float)   
    log_signal = pyqtSignal(str)      
    
    def __init__(self):
        super().__init__()
        self.pa = pyaudio.PyAudio()
        self.clap_detector = ClapDetector(self.pa)
        self.porcupine = None
        self.audio_stream = None
        self.is_running = True
        self.is_paused = False
        
        if not config.PORCUPINE_ACCESS_KEY:
             self.log_signal.emit("ERROR: Porcupine Key Missing")
             sys.exit(1)

        try:
            self.porcupine = pvporcupine.create(
                access_key=config.PORCUPINE_ACCESS_KEY,
                keywords=[config.DEFAULT_WAKE_WORD]
            )
        except Exception as e:
            print(f"[ERROR] Error initializing Porcupine: {e}")
            sys.exit(1)

    def play_sound(self, sound_key):
        """Plays a system sound asynchronously."""
        path = config.SOUNDS.get(sound_key)
        if path and os.path.exists(path):
            try:
                subprocess.Popen(["afplay", path], stderr=subprocess.DEVNULL)
            except Exception:
                pass
                
    def speak(self, text):
        """Speaks text using macOS native TTS."""
        try:
            # -v Daniel is the British English voice (Jarvis-like)
            subprocess.Popen(["say", "-v", "Daniel", text], stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def pause(self):
        self.is_paused = True
        self.log_signal.emit("Microphone: DISCONNECTED")
        
    def resume(self):
        self.is_paused = False
        self.log_signal.emit("Microphone: CONNECTED")
            
    def setup_audio_stream(self):
        if self.audio_stream and self.audio_stream.is_active(): return
        if not self.pa:
            self.pa = pyaudio.PyAudio()
            self.clap_detector.p = self.pa
        try:
            with ignore_stderr():
                self.audio_stream = self.pa.open(
                    rate=self.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=self.porcupine.frame_length
                )
        except Exception as e:
            self.log_signal.emit(f"Mic Error: {e}")

    def execute_command(self, app_config):
        cmd = app_config.get("command")
        args = app_config.get("args", [])
        msg = app_config.get("type_msg", "Executing command")
        try:
            self.log_signal.emit(f"Running: {msg}")
            print(f"[{msg}]...")
            full_command = [cmd] + args
            subprocess.Popen(full_command)
        except Exception as e:
            self.log_signal.emit(f"Exec Error: {e}")

    def launch_apps(self):
        print(f"Executing Double Clap Action")
        for app_config in config.APPS_TO_LAUNCH:
            self.execute_command(app_config)

    def trigger_triple_action(self):
        print("Executing Triple Clap Action")
        self.execute_command(config.SECONDARY_ACTION)
        
    def stop(self):
        self.is_running = False

    def run(self):
        print("==" * 30)
        self.log_signal.emit(f"System Online. Listening for '{config.DEFAULT_WAKE_WORD}'...")
        self.play_sound("startup")
        
        self.setup_audio_stream()
        
        while self.is_running:
            if self.is_paused:
                if self.audio_stream:
                    with ignore_stderr():
                        self.audio_stream.stop_stream()
                        self.audio_stream.close()
                    self.audio_stream = None
                if self.pa:
                    self.pa.terminate()
                    self.pa = None
                time.sleep(0.5)
                continue
            else:
                if not self.audio_stream:
                    self.setup_audio_stream()

            try:
                try:
                    pcm_bytes = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                except Exception:
                    continue
                
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm_bytes)
                rms = math.sqrt(sum(x**2 for x in pcm) / len(pcm))
                level = min(rms / 5000.0, 1.0)
                self.audio_level.emit(level)
                
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    self.log_signal.emit("Wake Word Detected!")
                    self.wake_detected.emit()
                    self.speak(config.WAKE_RESPONSE) # Replaced play_sound("wake")
                    
                    if self.audio_stream:
                        self.audio_stream.stop_stream()
                        self.audio_stream.close()
                        self.audio_stream = None
                    
                    try:
                        self.listening_claps.emit()
                        num_claps = self.clap_detector.listen_for_claps(timeout=config.ACTIVE_DURATION)
                        self.log_signal.emit(f"Claps Detected: {num_claps}")
                        
                        if num_claps == 2:
                            self.play_sound("success")
                            self.log_signal.emit("Action: Double Clap")
                            self.success.emit()
                            self.launch_apps()
                        elif num_claps == 3:
                            self.play_sound("success")
                            self.log_signal.emit("Action: Triple Clap")
                            self.success.emit()
                            self.trigger_triple_action()
                        else:
                            self.log_signal.emit("Ignored.")
                            self.play_sound("error")
                            
                    finally:
                        self.log_signal.emit("Resuming Watch...")
                        self.setup_audio_stream()

            except Exception:
                 if not self.audio_stream:
                      self.setup_audio_stream()
            except KeyboardInterrupt:
                break
                
        if self.porcupine: self.porcupine.delete()
        if self.audio_stream: self.audio_stream.close()
        if self.pa: self.pa.terminate()
