# Telegram birthday bot #

#### Bot sends reminders about registered users birthdays or other custom events and keeps records of gift fees ####

Start command to run app with docker:
```
$ docker-compose up --build -d
```

Enter in container and check db:
```
$ docker exec -it birthday_notification_postgresdb_1 psql -U admin hb_notification
```

Enter in container with bot:
```
$ docker exec -it birthday_notification_tgbot_1 bash
```




