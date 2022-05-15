### Nexus explorer backend

### Features

1. Proxifies all HTTP requests over HTTPS
2. Caches responses on the server, based on the Cache-control header (reduces direct API hits to the Nexus core)

### Python3.10 fix 
`git checkout python310`

### Installation: 
`pip3 install -r requirements.txt`

### Usage:
#### Method 1 - Waiterss:
To run the production server
```sh
sudo apt install python3-waitress
SERVER_URL="http://api.nexus-interactions.io:8080" waitress-serve --listen=*:5001 app:app
```
#### or Method 2 - Gunicorn:
```sh
sudo apt install gunicorn3
SERVER_URL="http://api.nexus-interactions.io:8080" gunicorn3 -w 1 -b 0.0.0.0:5001 app:app
```
