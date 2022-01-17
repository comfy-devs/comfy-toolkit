# Nyan Anime (Toolkit)

## Description
This is a toolkit with all kinds of scripts used for managing Nyan Anime.

## Stack
Other: <a href="https://www.docker.com/">Docker<a>  

## Docker Hint
Building is done with <code>docker-compose build</code>.  
Running is done with <code>docker-compose run nyananime-toolkit /bin/bash</code>.  
Shutting down is with <code>docker-compose down</code>.
> 1) Edit volumes in <code>docker-compose.yml</code>, to mount whatever folders you want  

## Scripts included
| Script                                                                    | Description                                             |
| ------------------------------------------------------------------------- | ------------------------------------------------------- |
| `process-series`                                                          | Used for processing anime series, in a GUI like form.   |
| `check-compability`                                                       | idk why that exists actually lol.                       |
| `ffmpeg-video-xx-x264 <source_file> <number>`                             | Processes a single episode with libx264.                |
| `ffmpeg-video-vp9 <source_file> <number> <min_rate> <rate> <max_rate>`    | Processes a single episode with libvpx-vp9.             |
| `ffmpeg-thumbnail <source_file> <number>`                                 | Extracts a thumbnail from a single episode.             |
| `ffmpeg-subs <source_file> <number>`                                      | Extracts subtitles from a single episode.               |
| `ffmpeg-subs-clean <file>`                                                | Cleans subtitles with a simple regex.                   |
| `ffmpeg-subs-clean-ad <file>`                                             | Cleans subtitles with custom strategies.                |
| `ffmpeg-chapters <source_file> <number>`                                  | Extracts chapters from a single episode.                |
| `ffmpeg-stats <source_file> <number>`                                     | Extracts stats from a single episode.                   |
| `tags.py <tag> <tag> ...`                                                 | Returns a bitflag for selected tags.                    |

## Contributing
If you want a feature added or you found a bug, make a new <a href="https://github.com/nyananime-devs/nyananime-toolkit/issues">Issue</a>.  
If you want to contribute, make a new <a href="https://github.com/nyananime-devs/nyananime-toolkit/pulls">Pull Request</a>.  
There are no guidelines or any of the sort and contributing is highly encougaraged!

## License
Nyan Anime (Toolkit) is licensed under the [GNU General Public License v3.0](https://github.com/nyananime-devs/nyananime-toolkit/blob/master/LICENSE).
