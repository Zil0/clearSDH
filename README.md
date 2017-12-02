# clearSDH

This script removes SDH elements from video files or subtitles.  
Now you can enjoy your legally acquired TV show episodes while noisily eating chips and not be informed of an [EXPLOSION] a split second seconds before Jesse gets killed, or the ♪ sad music ♪ playing when Walter has to dig him a grave.

## Installation

Just clone the repo, and make sure you have ffmpeg.

## Example usage

Process subtitles directly : `./main.py --in-place video.mkv`  
Output processeded subtitles : `./main.py subs.srt stripped_subs.srt`  
Output processed subtitles and don't touch the video : `./main.py --sub-file video.mp4` (will create video.srt)  
Note : other combinations that make sense should work.

## Troubleshooting

This has only been tested under ArchLinux, and only mkv, mp4 and srt formats are supported.  
Feel free to open an issue if faced with a bug.  
The regexes used to find SDH elements are added and modified following my own watch list, and probably leave out a lot. PR to improve them are welcomed.

## Limitations

- Only one subtitles track videos (TODO)
- Only one video at a time (TODO)
