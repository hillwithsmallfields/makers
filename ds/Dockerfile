include(buster)

### install some other packages
RUN apt install --yes git wget sudo

### install dependencies
RUN echo 'deb http://deb.debian.org/debian/ sid main' > /etc/apt/sources.list.d/sid.list
RUN apt update && apt upgrade --yes
RUN apt install --yes \
    python3-pip python3-dev virtualenv \
    postgresql postgresql-contrib postgresql-server-dev-all libpq-dev \
    mongodb nginx
      
