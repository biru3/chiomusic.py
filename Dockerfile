FROM ubuntu:latest
LABEL authors="Piop2"

WORKDIR /usr/src

COPY ./requirements.txt .

RUN apt-get -y update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install ffmpeg

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

ENV DiscordApiToken ${DiscordApiToken}

#CMD ["main.py"]
#ENTRYPOINT ["python3"]
