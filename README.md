# yearly-survey-bot

```
docker build . -t yearly-survey-bot
docker run -d -p 9340:9340 -v ~/responses.log:/tmp/responses.log --env-file .env --name yearly-survey-bot yearly-survey-bot
```

```
docker build . -t yearly-survey-bot; docker kill yearly-survey-bot; docker rm yearly-survey-bot; docker run -d -p 9340:9340 -v ~/logs/:/app/logs/ --env-file .env --name yearly-survey-bot yearly-survey-bot; docker logs -f yearly-survey-bot
```