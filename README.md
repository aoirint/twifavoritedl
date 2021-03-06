# twifavoritedl

- Python 3.8

## build docker image

```shell
make build
```

## create .env.myaccount

- Copy `template.env` to `.env.myaccount` and set values

## create twitter app

- <https://developer.twitter.com/en/portal/projects-and-apps>

Enable OAuth 1.0a and copy CONSUMER_KEY and CONSUMER_SECRET to your .env.

## run authenticate

```shell
make authenticate ARGS="--env-file=$(pwd)/.env.myaccount"
```

Open printed URL in your browser and authorize your app.

Paste outputs (OAUTH_TOKEN, OAUTH_SECRET) to your .env.

## create save directory

Save directory has to be owned by user=1000 and group=1000.

```shell
mkdir -p /path/to/twifavoritedl/tweets_myaccount
sudo chown -R 1000:1000 /path/to/twifavoritedl/tweets_myaccount
```

## run crawl

```shell
make run ARGS="--env-file=$(pwd)/.env.myaccount -v=/path/to/twifavoritedl/tweets_myaccount:/path/to/twifavoritedl/tweets_myaccount"
```

## Update requirements

```shell
pip3 install pip-tools
pip-compile requirements.in
```
