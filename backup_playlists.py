import yaml
import spotipy
import spotipy.util as util
import datetime as dt

scope = 'user-library-read'

with open("C:/spotify_api/spotify.yaml", 'r') as stream:
    try:
        credentials = yaml.safe_load(stream)
        username = credentials['username']
        password = credentials['password']
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        redirect_uri = credentials['redirect_uri']
    except yaml.YAMLError as exc:
        print(exc)


token = util.prompt_for_user_token(username,scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)

# The above step will open a browser window.
# You need to copy and paste the url from the browser into the terminal.
# URL should be something like http://localhost/?code=


def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'],
            track['name']))

def print_tracks_to_file(tracks, file_name):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        file_name.write(("\n{0} - {1} - {2}".format(i, track['artists'][0]['name'], track['name'])))

if token:
    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(username)
    file_name = 'playlist_backups_{}.txt'.format(dt.datetime.now().strftime("%Y-%m-%d"))
    with open('C:/spotify_api/playlist_backups/{file_name}'.format(file_name = file_name), 'w', encoding="utf-8") as playlist_file:
        for playlist in playlists['items']:
            if playlist['owner']['id'] == username:
                # print()
                playlist_file.write("")
                # print(playlist['name'])
                print(playlist['name'])
                playlist_file.write("\nPlaylist Name: {}".format(playlist['name']))
                # print ('  total tracks', playlist['tracks']['total'])
                playlist_file.write('\nNumber of Tracks:{}'.format(playlist['tracks']['total']))
                playlist_file.write('\nTracklist:')
                results = sp.playlist(playlist['id'],
                    fields="tracks,next")
                tracks = results['tracks']
                # show_tracks(tracks)
                print_tracks_to_file(tracks, playlist_file)
                # for i, item in enumerate(tracks['items']):
                #     track = item['track']
                #     playlist_file.write(("{0} - {1} - {2}".format(i, track['artists'][0]['name'], track['name'])))
                while tracks['next']:
                    tracks = sp.next(tracks)
                    print_tracks_to_file(tracks, playlist_file)
                playlist_file.write("\n\n")
else:
    print("Can't get token for", username)
