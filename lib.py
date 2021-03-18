#!/usr/bin/env python

import os

target_path = "/home/quizznor/git-repositories/music"

with open(f"{target_path}/lib","w") as library:
    for artist in [dir for dir in os.listdir(f"{target_path}/artists") if dir not in ["all",".keep"]]:
        for track in os.listdir(f"{target_path}/artists/{artist}"):
            library.write(f"{artist}" + "\t" + f"{track.replace('.mp3','')}" + "\n")

print("\nSucessfully updated library\n")
