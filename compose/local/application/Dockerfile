FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*


# Requirements are installed here to ensure they will be cached.
COPY ./pomodoro_system/requirements /requirements

RUN pip install -r /requirements/dev.txt

COPY ./compose/local/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/application/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

WORKDIR usr/src/app

COPY pomodoro_system/ ./

ENTRYPOINT ["/entrypoint"]
