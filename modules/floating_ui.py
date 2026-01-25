import tkinter as tk


class FloatingControlPanel:
    """Floating control panel for the screen monitor"""

    def __init__(self, root, monitor_controller):
        self.root = root
        self.monitor = monitor_controller

        # Create floating window
        self.window = tk.Toplevel(root)
        self.window.title("AI Monitor")
        self.window.attributes('-topmost', True)
        self.window.resizable(False, False)

        # Position in bottom-right corner
        self.window.geometry("250x180+100+100")

        self._create_widgets()

    def _create_widgets(self):
        """Create the control panel widgets"""
        # Main frame
        main_frame = tk.Frame(self.window, bg="#2c3e50", padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = tk.Label(
            main_frame,
            text="AI Image Monitor",
            font=("Arial", 12, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack(pady=(0, 10))

        # Status indicator
        status_frame = tk.Frame(main_frame, bg="#2c3e50")
        status_frame.pack(fill=tk.X, pady=5)

        self.status_dot = tk.Canvas(status_frame, width=12, height=12, bg="#2c3e50", highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 5))
        self.status_dot.create_oval(2, 2, 10, 10, fill="#95a5a6", outline="")

        self.status_label = tk.Label(
            status_frame,
            text="Stopped",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#95a5a6"
        )
        self.status_label.pack(side=tk.LEFT)

        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg="#2c3e50")
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(
            btn_frame,
            text="Start Monitoring",
            command=self._toggle_monitoring,
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            width=18,
            cursor="hand2"
        )
        self.start_btn.pack(pady=2)

        # Test button
        test_btn = tk.Button(
            btn_frame,
            text="Test Alert",
            command=self._test_alert,
            font=("Arial", 9),
            bg="#3498db",
            fg="white",
            width=18,
            cursor="hand2"
        )
        test_btn.pack(pady=2)

        # Stats label
        self.stats_label = tk.Label(
            main_frame,
            text="Detections: 0",
            font=("Arial", 9),
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        self.stats_label.pack(pady=(5, 0))

    def _toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if self.monitor.is_monitoring():
            self.monitor.stop_monitoring()
            self._update_status(False)
        else:
            self.monitor.start_monitoring()
            self._update_status(True)
            self._update_stats_loop()

    def _update_status(self, is_running):
        """Update the status indicator"""
        if is_running:
            self.status_dot.delete("all")
            self.status_dot.create_oval(2, 2, 10, 10, fill="#27ae60", outline="")
            self.status_label.config(text="Monitoring...", fg="#27ae60")
            self.start_btn.config(text="Stop Monitoring", bg="#e74c3c")
        else:
            self.status_dot.delete("all")
            self.status_dot.create_oval(2, 2, 10, 10, fill="#95a5a6", outline="")
            self.status_label.config(text="Stopped", fg="#95a5a6")
            self.start_btn.config(text="Start Monitoring", bg="#27ae60")

    def _test_alert(self):
        """Test the alert overlay"""
        if self.monitor.overlay:
            self.monitor.overlay.show_alert(duration=2000)

    def _update_stats_loop(self):
        """Update statistics display"""
        if self.monitor.is_monitoring():
            stats = self.monitor.get_stats()
            self.stats_label.config(
                text=f"Detections: {stats['ai_detections_count']} | Scans: {stats['total_analyses']}"
            )
            self.window.after(1000, self._update_stats_loop)

    def bring_to_front(self):
        """Bring window to front"""
        self.window.lift()
        self.window.attributes('-topmost', True)
