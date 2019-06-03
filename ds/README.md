
# Install makers in a docker container with docker-scripts

## Install

  - First install Docker:
    https://docs.docker.com/install/linux/docker-ce/debian/#install-using-the-repository

  - Then install `ds` and `wsproxy`:
     + https://gitlab.com/docker-scripts/ds#installation
     + https://gitlab.com/docker-scripts/wsproxy#installation

  - Get the code:
    ```
    git clone https://github.com/hillwithsmallfields/makers /opt/docker-scripts/makers
    ```

  - Create a directory for the container: `ds init makers/ds @makers.example.org`

  - Fix the settings:
    ```
    cd /var/ds/makers.example.org/
    vim settings.sh
    ```

  - Build image, create the container and configure it: `ds make`


## Access the website

  - When testing, open http://127.0.0.1:8000 in browser.

  - If the domain is not a real one, add to `/etc/hosts` the line
    `127.0.0.1 makers.example.org` and then try
    https://makers.example.org in browser.

  - Tell `wsproxy` to manage the domain of this container: `ds wsproxy add`

  - Tell `wsproxy` to get a free letsencrypt.org SSL certificate for this domain (if it is a real one):
    ```
    ds wsproxy ssl-cert --test
    ds wsproxy ssl-cert
    ```

## Other commands

    ds help

    ds shell
    ds stop
    ds start
