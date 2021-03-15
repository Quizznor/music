#!/usr/bin/env python

import os, sys
sys.dont_write_bytecode = True

import youtube_dl
import gid
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC

# Download the mp3 file
ydl_arguments = {"--extract-audio",
                 "--add-metadata",
                 "--audio-format mp3",
                 "--output '/home/quizznor/music/%(id)s.%(ext)s'"}

print("\nDOWNLOADING " + sys.argv[1])
os.system(f"youtube-dl {' '.join(ydl_arguments)} {sys.argv[1]}")
audio_path = "/home/quizznor/music/" + str([file for file in os.listdir("/home/quizznor/music") if file.endswith(".mp3")][0])


# Fiddle with metadata
audio = ID3(audio_path)
NAMES = ["","",""]

print("\nADDING METADATA FOR " + sys.argv[1])
for i,tag in enumerate(["TP1","TIT2","TALB"]):
    try:
        NAME = input(f"{tag} ({audio[tag]}): ")
    except KeyError:
        NAME = input(f"{tag}: ")

    NAMES[i] = NAME if NAME else str(audio[tag])
    NAMES[i] = NAMES[i].replace("'","").replace('"','')

audio.add(TPE1(encoding=3, text=f"{NAMES[0]}"))
audio.add(TIT2(encoding=3, text=f"{NAMES[1]}"))
audio.add(TALB(encoding=3, text=f"{NAMES[2]}"))

for tag in ["TDRC","TXXX:description","TXXX:comment","TXXX:purl","TSSE"]:
    audio.delall(tag)


# Check if song already exists
all_songs = open("/home/quizznor/music/lib").readlines()
if "{} - {}\n".format(NAMES[0],NAMES[1]) in all_songs:
    prompt = input("\nSong already in your library, continue? ")
    if prompt != "y":
        os.system(f"rm -rf {audio_path}")
        sys.exit("Goodbye!\n")

# Add album cover art
img_path_should = f"/home/quizznor/music/coverart/{str(NAMES[0]).replace(' ','_').lower()}-{str(NAMES[2]).replace(' ','_').lower()}.png"
if not os.path.isfile(img_path_should):
    gid_arguments = {"keywords": f"{NAMES[0]} {NAMES[1]} album cover",
                 "format": "png",
                 "limit":1,
                 "no_directory":True,
                 "prefix":f"{NAMES[0]} {NAMES[1]}",
                 "output_directory":"/home/quizznor/music/coverart/",
                 "no_numbering":True,
                 "silent_mode":True,
                 "aspect_ratio":"wide"}

    response = gid.googleimagesdownload()
    absolute_image_paths = response.download(gid_arguments)
    img_path_is = [file for file in os.listdir("/home/quizznor/music/coverart") if file.startswith(f"{NAMES[0]} {NAMES[1]}")][0]
    os.system(f"mv '/home/quizznor/music/coverart/{img_path_is}' {img_path_should}")

audio.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(f"{img_path_should}",'rb').read()))
audio.save()


# Update library and move song
print("\nUPDATING LIBRARY AND MOVING SONG TO APPROPRIATE FOLDER")
with open("/home/quizznor/music/lib", "a") as library:
    library.write("{} - {}\n".format(NAMES[0],NAMES[1]))

if not os.path.isdir(f"/home/quizznor/music/artists/{str(NAMES[0]).replace(' ','_').lower()}"):
    os.system(f"mkdir /home/quizznor/music/artists/{str(NAMES[0]).replace(' ','_').lower()}")

os.system(f"mv {audio_path} /home/quizznor/music/artists/{str(NAMES[0]).replace(' ','_').lower()}/{str(NAMES[1]).replace(' ','_').lower()}.mp3")

print("Track sucessfully added to library!\n")