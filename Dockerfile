FROM python:3.8-alpine3.10
ENV URL="https://www.apkmirror.com/apk/supercell/brawl-stars/"
ENV INTERVAL=7200
ENV NOTIFICATION="test@test.com"

COPY files/requirements.txt /
RUN pip install -r requirements.txt
COPY files/appkChecker.py /app/
WORKDIR /app
CMD [ "mkdir", "log" ]
VOLUME ["/app/log"]
CMD [ "python", "./appkChecker.py"]