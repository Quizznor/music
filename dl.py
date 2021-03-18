#!/usr/bin/env python

import os, sys
sys.dont_write_bytecode = True

import youtube_dl, gid
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC

target_path = "/home/quizznor/git-repositories/music"

ydl_arguments = {"--extract-audio", "--add-metadata", "--quiet",
                 "--audio-format mp3", f"--output '{target_path}/%(id)s.%(ext)s'"}


def download_song(link):

    print("\nDOWNLOADING " + link)
    os.system(f"youtube-dl {' '.join(ydl_arguments)} {link}")                   # Can we supress stdout for ydl?
    audio_path = f"{target_path}/" + str([file for file in os.listdir(f"{target_path}") if file.endswith(".mp3")][0])

    return audio_path

def add_metadata(song):

    audio, metadata = ID3(song), ["","",""]
    print("ADDING METADATA FOR " + song)

    for i,tag in enumerate(["TP1","TIT2","TALB"]):
        try:
            NAME = input(f"{tag} ({audio[tag]}): ")
        except KeyError:
            NAME = input(f"{tag}: ")

        metadata[i] = NAME if NAME else str(audio[tag])
        metadata[i] = metadata[i].replace("'","").replace('"','')

    for tag in ["TDRC","TXXX:description","TXXX:comment","TXXX:purl","TSSE"]:
        audio.delall(tag)

    audio.add(TPE1(encoding=3, text=f"{metadata[0]}"))
    audio.add(TIT2(encoding=3, text=f"{metadata[1]}"))
    audio.add(TALB(encoding=3, text=f"{metadata[2]}"))
    audio.save()

    return metadata

def add_picture(song):

    audio = ID3(song)
    img_path_should = f"{target_path}/coverart/{artist}-{album}.png"

    if not os.path.isfile(img_path_should):
        response = gid.googleimagesdownload()                                   # Can we supress stdout for gid?
        absolute_image_paths = response.download(gid_arguments)
        img_path_is = [file for file in os.listdir(f"{target_path}") if file.startswith(f"{metadata[0]} {metadata[1]}")][0]
        os.system(f"mv '{target_path}/{img_path_is}' {img_path_should}")

    audio.add(APIC(mime='image/jpeg',type=3, desc=u'Cover', data=open(f"{img_path_should}",'rb').read()))
    audio.save()

def handle_library(song):

    print("\nUPDATING LIBRARY AND MOVING SONG TO APPROPRIATE FOLDER")

    if not os.path.isdir(f"{target_path}/artists/{artist}"):
        os.system(f"mkdir {target_path}/artists/{artist}")

    os.system(f"mv {audio_path} {target_path}/artists/{artist}/{track}")
    os.system(f"ln -s {target_path}/artists/{artist}/{track} {target_path}/artists/all/{track}")

    print("TRACK ADDED TO LIBRARY SUCCESSFULLY!\n")


if __name__=="__main__":

    audio_path = download_song(sys.argv[1])                                     # Download the song from (e.g) YouTube
    metadata = add_metadata(audio_path)                                         # Add metadata for the song (Artist, Song, Album)

    artist = str(metadata[0]).replace(' ','_').lower()
    track = str(metadata[1]).replace(' ','_').lower() + ".mp3"
    album = str(metadata[2]).replace(' ','_').lower()

    gid_arguments = {"keywords": f"{metadata[0]} {metadata[2]} album cover", "limit":1,
                    "no_directory":True, "prefix":f"{metadata[0]} {metadata[1]}",
                    "output_directory":f"{target_path}", "no_numbering":True,
                    "silent_mode":True,}

    add_picture(audio_path)                                                     # Add album cover to the song (for display in a media player)

    if os.path.isfile(f"{target_path}/artists/{artist}/{track}"):
        prompt = input("\nSong already in your library! (y to continue) ")
        if prompt != "y":
            os.system(f"rm -rf {audio_path}") & sys.exit("Goodbye!\n")

    handle_library(audio_path)                                                  # Move song to appropriate folder and update playlists
