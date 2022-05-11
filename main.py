from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
ROOT_PATH = Path(os.environ['ROOT_PATH'])
CREDENTIAL_PATH = Path(os.environ['CREDENTIAL_PATH'])
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

import json
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen
import tempfile

from twitter import Twitter, OAuth, oauth_dance, read_token_file

if not CREDENTIAL_PATH.exists():
  oauth_dance('twifavoritedl', CONSUMER_KEY, CONSUMER_SECRET, CREDENTIAL_PATH)

oauth_token, oauth_secret = read_token_file(CREDENTIAL_PATH)

twitter = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))

for tweet in twitter.favorites.list(count=10, include_entities=True):
  tweet_id = str(tweet['id'])
  user_id = str(tweet['user']['id'])
  screen_name = tweet['user']['screen_name']

  tweet_url = f'https://twitter.com/{screen_name}/{tweet_id}'
  print(tweet_url)

  tweet_dir = Path(ROOT_PATH, user_id, tweet_id)
  tweet_dir.mkdir(parents=True, exist_ok=True)

  extended_entities = tweet.get('extended_entities', {})
  media = extended_entities.get('media', [])
  for medium in media:
    media_type = medium['type']
    if media_type == 'photo':
      params = {
        'name': '4096x4096',
      }
      image_raw_url = medium['media_url_https']
      image_url = f'{image_raw_url}?{urlencode(params)}'

      urlp = urlparse(image_url)
      image_url_path = urlp.path
      image_filename = os.path.basename(image_url_path)

      image_path = tweet_dir / image_filename
      if image_path.exists():
        continue

      print(image_url)
      image_data = urlopen(image_url).read()
      with open(image_path, 'wb') as fp:
        fp.write(image_data)

    elif media_type == 'video':
      variants = medium['video_info']['variants']

      best_video_url = None
      best_bitrate = None
      for variant in variants:
        content_type = variant['content_type']
        if not content_type.startswith('video/'):
          continue

        bitrate = variant.get('bitrate')
        if bitrate is None:
          continue

        if best_bitrate is None or best_bitrate < bitrate:
          best_bitrate = bitrate
          best_video_url = variant['url']

      assert best_video_url is not None

      urlp = urlparse(best_video_url)
      video_url_path = urlp.path
      video_filename = os.path.basename(video_url_path)

      video_path = tweet_dir / video_filename
      if video_path.exists():
        continue

      print(best_video_url)
      video_data = urlopen(best_video_url).read()
      with open(video_path, 'wb') as fp:
        fp.write(video_data)

  json_path = tweet_dir / 'tweet.json'
  with open(json_path, 'w', encoding='utf-8') as fp:
    json.dump(tweet, fp, ensure_ascii=False)
