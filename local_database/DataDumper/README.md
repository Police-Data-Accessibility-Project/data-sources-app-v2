The DataDumper directory contains scripts for backing up and restoring the Data Sources App Database.

## Files and Directories
- A `Dockerfile` which contains the instructions for building the docker image with Postgres functionality enabled
- A `dump.sh` script which handles the dump process
- A `restore.sh` script which handles the restore process
- A `docker-compose.yml` file which handles the setup of the docker container and can be modified to run either `dump.sh` or `restore.sh`
- A `.env` file which contains environment variables for the docker container
- A `dump` directory which stores the dump.

To connect to the database, your IP address will need to be added to the "allow" list in DigitalOcean database settings. Reach out to someone with admin access to get your IP address added.

## Environment Variables

See [ENV.md](ENV.md) in this directory