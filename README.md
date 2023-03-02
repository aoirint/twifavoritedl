# twifavoritedl

- Python 3.10

## 1. Build docker image

```shell
docker build -t aoirint/twifavoritedl .
```

## 2. Create a Twiter App

- <https://developer.twitter.com/en/portal/projects-and-apps>

Enable OAuth 1.0a and copy `Consumer Key` and `Consumer Secret` to your .env.

```env
# .env

TWIFAVDL_CONSUMER_KEY=
TWIFAVDL_CONSUMER_SECRET=
```

## 3. Authenticate with your Twitter account

```shell
docker run --rm --env-file ./.env -it aoirint/twifavoritedl authenticate
```

Open the printed URL in your browser and authorize your app.

Paste `OAuth Token`, `OAuth Secret` to your .env.

```env
# .env

TWIFAVDL_CONSUMER_KEY=
TWIFAVDL_CONSUMER_SECRET=
TWIFAVDL_OAUTH_TOKEN=
TWIFAVDL_OAUTH_SECRET=
```


## 4. Prepare a download directory

```shell
mkdir ./data
chown -R 1000:1000 ./data
```

## 5. Configure .env

```env
# .env

TWIFAVDL_ROOT_PATH=/data
TWIFAVDL_INPAGE_COUNT=200

TWIFAVDL_CONSUMER_KEY=
TWIFAVDL_CONSUMER_SECRET=
TWIFAVDL_OAUTH_TOKEN=
TWIFAVDL_OAUTH_SECRET=
```

## 5. Execute download

```shell
docker run --rm --env-file ./.env -v "./data:/data" aoirint/twifavoritedl favorite

docker run --rm --env-file ./.env -v "./data:/data" aoirint/twifavoritedl search --keyword="#superbowl"

docker run --rm --env-file ./.env -v "./data:/data" aoirint/twifavoritedl lookup --id_list 1050118621198921728 20
docker run --rm --env-file ./.env -v "./data:/data" aoirint/twifavoritedl lookup --id_list_file /data/id_list.txt
```

## Update requirements

```shell
pip3 install pip-tools
pip-compile requirements.in
```
