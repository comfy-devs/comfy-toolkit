# Nyan Anime (Toolkit)

## Description
This is a toolkit with all kinds of scripts used for managing Nyan Anime.

## Stack
Other: <a href="https://www.docker.com/">Docker<a>  

## Docker Hint
Building is done with <code>docker-compose build</code>.  
Running is done with <code>docker-compose run nyananime-toolkit /bin/bash</code>.  
Shutting down is with <code>docker-compose down</code>.
For faster testing you can do <code>docker-compose build; docker-compose run nyananime-toolkit /bin/bash</code>.
> 1) Edit <code>.env-dummy</code> and save it as <code>.env</code>  
> 2) (Optional) Create an SSH key, ssh-copy-id to the host and save it as <code>ssh/id_rsa</code> to wherever you mounted the core folder  
> 3) (Optional) Edit feeds.conf and filters.conf and save it as <code>rss/feeds.conf</code> and <code>rss/filters.conf</code> under your core folder to use RSS

## Scripts included
| Script                        | Description                                               |
| ----------------------------- | --------------------------------------------------------- |
| `python dashboard.py`         | Used for processing anime series, in a GUI like form.     |
| `ffmpeg-x264-xx`              | Processes an episode with libx264.                        |
| `ffmpeg-x264-hls`             | Generates HLS streams from an episode.                    |
| `ffmpeg-vp9`                  | Processes an episode with libvpx-vp9.                     |
| `ffmpeg-thumbnail`            | Extracts a thumbnail from an episode.                     |
| `ffmpeg-subs`                 | Extracts subtitles from an episode.                       |
| `ffmpeg-chapters`             | Extracts chapters from an episode.                        |
| `ffmpeg-stats`                | Extracts stats from an episode.                           |
| `subs-clean`                  | Cleans subtitles with a simple regex.                     |
| `subs-clean-ad`               | Cleans subtitles with custom strategies.                  |
| `torrent-create`              | Creates a torrent for a series.                           |

## Contributing
If you want a feature added or you found a bug, make a new <a href="https://github.com/nyananime-devs/nyananime-toolkit/issues">Issue</a>.  
If you want to contribute, make a new <a href="https://github.com/nyananime-devs/nyananime-toolkit/pulls">Pull Request</a>.  
There are no guidelines or any of the sort and contributing is highly encougaraged!

## License
Nyan Anime (Toolkit) is licensed under the [GNU General Public License v3.0](https://github.com/nyananime-devs/nyananime-toolkit/blob/master/LICENSE).
