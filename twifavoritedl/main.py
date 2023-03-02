
import os
from pathlib import Path

import json
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen
import traceback
import time
from datetime import datetime, timezone

from twitter import Twitter, OAuth, oauth_dance

from pydantic import BaseModel


class FavoriteConfig(BaseModel):
  root_path: Path
  consumer_key: str
  consumer_secret: str
  oauth_token: str
  oauth_secret: str
  inpage_count: int
  max_id: int | None
  full_save: bool


class AuthenticateConfig(BaseModel):
  consumer_key: str
  consumer_secret: str


def __run_favorite(config: FavoriteConfig):
  param_max_id = config.max_id

  twitter = Twitter(
    auth=OAuth(
      config.oauth_token,
      config.oauth_secret,
      config.consumer_key,
      config.consumer_secret,
    ),
  )

  updated_at = datetime.now(timezone.utc)

  tweets = []

  # favorite tweets
  if not config.full_save:
    kwargs = {}
    if param_max_id is not None: # optional kwarg
      kwargs['max_id'] = param_max_id

    new_tweets = twitter.favorites.list(count=config.inpage_count, include_entities=True, tweet_mode='extended', **kwargs)

    tweets += new_tweets
  else:
    saved_tweet_ids = []

    while True:
      kwargs = {}
      if param_max_id is not None: # optional kwarg
        kwargs['max_id'] = param_max_id

      new_tweets = twitter.favorites.list(count=config.inpage_count, include_entities=True, tweet_mode='extended', **kwargs)
      if len(new_tweets) == 0:
        print(f'No tweet found anymore (max id: {param_max_id})')
        break
      if len(new_tweets) == 1 and new_tweets[0]['id'] == param_max_id and param_max_id in saved_tweet_ids:
        print('Oldest tweet saved')
        break

      param_max_id = min(map(lambda tweet: int(tweet['id']), new_tweets))
      tweets += new_tweets
      saved_tweet_ids += list(map(lambda tweet: int(tweet['id']), new_tweets))
      print(f'Current tweets: {len(tweets)}, oldest ID: {param_max_id}')
      time.sleep(3)

  # self tweets
  tweets += twitter.statuses.user_timeline(count=config.inpage_count, include_entities=True, include_rts=True, tweet_mode='extended')

  for tweet in tweets:
    tweet_id = str(tweet['id'])

    user_id = str(tweet['user']['id'])
    screen_name = tweet['user']['screen_name']

    tweet_url = f'https://twitter.com/{screen_name}/status/{tweet_id}'
    print(tweet_url)

    tweet_dir = Path(config.root_path, user_id, tweet_id)
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


def run_favorite(args):
  __run_favorite(
    config=FavoriteConfig(
      root_path=args.root_path,
      oauth_token=args.oauth_token,
      oauth_secret=args.oauth_secret,
      consumer_key=args.consumer_key,
      consumer_secret=args.consumer_secret,
      inpage_count=args.inpage_count,
      max_id=args.max_id,
      full_save=args.full_save,
    )
  )


def __run_authenticate(config: AuthenticateConfig):
  oauth_token, oauth_secret = oauth_dance('twifavoritedl', config.consumer_key, config.consumer_secret)

  print(f'TWIFAVDL_OAUTH_TOKEN={oauth_token}')
  print(f'TWIFAVDL_OAUTH_SECRET={oauth_secret}')


def run_authenticate(args):
  __run_authenticate(
    config=AuthenticateConfig(
      oauth_token=args.oauth_token,
      oauth_secret=args.oauth_secret,
      consumer_key=args.consumer_key,
      consumer_secret=args.consumer_secret,
    )
  )


def main():
  import argparse
  parser = argparse.ArgumentParser()

  subparsers = parser.add_subparsers()
  subparser_favorite = subparsers.add_parser('favorite')
  subparser_favorite.add_argument('--root_path', type=Path, default=os.environ.get('TWIFAVDL_ROOT_PATH'))
  subparser_favorite.add_argument('--consumer_key', type=str, default=os.environ.get('TWIFAVDL_CONSUMER_KEY'))
  subparser_favorite.add_argument('--consumer_secret', type=str, default=os.environ.get('TWIFAVDL_CONSUMER_SECRET'))
  subparser_favorite.add_argument('--oauth_token', type=str, default=os.environ.get('TWIFAVDL_OAUTH_TOKEN'))
  subparser_favorite.add_argument('--oauth_secret', type=str, default=os.environ.get('TWIFAVDL_OAUTH_SECRET'))
  subparser_favorite.add_argument('--inpage_count', type=int, default=os.environ.get('TWIFAVDL_INPAGE_COUNT'))
  subparser_favorite.add_argument('--max_id', type=int)
  subparser_favorite.add_argument('--full_save', action='store_true')
  subparser_favorite.set_defaults(handler=run_favorite)

  subparser_authenticate = subparsers.add_parser('authenticate')
  subparser_authenticate.add_argument('--consumer_key', type=str, default=os.environ.get('TWIFAVDL_CONSUMER_KEY'))
  subparser_authenticate.add_argument('--consumer_secret', type=str, default=os.environ.get('TWIFAVDL_CONSUMER_SECRET'))
  subparser_authenticate.set_defaults(handler=run_authenticate)

  args = parser.parse_args()

  if hasattr(args, 'handler'):
    args.handler(args)
  else:
    parser.print_help()


if __name__ == '__main__':
  main()
