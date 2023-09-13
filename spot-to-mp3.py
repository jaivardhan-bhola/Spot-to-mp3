import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import re
import inquirer
from pytube import YouTube
import urllib.request
import eyed3
load_dotenv()
tracks = [] 

def auth():
    global session 
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    session = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_id(url):
    id = re.search('(?<=playlist\/)(.*)(?=\?)', url).group(0)
    tracks_raw = session.playlist_tracks(id)["items"]
    for track in tracks_raw:
        tracks.append(track["track"]["name"]+ " by " + track["track"]["artists"][0]["name"])
    download_path = os.getcwd()+"/"+session.playlist(id)["name"]
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    return download_path
def get_album_id(url):
    id = re.search('(?<=album\/)(.*)(?=\?)', url).group(0)
    tracks_raw = session.album_tracks(id)["items"]
    for track in tracks_raw:
        tracks.append(track["name"]+ " by " + track["artists"][0]["name"])
    download_path = os.getcwd()+"/"+session.album(id)["name"]
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    return download_path
def get_song_id(url):
    id = re.search('(?<=track\/)(.*)(?=\?)', url).group(0)
    track = session.track(id)
    tracks.append(track["name"]+ " by " + track["artists"][0]["name"])
def download(download_path):
    video_links = {}
    for track in tracks:
        print("Searching for " + track + "...")
        link = "https://www.youtube.com/results?search_query=" + track.replace(" ", "+") + "+lyrics"
        try:
            html = urllib.request.urlopen(link)
        except UnicodeEncodeError:
            regex = r'(\w|\s)*'
            matches = re.finditer(regex, track, re.DOTALL)
            new_track = ""
            for matchNum, match in enumerate(matches):
                matchNum = matchNum + 1
                new_track += match.group()
            link = "https://www.youtube.com/results?search_query=" + new_track.replace(" ", "+") + "+lyrics"
            html = urllib.request.urlopen(link)  
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        if "/" in track:
            track = track.replace("/", "-")
        video_links[track] = "https://www.youtube.com/watch?v=" + video_ids[0]
    for track in video_links:
        print("Downloading " + track + "...")
        YouTube(video_links[track]).streams.filter(only_audio=True).first().download(filename=f"{track.split(' by')[0]}.mp3", output_path=download_path)

def main():

    auth()
    print("Welcome to Spot-to-MP3!")
    questions = [
        inquirer.List('option', message="What would you like to do?", choices=['Download a playlist', 'Download an album', 'Download a song', 'Exit'])
    ]
    answers = inquirer.prompt(questions)
    download_path = os.getcwd()
    if answers["option"] == "Download a playlist":
        url = input("Enter the playlist URL: ")
        download_path = get_playlist_id(url)
    elif answers["option"] == "Download an album":
        url = input("Enter the album URL: ")
        download_path = get_album_id(url)
    elif answers["option"] == "Download a song":
        url = input("Enter the song URL: ")
        get_song_id(url)
    elif answers["option"] == "Exit":
        exit()
    download(download_path)
main()