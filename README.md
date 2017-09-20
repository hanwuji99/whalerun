# whale.run API

## Getting started

Download [Docker](https://www.docker.com/get-docker).
If you are on Mac or Windows, [Docker Compose](https://docs.docker.com/compose/overview/) will be automatically installed.
On Linux, make sure you have the latest version of [Compose](https://docs.docker.com/compose/install/).

Place an [environment file](https://docs.docker.com/compose/env-file/) in this directory with necessary environment variables defined.

Run in this directory:

    docker-compose up

The app will be running at [http://localhost:5000](http://localhost:5000).

For more details on deployment in a production environment,
please refer to [Docker Swarm](https://docs.docker.com/engine/swarm/).

## Architecture

* API Gateway: gateway

* Services: user, dataset, notebook, topic, comment, vote, message
