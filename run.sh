# Build and start
sudo docker build -t apk-checker . && sudo docker run -d --name apk-checker -v `pwd`/log:/app/log -e apk-checker

# Build and start + params 
#sudo docker build -t apk-checker . && sudo docker run -d --name apk-checker -v `pwd`/log:/app/log -e INTERVAL=259200 apk-checker
#sudo docker build -t apk-checker . && sudo docker run -d --name apk-checker -v `pwd`/log:/app/log -e INTERVAL=259200 -e NOTIFICATION=test@test.org apk-checker
sudo docker build -t apk-checker . && sudo docker run -d --name apk-checker -v `pwd`/log:/app/log -e INTERVAL=259200 -e NOTIFICATION=test@test.org -e URL=https://www.apkmirror.com/apk/playrix/gardenscapes-2 apk-checker

sleep 10

# Check Logs
sudo docker logs apk-checker 

# Stop and Remove
sudo docker stop apk-checker && sudo docker rm apk-checker && sudo docker rmi apk-checker
