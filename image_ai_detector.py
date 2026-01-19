import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import base64
import io
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class ImageAIDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Image Detection Tool")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Variables
        self.image_path = None
        self.current_image = None
        self.api_key = os.getenv('ANTHROPIC_API_KEY')

        # Check API key
        if not self.api_key:
            messagebox.showerror("Error", "ANTHROPIC_API_KEY not found in .env file")

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🔍 AI-Generated Image Detector",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)

        # Main container
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Upload section
        upload_frame = tk.Frame(main_frame, bg="#ecf0f1")
        upload_frame.pack(pady=10)

        self.upload_btn = tk.Button(
            upload_frame,
            text="📁 Select Image",
            command=self.upload_image,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        self.analyze_btn = tk.Button(
            upload_frame,
            text="🔬 Analyze Image",
            command=self.analyze_image,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=5)

        # Image preview section
        preview_frame = tk.LabelFrame(
            main_frame,
            text="Image Preview",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        preview_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(
            preview_frame,
            text="No image selected",
            bg="white",
            fg="#95a5a6",
            font=("Arial", 12)
        )
        self.image_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Results section
        results_frame = tk.LabelFrame(
            main_frame,
            text="Analysis Results",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        results_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Results text with scrollbar
        results_container = tk.Frame(results_frame, bg="white")
        results_container.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(results_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text = tk.Text(
            results_container,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="white",
            fg="#2c3e50",
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)

        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            bg="#34495e",
            fg="white",
            font=("Arial", 9),
            anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def upload_image(self):
        """Handle image file selection"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select an image",
            filetypes=file_types
        )

        if filename:
            self.image_path = filename
            self.display_image(filename)
            self.analyze_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"Loaded: {os.path.basename(filename)}")
            self.results_text.delete(1.0, tk.END)

    def display_image(self, path):
        """Display the selected image in the preview area"""
        try:
            # Open and resize image
            image = Image.open(path)

            # Calculate resize to fit preview area (max 400x300)
            max_width, max_height = 400, 300
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Update label
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def encode_image(self, image_path):
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image(self):
        """Analyze the image using Claude Vision API"""
        if not self.image_path:
            messagebox.showwarning("Warning", "Please select an image first")
            return

        if not self.api_key:
            messagebox.showerror("Error", "API key not configured")
            return

        # Update UI
        self.status_label.config(text="Analyzing image...")
        self.analyze_btn.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Analyzing image, please wait...\n")
        self.root.update()

        try:
            # Get image format
            image_extension = os.path.splitext(self.image_path)[1].lower()
            media_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp'
            }
            media_type = media_type_map.get(image_extension, 'image/jpeg')

            # Encode image
            image_data = self.encode_image(self.image_path)

            # Prepare the prompt
            prompt = """You are an expert at detecting AI-generated images, 3D renders, and distinguishing them from real photographs. Analyze this image in extreme detail.

Look for these SPECIFIC indicators:

**AI-Generated Image Artifacts:**
- Unnatural symmetry or repetitive patterns
- Weird hands, fingers, or facial features
- Inconsistent lighting sources or shadow directions
- Blurry or malformed text
- Impossible reflections or perspectives
- Unnatural skin texture or hair strands
- Background elements that don't make logical sense
- Objects merging unnaturally into each other
- Unusual color gradients or saturation

**3D Render Indicators:**
- Perfectly clean surfaces with no dust, wear, or imperfections
- Overly perfect geometry and straight lines
- Unrealistic material properties (too glossy, too matte, too perfect)
- Artificial lighting that's too evenly distributed
- Lack of natural randomness (everything looks placed intentionally)
- No lens artifacts like chromatic aberration or subtle blur
- Perfectly placed objects with no natural chaos
- Materials that look "CG-like" rather than real-world weathered

**Real Photograph Indicators:**
- Natural imperfections, dust, scratches, wear and tear
- Realistic depth of field and lens characteristics
- Natural lighting with complex interactions
- Random elements and organic chaos
- Realistic material aging and weathering
- Natural color variations and noise
- Authentic shadows with proper penumbra
- Lens artifacts (slight distortion, vignetting)

**Your Analysis Must Include:**
1. **CONCLUSION**: State clearly: "AI-Generated", "3D Render", "Real Photograph", or "Uncertain"
2. **CONFIDENCE**: Give percentage (0-100%)
3. **EVIDENCE**: List 5-7 specific visual elements you observed
4. **KEY INDICATORS**: What were the strongest tells?
5. **REASONING**: Explain your logic step by step

Be brutally honest and detailed. If something looks even slightly artificial, call it out specifically."""

            # Make API call
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 2048,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": image_data
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                }
            )

            if response.status_code == 200:
                data = response.json()
                result_text = data['content'][0]['text']

                # Display results
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, result_text)

                self.status_label.config(text="Analysis complete")
            else:
                error_msg = f"API Error: Status {response.status_code}\n{response.text[:200]}"
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, error_msg)
                self.status_label.config(text="Analysis failed")

        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, error_msg)
            self.status_label.config(text="Error occurred")
            messagebox.showerror("Error", error_msg)

        finally:
            self.analyze_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = ImageAIDetector(root)
    root.mainloop()


if __name__ == "__main__":
    main()
