"""
This script backs up my Spotify playlists and liked songs to a csv file.
Only backs up playlists owned by my account.
Input:
    Spotify key, etc. stored at C:/spotify_api/spotify.yaml
Output:
    .csv file with fields playlist_name, artist/s, track_name, album_name,
    popularity, spotify_uri
"""

import yaml
import spotipy
import spotipy.util as util
import pandas as pd
from datetime import datetime as dt

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
def print_log(string_in):
    print(dt.now().strftime('%Y-%m-%d %H:%M:%S'), " -  {string_in}".format(string_in=string_in))

def playlist_to_dataframe(spotify_client, playlist_object, df_columns):
    """
    Given a playlist object this function returns a dataframe with that playlist's
    tracks.
    Input:
        Authenticated Spotify client.
        Playlist object
        Columns to be used in dataframe.
    Output:
        Dataframe containing all liked tracks with fields playlist_name ('Liked Tracks'),
        artist_name, track_name, album_name, popularity, spotify_uri.

    """
    sp = spotify_client
    temp_df = pd.DataFrame(columns=df_columns)
    playlist_name = playlist_object['name']
    results = sp.playlist(playlist_object['id'],
                    fields="tracks,next")
    tracks = results['tracks']
    total_tracks = tracks['total']
    track_items = tracks['items']
    while tracks['next']:
        tracks = sp.next(tracks)
        overflow_track_items = tracks['items']
        track_items.extend(overflow_track_items)
    tracks = track_items
    for i, item in enumerate(tracks):
        track = item['track']
        artist_name = [x['name'] for x in track['artists']]
        track_name = track['name']
        album_name = track['album']['name']
        popularity = track['popularity']
        spotify_uri = track['uri']
        temp_df.loc[len(temp_df)] = [playlist_name, artist_name, track_name, album_name, popularity, spotify_uri]
    return temp_df

def get_my_playlist_tracks(spotify_client, df_columns):
    """
    Gets a dataframe containing all the songs saved in all playlists I own.
    Input:
        Authenticated Spotify client.
        Columns to be used in dataframe.
    Output:
        Dataframe containing all playlist tracks with fields playlist_name,
        artist_name, track_name, album_name, popularity, spotify_uri.
    """
    print_log('Getting tracks in playlists.')
    sp = spotify_client
    playlists = sp.user_playlists(username)
    total_playlists = playlists['total']
    playlist_items = playlists['items']
    while len(playlist_items) < total_playlists:
        overflow_playlists = sp.user_playlists(username, offset=len(playlist_items))
        overflow_playlists_items = overflow_playlists['items']
        playlist_items.extend(overflow_playlists_items)

    all_playlists_df = pd.DataFrame(columns=df_columns)
    for playlist in playlist_items:
        if playlist['owner']['id'] == username:
            temp_playlist_df = playlist_to_dataframe(sp, playlist, df_columns)
            all_playlists_df = all_playlists_df.append(temp_playlist_df, ignore_index=True)
    return all_playlists_df

def get_current_user_liked_tracks(spotify_client, df_columns):
    """
    Gets currently logged in user's liked tracks and returns in dataframe.
    Input:
        Authenticated Spotify client.
        Columns to be used in dataframe.
    Output:
        Dataframe containing all liked tracks with fields playlist_name ('Liked Tracks'),
        artist_name, track_name, album_name, popularity, spotify_uri.
    """
    print_log('Getting liked tracks.')
    sp = spotify_client
    playlist_name = 'Liked Tracks'
    temp_df = pd.DataFrame(columns=df_columns)
    tracks = sp.current_user_saved_tracks(limit=50)
    track_items = tracks['items']
    while tracks['next']:
      tracks = sp.next(tracks)
      overflow_track_items = tracks['items']
      track_items.extend(overflow_track_items)
    for i, item in enumerate(track_items):
        track = item['track']
        artist_name = [x['name'] for x in track['artists']]
        track_name = track['name']
        album_name = track['album']['name']
        popularity = track['popularity']
        spotify_uri = track['uri']
        temp_df.loc[len(temp_df)] = [playlist_name, artist_name, track_name, album_name, popularity, spotify_uri]
    return temp_df

def main():
    print_log('Attempting to backup Spotify playlists and liked tracks.')
    start_time = dt.now()
    if token:
        sp = spotipy.Spotify(auth=token)
        playlist_df_columns = ['playlist_name','artist_name','track_name','album_name',
                                'popularity','spotify_uri']
        my_playlist_tracks = get_my_playlist_tracks(sp, playlist_df_columns)
        my_liked_tracks = get_current_user_liked_tracks(sp, playlist_df_columns)
        all_playlists_df = my_playlist_tracks.append(my_liked_tracks, ignore_index=True)
        print_log('Number of rows and columns: {}'.format(all_playlists_df.shape))
        print_log('Writing file.')
        file_name = 'playlist_backups_{}.csv'.format(dt.now().strftime("%Y-%m-%d"))
        file_path = 'C:/spotify_api/playlist_backups/{file_name}'.format(file_name = file_name)
        all_playlists_df.to_csv(file_path)
        end_time = dt.now()
        print_log('Backup completed in {0} seconds, file saved at {1}'.format((end_time-start_time).seconds, file_path))
    else:
        print_log("Can't get token for", username)

if __name__ == "__main__":
    main()
