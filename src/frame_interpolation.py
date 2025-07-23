# frame_interpolation.py

import os
import subprocess
import tempfile
from moviepy.editor import VideoFileClip
from pathlib import Path
import sys

class RIFEEnhancer:
    def __init__(self, rife_path: str, ffmpeg_path: str = "ffmpeg"):
        self.rife_path = rife_path
        self.inference_script = os.path.join(rife_path, "inference_video.py")
        self.ffmpeg_path = ffmpeg_path  # <-- Path to ffmpeg.exe

        if not os.path.isdir(self.rife_path):
            raise FileNotFoundError(f"RIFE directory not found at: {self.rife_path}")
        if not os.path.isfile(self.inference_script):
            raise FileNotFoundError(f"RIFE inference script not found at: {self.inference_script}")

    def enhance_clip(self, input_clip_path: str, output_path: str) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_frames_dir = os.path.join(temp_dir, "input_frames")
            output_frames_dir = os.path.join(temp_dir, "output_frames")
            os.makedirs(input_frames_dir)
            os.makedirs(output_frames_dir)

            print("Decomposing video into frames...")
            self._extract_frames(input_clip_path, input_frames_dir)
            
            print("Running RIFE inference for 4x interpolation...")
            self._run_rife_inference(input_frames_dir, output_frames_dir)
            
            print("Recomposing enhanced frames into video...")
            self._recompose_video(output_frames_dir, output_path)
            
            return output_path

    def _extract_frames(self, video_path: str, frames_dir: str):
        # Use the direct path to ffmpeg
        cmd = [self.ffmpeg_path, "-i", video_path, os.path.join(frames_dir, "frame_%04d.png")]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

    def _run_rife_inference(self, input_dir: str, output_dir: str):
        cmd = [sys.executable, self.inference_script, "--img", input_dir, "--exp", "2", "--png", "--output", output_dir]
        subprocess.run(cmd, cwd=self.rife_path, check=True, capture_output=True, text=True)

    def _recompose_video(self, frames_dir: str, output_path: str):
        # Use the direct path to ffmpeg
        cmd = [self.ffmpeg_path, "-framerate", "30", "-i", os.path.join(frames_dir, "frame_%04d.png"),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", output_path]
        subprocess.run(cmd, check=True, capture_output=True, text=True)