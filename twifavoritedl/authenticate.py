from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

from twitter import Twitter, OAuth, oauth_dance

oauth_token, oauth_secret = oauth_dance('twifavoritedl', CONSUMER_KEY, CONSUMER_SECRET)

print(f'OAUTH_TOKEN={oauth_token}')
print(f'OAUTH_SECRET={oauth_secret}')

