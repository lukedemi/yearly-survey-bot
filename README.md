# yearly-survey-bot

docker build . -t yearly-survey-bot
docker run -d -p 9340:9340 --name yearly-survey-bot yearly-survey-bot
