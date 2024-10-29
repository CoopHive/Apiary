<!-- ffmpeg -i xyz.mov -vf "fps=4,scale=1300:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" xyz.gif -->

# Bundle

![](Bundle.gif)
