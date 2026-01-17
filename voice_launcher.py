import struct
import time
import sys
import subprocess
import os
import contextlib
import pyaudio
import pvporcupine
import config

# Context manager to suppress stderr (C-level)
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
    def __init__(self):
        self.chunk = config.CHUNK_SIZE
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = config.SAMPLE_RATE
        self.p = pyaudio.PyAudio()

    def get_loudness(self, data):
        # Convert binary data to integers
        count = len(data) // 2
        shorts = struct.unpack(f"{count}h", data)
        sum_squares = 0.0
        for sample in shorts:
            sum_squares += sample * sample
        
        if count == 0:
            return 0
            
        rms = (sum_squares / count) ** 0.5
        return rms

    def listen_for_claps(self, timeout=config.ACTIVE_DURATION):
        """
        Listens for claps. Returns the number of claps detected (0, 1, 2, 3...)
        """
        if config.DEBUG_MODE:
            print(f"[DEBUG] Listening for claps for {timeout} seconds...")

        try:
            # Suppress potential audio device warnings here too
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
                    # Once first clap is detected, start counting for the specific window
                    return self._count_subsequent_claps(stream)
            
            return 0

        finally:
            with ignore_stderr():
                stream.stop_stream()
                stream.close()

    def _count_subsequent_claps(self, stream):
        """
        Called after the first clap is detected. Counts how many total claps occur within the window.
        Returns the total count (including the first one).
        """
        clap_count = 1
        start_time_of_sequence = time.time()
        last_clap_time = start_time_of_sequence
        
        # We listen for CLAP_INTERVAL seconds starting from the first clap
        while (time.time() - start_time_of_sequence) < config.CLAP_INTERVAL:
            try:
                data = stream.read(self.chunk, exception_on_overflow=False)
                loudness = self.get_loudness(data)
                
                if loudness > config.CLAP_THRESHOLD:
                    current_time = time.time()
                    # 150ms debounce
                    if (current_time - last_clap_time) > 0.15: 
                        clap_count += 1
                        last_clap_time = current_time
                        if config.DEBUG_MODE:
                            print(f"[DEBUG] Subsequent clap detected! (Total: {clap_count})")
            except Exception as e:
                print(f"Error reading audio stream: {e}")
                break
        
        return clap_count

    def close(self):
        self.p.terminate()

class VoiceLauncher:
    def __init__(self):
        self.clap_detector = ClapDetector()
        self.porcupine = None
        self.audio_stream = None
        self.pa = pyaudio.PyAudio()
        
        if not config.PORCUPINE_ACCESS_KEY:
             print("\n" + "!" * 60)
             print("ERROR: Porcupine AccessKey is missing in config.py")
             print("Please get a key from https://console.picovoice.ai/ and add it.")
             print("!" * 60 + "\n")
             sys.exit(1)

        try:
            # Try to initialize Porcupine
            self.porcupine = pvporcupine.create(
                access_key=config.PORCUPINE_ACCESS_KEY,
                keywords=[config.DEFAULT_WAKE_WORD]
            )
        except ValueError as e:
            print(f"[ERROR] Porcupine initialization failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Error initializing Porcupine: {e}")
            if "validation" in str(e).lower() or "accesskey" in str(e).lower():
                 print("Please ensure you have a valid PORCUPINE_ACCESS_KEY in config.py.")
            sys.exit(1)
            
    def setup_audio_stream(self):
        """Opens a fresh audio stream for Porcupine."""
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
            print(f"[ERROR] Could not open audio stream for wake word detection: {e}")
            sys.exit(1)

    def execute_command(self, app_config):
        cmd = app_config.get("command")
        args = app_config.get("args", [])
        msg = app_config.get("type_msg", "Executing command")
        
        try:
            print(f"[{msg}]...")
            full_command = [cmd] + args
            # Using subprocess.Popen to not block execution
            subprocess.Popen(full_command)
        except Exception as e:
            print(f"Failed to execute {cmd}: {e}")

    def launch_apps(self):
        print(f"Executing Double Clap Action: Launching apps...")
        for app_config in config.APPS_TO_LAUNCH:
            self.execute_command(app_config)

    def trigger_triple_action(self):
        print("Executing Triple Clap Action...")
        self.execute_command(config.SECONDARY_ACTION)

    def run(self):
        print("==" * 30)
        print(f"System Online. Wake word: '{config.DEFAULT_WAKE_WORD}'")
        print("Waiting for wake word...")
        print("==" * 30)
        
        # Initial stream setup
        self.setup_audio_stream()

        try:
            while True:
                # Read audio frame
                try:
                    pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                except IOError:
                    # Sometimes overflow happens, ignore
                    continue
                
                # Unpack struct to tuple of ints
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                # Process with Porcupine
                keyword_index = self.porcupine.process(pcm)

                if keyword_index >= 0:
                    print(f"\n[{time.strftime('%H:%M:%S')}] Wake word '{config.DEFAULT_WAKE_WORD}' detected!")
                    print(f"Listening for claps for {config.ACTIVE_DURATION} seconds...")
                    
                    # COMPLETELY CLOSE the stream to release the mic for ClapDetector
                    # This prevents the "PaMacCore" -50 error and sync issues
                    if self.audio_stream:
                        with ignore_stderr():
                            self.audio_stream.close()
                        self.audio_stream = None
                    
                    try:
                        # Listen for claps
                        num_claps = self.clap_detector.listen_for_claps(timeout=config.ACTIVE_DURATION)
                        
                        print(f"Sequence finished. Total claps detected: {num_claps}")
                        
                        if num_claps == 2:
                            print("Double detected! Launching apps.")
                            self.launch_apps()
                        elif num_claps == 3:
                            print("Triple clap detected! Triggering secondary action.")
                            self.trigger_triple_action()
                        else:
                            print("No valid clap pattern detected or action ignored.")
                            
                    finally:
                        # Re-open a FRESH stream for wake word listening
                        print("\nResuming wake word listening...")
                        self.setup_audio_stream()

        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            if self.porcupine:
                self.porcupine.delete()
            if self.audio_stream:
                self.audio_stream.close()
            if self.pa:
                self.pa.terminate()
            if self.clap_detector:
                self.clap_detector.close()

if __name__ == "__main__":
    app = VoiceLauncher()
    app.run()
