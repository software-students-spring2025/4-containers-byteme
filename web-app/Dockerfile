FROM python:3.12

WORKDIR /web-app

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

ADD . .

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]