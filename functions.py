import torch
import numpy as np

genres = ['electronic', 'folk', 'hip_hop', 'jazz', 'rock']
min_tempo = 0
max_tempo = 222.605
min_loudness = -60.0
max_loudness = 2.383
def get_song_tensor(name, artist, sp):

  results = sp.search(q="track:" + name + " artist:" + artist, type="track")
  track_id = results['tracks']['items'][0]['id']
  artist = results['tracks']['items'][0]['artists'][0]['name']
  name = results['tracks']['items'][0]['name']
  img_link = results['tracks']['items'][0]['album']['images'][0]['url']

  f = sp.audio_features(track_id)[0]
  song = np.array([
    f['danceability'], 
    f['energy'], 
    (f['loudness'] - min_loudness) / (max_loudness - min_loudness), 
    f['speechiness'], 
    f['acousticness'], 
    f['instrumentalness'], 
    f['liveness'], 
    f['valence'], 
    (f['tempo'] - min_tempo) / (max_tempo - min_tempo),
    1
  ])
  song = torch.tensor(song).reshape(10).float()
  return song, img_link, artist, name

def get_genre(name, artist, model, sp):
  song, img_link, artist, name = get_song_tensor(name, artist, sp)  

  t = model(song)
  value = (t == max(t)).nonzero(as_tuple=True)[0].detach()

  to_return = (f'Primary genre: {genres[value]} ({round(int(10000*max(t)))/100}% confidence)\n')
  
  if max(t) < .6:
    t_list = list(t)
    t_list[t_list.index(max(t_list))] = torch.tensor(0)
    secondary_genre = genres[t_list.index(max(t_list))]
    sum = 0
    for val in t_list:
      sum += val.item()
    secondary_confidence = max(t_list) / sum
    if secondary_confidence > .6:
      to_return += f'Secondary genre: {secondary_genre} ({round(int(10000*secondary_confidence))/100}% confidence)\n'

  return to_return, artist, name, img_link
