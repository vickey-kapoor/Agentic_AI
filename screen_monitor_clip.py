"""
AI Image Detection Screen Monitor - Deepfake Detection
Uses fine-tuned SigLIP model for 94%+ accuracy
"""

import os
import tkinter as tk
from dotenv import load_dotenv
import sys

from modules.deepfake_detector import DeepfakeDetector
from modules.screen_capture import ScreenCapture
from modules.image_cache import ImageCache
from modules.floating_ui import FloatingControlPanel
from modules.overlay_window import OverlayWindow

# Import monitor controller but we'll create a modified version
import threading
import time
from PIL import Image


class MonitorController:
    """Monitor controller using deepfake detection"""

    def __init__(self, detector, screen_capture, image_cache, overlay):
        self.detector = detector
        self.screen_capture = screen_capture
        self.image_cache = image_cache
        self.overlay = overlay

        self._monitoring = False
        self._monitor_thread = None
        self._interval = 3
        self.control_panel = None

        self.stats = {
            'total_captures': 0,
            'total_analyses': 0,
            'ai_detections_count': 0,
            'cache_hits': 0
        }

    def start_monitoring(self):
        if self._monitoring:
            return
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("Monitoring started...")

    def stop_monitoring(self):
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        print("Monitoring stopped.")

    def is_monitoring(self):
        return self._monitoring

    def _monitor_loop(self):
        while self._monitoring:
            try:
                screenshot = self.screen_capture.capture_screen()
                self.stats['total_captures'] += 1

                # Resize for processing
                screenshot_small = screenshot.copy()
                screenshot_small.thumbnail((512, 512), Image.Resampling.LANCZOS)

                # Check cache
                cached = self.image_cache.get(screenshot_small)
                if cached:
                    self.stats['cache_hits'] += 1
                    time.sleep(self._interval)
                    continue

                # Analyze with deepfake detector
                print(f"Analyzing capture #{self.stats['total_captures']}...")
                result = self.detector.analyze_image(screenshot_small)
                self.stats['total_analyses'] += 1

                self.image_cache.set(screenshot_small, result)

                is_ai = result.get('is_ai', False)
                confidence = result.get('confidence', 0)
                verdict = result.get('verdict', 'Unknown')

                if is_ai:
                    print(f"AI DETECTED! Confidence: {confidence*100:.0f}%")
                    self.stats['ai_detections_count'] += 1
                else:
                    print(f"REAL IMAGE. Confidence: {confidence*100:.0f}%")

                # Show overlay
                self._show_result(is_ai, verdict, confidence)

            except Exception as e:
                print(f"Error: {e}")

            time.sleep(self._interval)

    def _show_result(self, is_ai, verdict, confidence):
        try:
            if self.overlay and self.overlay.root:
                self.overlay.root.after(
                    0,
                    lambda: self.overlay.show_result(is_ai, verdict, confidence)
                )
        except Exception as e:
            print(f"Overlay error: {e}")

    def get_stats(self):
        stats = self.stats.copy()
        total = stats['total_analyses']
        hits = stats['cache_hits']
        stats['cache_hit_rate'] = (hits / (total + hits) * 100) if (total + hits) > 0 else 0
        return stats


class ScreenMonitor:
    """Main application using deepfake detection"""

    def __init__(self):
        load_dotenv()

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("AI Image Detector")

        print("=" * 50)
        print("AI IMAGE DETECTOR - Deepfake Edition")
        print("=" * 50)
        print("Using SigLIP model (94.44% accuracy)")
        print("=" * 50)

        try:
            # Initialize deepfake detector
            print("\nInitializing detector...")
            self.detector = DeepfakeDetector()

            # Initialize other components
            self.screen_capture = ScreenCapture()
            self.image_cache = ImageCache(max_size=50, ttl=300)
            self.overlay = OverlayWindow(self.root)

            # Create monitor controller
            self.monitor = MonitorController(
                self.detector,
                self.screen_capture,
                self.image_cache,
                self.overlay
            )

            # Create control panel
            self.control_panel = FloatingControlPanel(self.root, self.monitor)
            self.monitor.control_panel = self.control_panel

            self.control_panel.window.protocol("WM_DELETE_WINDOW", self.on_closing)

            print("\nReady! Click 'Start Monitoring' to begin.")
            print("=" * 50)

        except Exception as e:
            print(f"Error: {e}")
            self._show_error(str(e))

    def _show_error(self, message):
        from tkinter import messagebox
        messagebox.showerror("Error", message)

    def on_closing(self):
        print("\nShutting down...")
        if hasattr(self, 'monitor') and self.monitor.is_monitoring():
            self.monitor.stop_monitoring()

        stats = self.monitor.get_stats() if hasattr(self, 'monitor') else {}
        print("\n" + "=" * 50)
        print("SESSION SUMMARY")
        print("=" * 50)
        print(f"Total captures: {stats.get('total_captures', 0)}")
        print(f"Total analyses: {stats.get('total_analyses', 0)}")
        print(f"AI detections: {stats.get('ai_detections_count', 0)}")
        print("=" * 50)

        try:
            self.overlay.destroy()
        except:
            pass
        try:
            self.control_panel.window.destroy()
        except:
            pass

        self.root.quit()
        self.root.destroy()

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()


def main():
    app = ScreenMonitor()
    app.run()


if __name__ == "__main__":
    main()
