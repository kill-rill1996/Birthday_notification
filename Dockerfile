FROM python:3.10

WORKDIR /usr/src/app

# buffer
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install cron

# Copy hello-cron file to the cron.d directory
COPY events-cron /etc/cron.d/events-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/events-cron

# Apply cron job
RUN crontab /etc/cron.d/events-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

RUN pip install --upgrade pip

COPY ./requirements.txt /usr/src/app

RUN pip install -r requirements.txt

COPY . /usr/src/app

# Run the command on container startup
# CMD cron && tail -f /var/log/cron.log