FROM python:3.9
WORKDIR /app

ENV DEBUG TRUE

COPY requirements.txt ./

# full install:
#RUN apt-get update -qq && \
#    apt-get install -y python-pexpect libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev libboost-python-dev libboost-thread-dev libbluetooth3-dev && \
#    apt-get clean

# Dropped Switchbot
#RUN apt-get update -qq && \
#    apt-get install -y libdbus-1-dev libglib2.0-dev libboost-python-dev libboost-thread-dev libbluetooth3-dev && \
#    apt-get clean


RUN pip3 install --no-cache-dir -r ./requirements.txt

COPY . .

CMD ["python3", "./pigent.py"]
