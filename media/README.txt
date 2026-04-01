Extract a video into sequential PNG frames in this directory.

Use zero-padded filenames so playback order sorts correctly, for example:

000001.png
000002.png
000003.png

The sidebar scans this directory for every `.png` file and loops them in lexical order.

Sample command line invocation:

    brew install yt-dlp
    yt-dlp <url>
    ffmpeg -i 'video.webm' -vf "fps=30" "%06d.png"
    # Then let it run for however long you want extracted