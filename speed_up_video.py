
from moviepy.editor import VideoFileClip

def speed_up_video(input_video_path, output_video_path, speed_factor=2):
    # Load the video file
    video_clip = VideoFileClip(input_video_path)
    
    # Speed up the video
    new_clip = video_clip.speedx(factor=speed_factor)
    
    # Write the resulting video to the output file
    new_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

# Example usage
input_video_path = 'demo.mov'
output_video_path = 'demo_2x.mov'
speed_up_video(input_video_path, output_video_path)
