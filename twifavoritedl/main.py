from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
ROOT_PATH = Path(os.environ['ROOT_PATH'])
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
OAUTH_SECRET = os.environ['OAUTH_SECRET']
INPAGE_COUNT = int(os.environ['INPAGE_COUNT'])

import json
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen
import tempfile
import time
from datetime import datetime, timezone
from typing import Optional

from twitter import Twitter, OAuth, oauth_dance

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--max_id', type=int)
args = parser.parse_args()

param_max_id: Optional[int] = args.max_id

twitter = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

updated_at = datetime.now(timezone.utc)

tweets = []

# favorite tweets
tweets += twitter.favorites.list(count=INPAGE_COUNT, include_entities=True, tweet_mode='extended', max_id=param_max_id)

# self tweets
tweets += twitter.statuses.user_timeline(count=INPAGE_COUNT, include_entities=True, include_rts=True, tweet_mode='extended')

for tweet in tweets:
  tweet_id = str(tweet['id'])

  user_id = str(tweet['user']['id'])
  screen_name = tweet['user']['screen_name']

  tweet_url = f'https://twitter.com/{screen_name}/status/{tweet_id}'
  print(tweet_url)

  tweet_dir = Path(ROOT_PATH, user_id, tweet_id)
  tweet_dir.mkdir(parents=True, exist_ok=True)

  entities = tweet.get('entities', {})
  media = entities.get('media', [])

  extended_entities = tweet.get('extended_entities', {})
  media += extended_entities.get('media', [])

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
      time.sleep(1)

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
      time.sleep(1)

  json_path = tweet_dir / 'tweet.json'

  found_at = updated_at
  if json_path.exists():
    with open(json_path, 'r', encoding='utf-8') as fp:
      old_data = None
      try:
        old_data = json.load(fp)
      except ValueError:
        traceback.print_exc()

      if old_data is not None:
        found_at_str = old_data.get('found_at')
        if found_at_str is not None:
          found_at = datetime.fromisoformat(found_at_str)

  with open(json_path, 'w', encoding='utf-8') as fp:
    json.dump({
      'tweet': tweet,
      'found_at': found_at.isoformat(),
      'updated_at': updated_at.isoformat(),
    }, fp, ensure_ascii=False)
