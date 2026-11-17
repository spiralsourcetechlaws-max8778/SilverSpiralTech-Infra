# SilverSpiralTech - Sliver C2 Deployment

## Render (Background Worker)
1. Create a new Background Worker in Render.
2. Point it to this directory.
3. Render will build the Dockerfile.
4. Once live, open the Render Shell for this worker and run:
   `sliver-server operator --name bridge_operator --lhost 0.0.0.0 --save /root/.sliver/operator.cfg`
5. Download `/root/.sliver/operator.cfg` to your local `/root/SilverSpiralTech/bridge/operator.cfg`.

## Koyeb (Docker)
1. Deploy this directory as a Docker service.
2. Ensure TCP ports 31337 and 8888 are exposed.

## GitHub Codespaces (Temporary)
1. Open this repo in Codespaces.
2. Run `docker build -t sliver .`
3. Run `docker run -d --name sliver -p 31337:31337 -p 8888:8888 sliver`
