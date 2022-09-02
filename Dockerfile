# pulls a lightweighted python image
FROM python:3.9.13-slim-buster

# folder for application
WORKDIR /app

# copy requirements file
COPY requirements.txt requirements.txt

# update pip3 version
RUN pip3 install --upgrade pip

# install all requirements according to file
RUN pip3 install -r requirements.txt

# copy all application files
COPY . .

# set environment variable for flask application
RUN export FLASK_APP=tima.py

# install mariadb-client to check connection to database
# this is only used in combination with the startup.sh script
RUN apt-get update
RUN apt-get install mariadb-client-10.3 -y

# start flask application
CMD [ "flask", "run", "-h", "0.0.0.0" ]
