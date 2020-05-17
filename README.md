

# apkMirrorChecker


**apkMirrorChecker** is a Python script to monitor a determined appkmirror url within specified intervals for changes. When it detects a change on a webpage a notification e-mail will be send if e-mail notification params is provided.

# **Dependencies**
All you need is **Docker**

# **Usage**

**Clone GIT Repo** 		 

    git clone https://github.com/gennadyd/apkMirrorChecker.git

**Build Docker Image** 		

    sudo docker build -t apk-checker apkMirrorChecker 

**Run Docker Container + PARAMS**

    sudo docker run -d --name apk-checker -v `pwd`/log:/app/log -e INTERVAL=259200 apk-checker
    sudo docker run -d --name apk-checker -v `pwd`/log:/app/log -e INTERVAL=259200 -e NOTIFICATION=test@test.org apk-checker
    sudo docker run -d --name apk-checker -v `pwd`/log:/app/log -e INTERVAL=259200 -e NOTIFICATION=test@test.org -e URL=https://www.apkmirror.com/apk/playrix/gardenscapes-2 apk-checker

**Show Docker Container Logs**

    sudo docker logs apk-checker`

**Stop & Remove Docker Container**

    sudo docker stop apk-checker && sudo docker rm apk-checker

**Remove Docker Image**
   
    sudo docker rmi apk-checker



