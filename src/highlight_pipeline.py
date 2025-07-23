# highlight_pipeline.py

import os
import argparse
from pathlib import Path
from frame_interpolation import RIFEEnhancer
import subprocess # <-- This was the missing import

class HighlightGenerator:
    def __init__(self, rife_path: str, ffmpeg_path: str):
        self.enhancer = RIFEEnhancer(rife_path, ffmpeg_path)

    def generate_highlights(self, video_path: str, output_dir: str):
        print("🎬 Starting RIFE test...")
        os.makedirs(output_dir, exist_ok=True)
        enhanced_path = os.path.join(output_dir, "rife_test_output.mp4")
        print(f"✨ Testing RIFE enhancement on: {video_path}")

        try:
            result = self.enhancer.enhance_clip(video_path, enhanced_path)
            print(f"✅ RIFE test completed: {result}")
            return result
        except Exception as e:
            print(f"❌ Error: {e}")
            if isinstance(e, subprocess.CalledProcessError):
                print("--- Subprocess Error Details ---")
                print(f"Stderr: {e.stderr}")
                print(f"Stdout: {e.stdout}")
            return None

def main():
    parser = argparse.ArgumentParser(description="RIFE Enhancement Test")
    parser.add_argument("--ffmpeg", required=True, help="Full path to the ffmpeg.exe executable")
    parser.add_argument("--rife", required=True, help="Path to the RIFE model directory")
    parser.add_argument("--video", required=True, help="Input video path")
    parser.add_argument("--output", default="output", help="Output directory")

    args = parser.parse_args()

    generator = HighlightGenerator(args.rife, args.ffmpeg)
    result = generator.generate_highlights(args.video, args.output)

    if result:
        print(f"✅ Processing complete: {result}")
    else:
        print("❌ Processing failed")

if __name__ == "__main__":
    main()