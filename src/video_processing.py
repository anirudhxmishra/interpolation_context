import cv2 as cv
import numpy as np
import os
from tqdm import tqdm
from typing import Tuple # <--- 1. IMPORT TUPLE

def calculate_motion_scores(video_path: str) -> Tuple[np.ndarray, float]: # <--- 2. USE TUPLE HERE
    """
    Analyzes a video to generate a time-series of motion intensity scores.

    This function iterates through the video, calculates the dense optical flow
    between consecutive frames, and computes the mean magnitude of the flow
    vectors as a motion score for each frame transition.

    Args:
        video_path (str): The full path to the input video file.

    Returns:
        A tuple containing:
        - np.ndarray: An array of motion scores, one for each frame transition.
        - float: The frames per second (fps) of the video.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    try:
        cap = cv.VideoCapture(video_path)
        frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv.CAP_PROP_FPS)

        if not cap.isOpened():
            raise IOError("Cannot open video file.")
            
        ret, prev_frame = cap.read()
        if not ret:
            raise IOError("Could not read the first frame of the video.")
        
        prev_gray = cv.cvtColor(prev_frame, cv.COLOR_BGR2GRAY)
        
        scores = []
        
        # tqdm shows a progress bar in the console
        with tqdm(total=frame_count - 1, desc="Calculating Motion Scores") as pbar:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                flow = cv.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                magnitude, _ = cv.cartToPolar(flow[..., 0], flow[..., 1])
                frame_score = np.mean(magnitude)
                scores.append(frame_score)
                
                prev_gray = gray
                pbar.update(1)

        cap.release()
        
        print(f"Motion scores calculated for {len(scores)} frames.")
        return np.array(scores), fps

    except Exception as e:
        if 'cap' in locals() and cap.isOpened():
            cap.release()
        raise IOError(f"An error occurred during video processing: {e}")

if __name__ == '__main__':
    # This is a test block to run the function directly
    try:
        test_video_path = "../data/test_match.mp4" 
        motion_scores, video_fps = calculate_motion_scores(test_video_path)
        
        print("\n--- Motion Analysis Complete ---")
        print(f"Total scores calculated: {len(motion_scores)}")
        print(f"Video FPS: {video_fps}")
        print(f"Sample scores (first 10): {np.round(motion_scores[:10], 2)}")
        
    except (FileNotFoundError, IOError) as e:
        print(f"Error: {e}")