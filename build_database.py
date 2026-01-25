"""
Build the CLIP reference database for AI image detection.

Instructions:
1. Add real photos to: reference_images/real/
2. Add AI-generated images to: reference_images/ai/
3. Run this script to build the database

The more images you add (10-20 each minimum), the better the accuracy.
"""

import os
import sys
sys.path.insert(0, '.')

from modules.clip_detector import CLIPDetector

def main():
    print("=" * 50)
    print("CLIP Reference Database Builder")
    print("=" * 50)

    # Paths
    base_path = os.path.dirname(os.path.abspath(__file__))
    real_folder = os.path.join(base_path, "reference_images", "real")
    ai_folder = os.path.join(base_path, "reference_images", "ai")
    db_path = os.path.join(base_path, "clip_database.pkl")

    # Check folders exist
    if not os.path.exists(real_folder):
        os.makedirs(real_folder)
        print(f"Created: {real_folder}")

    if not os.path.exists(ai_folder):
        os.makedirs(ai_folder)
        print(f"Created: {ai_folder}")

    # Count images
    real_count = len([f for f in os.listdir(real_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    ai_count = len([f for f in os.listdir(ai_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])

    print(f"\nFound {real_count} real images")
    print(f"Found {ai_count} AI images")

    if real_count < 5 or ai_count < 5:
        print("\n" + "=" * 50)
        print("NOT ENOUGH IMAGES!")
        print("=" * 50)
        print(f"\nPlease add at least 5 images to each folder:")
        print(f"  Real photos: {real_folder}")
        print(f"  AI images:   {ai_folder}")
        print("\nTip: Add 10-20 images of each type for better accuracy")
        return

    # Initialize detector
    print("\nInitializing CLIP detector...")
    detector = CLIPDetector()

    # Add real images
    print(f"\nProcessing real images from: {real_folder}")
    detector.add_reference_folder(real_folder, is_ai=False)

    # Add AI images
    print(f"\nProcessing AI images from: {ai_folder}")
    detector.add_reference_folder(ai_folder, is_ai=True)

    # Save database
    detector.save_database(db_path)

    # Summary
    stats = detector.get_stats()
    print("\n" + "=" * 50)
    print("DATABASE BUILT SUCCESSFULLY!")
    print("=" * 50)
    print(f"Real images:  {stats['real_count']}")
    print(f"AI images:    {stats['ai_count']}")
    print(f"Total:        {stats['total']}")
    print(f"\nSaved to: {db_path}")
    print("\nYou can now run screen_monitor_clip.py")


if __name__ == "__main__":
    main()
