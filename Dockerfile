FROM python:3.9
WORKDIR /app

ENV DEBUG TRUE

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r ./requirements.txt

COPY . .

CMD ["python3", "./pigent.py"]
