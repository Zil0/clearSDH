import os
import re
import subprocess


class ClearSDH:

    get_sub_command = "ffmpeg -i '{infile}' -y -map 0:s:0 '{outfile}'"
    replace_sub_command = "ffmpeg -i '{videofilename}' -i '{subfilename}' -y \
        -map 0:v -map 0:a -map 1:0 -c copy -c:s srt '{outfile}'"

    # Remove any match in the following regexes
    # Order is important, as matches are removed as we cycle through them
    regexes = [
        "(\[[^\]\n]*|[^\[\n]*\]) ?",  # indication between square brackets
        "^\W+$",                      # any line with no words
    ]
    regexes = [re.compile(r) for r in regexes]

    supported_subs = [".srt"]
    supported_vids = [".mkv"]

    def __init__(self, filenames, debug=False):
        if len(filenames) < 1:
            raise ValueError()
        self.video_in = filenames.get("video_in")
        self.video_out = filenames.get("video_out", self.video_in)
        if filenames.get("subtitles_in"):
            self.subtitles_in = filenames["subtitles_in"]
        else:
            self.subtitles_in = os.path.splitext(self.video_in)[0] + ".srt"
        self.subtitles_out = filenames.get("subtitles_out", self.subtitles_in)

        self.debug = debug

    def get_sub_file(self):
        if not os.path.exists(self.video_in):
            raise FileNotFoundError()
        err = self.run_and_wait(self.get_sub_command.format(
            infile=self.video_in, outfile=self.subtitles_in))
        if err or not os.path.exists(self.subtitles_in):
            raise IOError()

    def remove_SDH(self, nowrite=False):
        with open(self.subtitles_in, 'r') as f:
            subs = f.read().splitlines()
        stripped_subs = []
        SDH_lines = []
        i = 1
        j = 0
        for line in subs:
            if not line:
                pass
            elif line.isdigit() and int(line) == i:
                i += 1
                j = 0
                if stripped_subs and len(stripped_subs[-1]) == 1:
                    stripped_subs.pop()
            else:
                if j == 0:
                    stripped_subs.append([line])
                    j += 1
                else:
                    new_line = line
                    for r in self.regexes:
                        new_line = re.sub(r, '', new_line)
                    if new_line:
                        if new_line != line:
                            SDH_lines.append(self.diffstring(line, new_line))
                        stripped_subs[-1].append(new_line)
                    else:
                        SDH_lines.append(line)
        if nowrite:
            if self.video_in:
                # We created this file
                os.remove(self.subtitles_in)
            return SDH_lines
        with open(self.subtitles_out, 'w') as f:
            for i, line_block in enumerate(stripped_subs):
                f.write(str(i + 1) + '\n')
                f.write("\n".join(line_block) + '\n\n')

    def make_video_out(self):
        """Create a new video with stripped subtitles, or replace them"""
        if self.video_in != self.video_out:
            self.run_and_wait(
                self.replace_sub_command.format(
                    videofilename=self.video_in,
                    subfilename=self.subtitles_out,
                    outfile=self.video_out))
        else:
            name, ext = os.path.splitext(self.video_in)
            tempname = name + "_temp" + ext
            self.run_and_wait(
                self.replace_sub_command.format(
                    videofilename=self.video_in,
                    subfilename=self.subtitles_out,
                    outfile=tempname))
            os.rename(tempname, self.video_in)
        os.remove(self.subtitles_out)

    def run_and_wait(self, command_string):
        p = subprocess.Popen(command_string,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             shell=True)
        p.wait()
        if self.debug:
            print(p.stdout.read().decode())
        return p.returncode

    @staticmethod
    def diffstring(sfull, sstripped):
        result = ''
        i = 0
        for c in sfull:
            if i < len(sstripped) and c == sstripped[i]:
                result += c
                i += 1
            else:
                result += c + '\u0336'
        return result
