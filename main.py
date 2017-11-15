#!/usr/bin/env python3

import os
import sys
import argparse
from clearSDH import ClearSDH


def filetype(filename, video_text, sub_text):
    ext = os.path.splitext(filename)[1]
    if ext in ClearSDH.supported_vids:
        return video_text
    elif ext in ClearSDH.supported_subs:
        return sub_text
    else:
        raise ValueError()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove SDH information from \
                                     subtitle file")
    parser.add_argument(
        "source", help="video file to get subtitles from, or srt file")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("dest", nargs='?', default=None,
                       help="video file to be created with stripped subtitles")
    group.add_argument("--in-place", "-i", action="store_true",
                       help="directly modifiy source file")
    group.add_argument("--sub-file", "-s", action="store_true",
                       help="output a stripped srt file")
    group.add_argument("--dry-run", "-n", action="store_true", help="just print \
                        subtitles lines that would get removed")
    parser.add_argument("--debug", "-d", action="store_true", help="show \
                        ffmpeg output")
    args = parser.parse_args()

    filenames = {}
    try:
        filenames[filetype(args.source, "video_in",
                           "subtitles_in")] = args.source
        video = "video_in" in filenames
    except ValueError:
        sys.exit("Unknown input format : " + args.source)
    if args.dest:
        try:
            filenames[filetype(args.dest, "video_out",
                               "subtitles_out")] = args.dest
        except ValueError:
            sys.exit("Unknown output format : " + args.dest)

    if not video and args.sub_file:
        sys.exit("Invalid options combination.")

    cs = ClearSDH(filenames, args.debug)

    if video:
        try:
            cs.get_sub_file()
        except FileNotFoundError:
            print("Error : file not found.")
            sys.exit(1)
        except IOError:
            print("Error processing video. Try again with --debug to find out"
                  " why.")
            sys.exit(1)

    removed_SDH = cs.remove_SDH(nowrite=args.dry_run)

    if args.dry_run:
        print("Will strip :")
        print("\n".join(removed_SDH))
        sys.exit(0)

    if not video or args.sub_file:
        sys.exit(0)

    if video:
        cs.make_video_out()
