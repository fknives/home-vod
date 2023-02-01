FROM python:3.9-bullseye

# ENV setup
RUN ["python","--version"]
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "nginx", "-y"]
RUN ["pip", "install", "uwsgi"]
RUN ["uwsgi", "--version"]
RUN ["pip", "install", "flask"]
RUN ["pip", "install", "passlib"]
RUN ["pip", "install", "pyotp"]

# NGINX configuration setup
COPY ./application/nginx-proxy-config /etc/nginx/sites-available/nginx-proxy-config
RUN ln -s /etc/nginx/sites-available/nginx-proxy-config /etc/nginx/sites-enabled

COPY ./certificate /certificate

WORKDIR $HOME/server

# load source files
COPY ./application $HOME/server

# run server commands
RUN nginx -t
RUN service nginx configtest

# create database - no longer needed, since binding volume
#RUN mkdir instance
#RUN python db.py

CMD service nginx restart & uwsgi --ini home-vod-server.ini