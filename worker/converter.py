import ffmpeg

(
    ffmpeg
    .input('static/videos/in/video1693623765.mp4')
    .filter('fps', fps=15)
    .output('video1693623765.avi', vcodec='h264', crf=28, preset='fast', movflags='faststart', pix_fmt='yuv420p')
    .run()
)