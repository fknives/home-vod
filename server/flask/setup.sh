#!/bin/bash

if [ -f "certificate/cert.pem" ] && [ -f "certificate/key.pem" ]; then
    echo "Certificates found!"
else
    echo "Certificates not found! Make sure you have cert.pem and key.pem ready in folder $(pwd)/certificate/" >&2
    echo "To generate certificate use following command: \`openssl req -x509 -newkey rsa:4096 -keyout key.pem -nodes -out cert.pem -sha256 -days 365 -addext \"subjectAltName = IP:<ipaddress>\"\`" >&2
    echo "If -addext option doesn't work and you use libressl (to verify use openssl version) checkout https://github.com/libressl/portable/issues/544"
    exit 1
fi

while getopts ":u:p:m:" opt; do
  case $opt in
    u) admin_username="$OPTARG"
    ;;
    p) password="$OPTARG"
    ;;
    m) mount_folder="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    exit 1
    ;;
  esac
done

if [ -z "$admin_username" ]; then
  echo "-u Admin Username is required! ">&2
  exit 1
fi
if [ -z "$password" ]; then
  echo "-p Admin Password is required! ">&2
  exit 1
fi
if [ -z "$mount_folder" ]; then
  echo "-p Media Folder absolute path is required! ">&2
  exit 1
fi

echo "Admin username of backend: $admin_username"
echo "Admin password of backend: $password"
echo "Media folder mounted: $mount_folder"

IMG_NAME="home-vod-server:1.0"
CONTAINER_NAME="home-vod-server"

# build docker image if doesn't exists already
if [[ "$(docker images -q $IMG_NAME 2> /dev/null)" == "" ]]; then
  echo "Building Docker Image..."
  docker build -t $IMG_NAME .
else
  echo "Docker image $IMG_NAME already exists, skipping build."
fi

# delete container if it exists
echo "Deleting existing container($CONTAINER_NAME)..."
docker stop $CONTAINER_NAME 2> /dev/null
docker rm $CONTAINER_NAME 2> /dev/null

# start container binding the source and media files
echo "Creating container($CONTAINER_NAME)..."
docker run -d --name "$CONTAINER_NAME" -p443:443 --restart=always --mount type=bind,source="$(pwd)"/application,target=/server --mount type=bind,source="$mount_folder",target="/media-data/media",readonly $IMG_NAME

# initialize database with admin credentials
echo "Initializing database with adming user..."
docker exec $CONTAINER_NAME python backend/data/db.py -u "$admin_username" -p "$password"

echo "Docker container should be ready to use."
echo "To test server, you may use \`curl -k -d \"username=$admin_username&password=$password\" https://localhost:443/login\`"
echo "To tests use \`docker exec home-vod-server python -m unittest discover -v -s .\`."