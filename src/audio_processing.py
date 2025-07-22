import librosa
import numpy as np
from moviepy.editor import VideoFileClip
import os
import tempfile

def detect_audio_peaks(video_path: str, delta: float = 2, wait: int = 560) -> np.ndarray:
    """
    Analyzes the audio track of a video to find timestamps of high-energy events.

    This function extracts the audio, computes an onset strength envelope which acts as
    a proxy for excitement (e.g., crowd roars), and then picks the most prominent
    peaks from that envelope.

    Args:
        video_path (str): The full path to the input video file.
        delta (float): A threshold for peak picking. Higher values make detection less sensitive.
        wait (int): The number of frames to wait after a peak before detecting another.

    Returns:
        np.ndarray: An array of timestamps (in seconds) corresponding to the detected audio peaks.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    # Use a temporary directory to handle the extracted audio file
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = os.path.join(temp_dir, "temp_audio.wav")

        try:
            # 1. Extract audio from the video file
            print("Extracting audio...")
            with VideoFileClip(video_path) as video:
                video.audio.write_audiofile(audio_path, codec='pcm_s16le') # Use a standard WAV codec
        except Exception as e:
            raise IOError(f"Error extracting audio from video: {e}")

        # 2. Load the audio signal
        print("Loading audio and computing onset strength...")
        try:
            y, sr = librosa.load(audio_path)
        except Exception as e:
            raise IOError(f"Error loading audio file with librosa: {e}")

        # 3. Compute the onset strength envelope
        hop_length = 512
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

        # 4. Detect peaks in the envelope
        print("Detecting peaks...")
        peaks = librosa.util.peak_pick(
            onset_env,
            pre_max=40, post_max=800,
            pre_avg=7, post_avg=7,
            delta=delta,
            wait=wait
        )

        # 5. Convert peak frames to timestamps
        peak_times = librosa.frames_to_time(peaks, sr=sr, hop_length=hop_length)
        print(f"Found {len(peak_times)} audio peaks.")

        return peak_times

if __name__ == '__main__':
    # This is a test block to run the function directly
    # Make sure to adjust the path to your test video
    try:
        # Example usage:
        # Assumes this script is in 'src' and the video is in 'data'
        test_video_path = "data/test_match.mp4" 
        
        # Use the parameters you found during tuning in the notebook
        tuned_delta = 2
        tuned_wait = 560
        
        timestamps = detect_audio_peaks(test_video_path, delta=tuned_delta, wait=tuned_wait)
        
        print("\n--- Final Detected Timestamps (seconds) ---")
        print(np.round(timestamps, 2))
        
    except (FileNotFoundError, IOError) as e:
        print(f"Error: {e}")