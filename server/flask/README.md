# Home-VOD Flask Backend

Learning Python Flask Project.

## Development

For Runtime Environment I have used a docker container. The `setup.sh` script should create it.

The source code is bound to the container so any changes are reflected inside the container as well.

## Tests

### Just run all tests

You can run all tests just from docker, using docker exec:

`docker exec home-vod-server python -m unittest discover -v -s .`

This should run all the tests.

> Ensure the testdb is deleted if you have stopped the execution of tests.

### Interactive mode

While developing you may want to run a single test multiple times. Suggestion is to connect interactively with the container:
`docker exec -it home-vod-server /bin/bash`

Then use the following command to run the specific test:
`python -m unittest ./test/test_logout.py`

You can also run all the tests with the following at this point.
`python -m unittest discover -v -s .`

> Ensure you are in the `/server` folder