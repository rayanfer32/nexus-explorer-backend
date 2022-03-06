### Nexus explorer backend

### Features

1. Proxifies all HTTP requests over HTTPS
2. Caches responses on the server, based on the Cache-control header (reduces direct API hits to the Nexus core)

### Installation: 
`pip3 install -r requirements.txt`

### Usage:

To run the production server
`waitress-serve --listen=*:8080 app:app`
