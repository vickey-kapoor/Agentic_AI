import os
import tkinter as tk
from dotenv import load_dotenv
import sys

# Import custom modules
from modules.ai_detector_core import AIDetectorCore
from modules.screen_capture import ScreenCapture
from modules.image_cache import ImageCache
from modules.monitor_controller import MonitorController
from modules.floating_ui import FloatingControlPanel
from modules.overlay_window import OverlayWindow


class ScreenMonitorApp:
    """Main application for floating AI media detector"""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Create hidden root window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        self.root.title("AI Monitor")

        # Load API key
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            self.show_error_and_exit("ANTHROPIC_API_KEY not found in .env file")
            return

        # Initialize components
        print("Initializing AI Media Monitor...")
        print(f"Using model: claude-3-5-haiku-latest")

        try:
            # Core components
            self.ai_detector = AIDetectorCore(self.api_key)
            self.screen_capture = ScreenCapture()
            self.image_cache = ImageCache(max_size=100, ttl=300)  # 5 minute TTL

            # Create overlay window
            self.overlay = OverlayWindow(self.root)

            # Create monitor controller (control_panel will be set later)
            self.monitor = MonitorController(
                self.ai_detector,
                self.screen_capture,
                self.image_cache,
                self.overlay
            )

            # Create floating control panel
            self.control_panel = FloatingControlPanel(self.root, self.monitor)

            # Link control panel to monitor (for showing detection snapshots)
            self.monitor.control_panel = self.control_panel

            # Set up window close handler
            self.control_panel.window.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Bring control panel to front (Windows-specific)
            try:
                self.control_panel.bring_to_front()
                # Force window to be topmost
                self.control_panel.window.focus_force()
            except Exception as e:
                print(f"Note: Could not bring window to front: {e}")

            print("Initialization complete!")
            print("\nWelcome to AI Media Monitor!")
            print("=" * 50)
            print("This tool monitors your screen and alerts you")
            print("when AI-generated images or 3D renders are detected.")
            print("\nInstructions:")
            print("1. Click 'Start Monitoring' in the control panel")
            print("2. Browse normally (Facebook, Instagram, etc.)")
            print("3. Watch for red border when AI content is detected")
            print("=" * 50)

        except Exception as e:
            self.show_error_and_exit(f"Initialization error: {str(e)}")

    def on_closing(self):
        """Handle clean shutdown"""
        print("\nShutting down...")

        # Stop monitoring if active
        if self.monitor.is_monitoring():
            self.monitor.stop_monitoring()

        # Show final statistics
        stats = self.monitor.get_stats()
        print("\n" + "=" * 50)
        print("SESSION SUMMARY")
        print("=" * 50)
        print(f"Total screen captures: {stats['total_captures']}")
        print(f"Total analyses: {stats['total_analyses']}")
        print(f"AI detections: {stats['ai_detections_count']}")
        print(f"Cache hit rate: {stats['cache_hit_rate']:.1f}%")
        print("=" * 50)

        # Destroy windows
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

    def show_error_and_exit(self, message):
        """Show error message and exit"""
        print(f"\nERROR: {message}")
        try:
            from tkinter import messagebox
            messagebox.showerror("Error", message)
        except:
            pass
        sys.exit(1)

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            self.on_closing()


def main():
    """Main entry point"""
    print("\n" + "=" * 50)
    print("AI MEDIA DETECTOR - Floating Monitor")
    print("=" * 50)
    print("Detects AI-generated images in real-time")
    print("while you browse social media")
    print("=" * 50 + "\n")

    app = ScreenMonitorApp()
    app.run()


if __name__ == "__main__":
    main()
