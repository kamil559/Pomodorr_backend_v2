# Pomodorr_backend_v2

[![Build Status](https://img.shields.io/travis/kamil559/pomodorr_v2/master.svg?label=TravisCI&style=flat&logo=travis)](https://travis-ci.org/github/kamil559/pomodorr_v2) 
[![Build Status](https://circleci.com/gh/kamil559/pomodorr_v2/tree/master.svg?style=svg)](https://app.circleci.com/pipelines/github/kamil559/pomodorr_v2) 
[![codecov](https://codecov.io/gh/kamil559/pomodorr_v2/branch/master/graph/badge.svg)](https://codecov.io/gh/kamil559/pomodorr_v2) 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 
[![License: MIT](https://img.shields.io/github/license/kamil559/pomodorr_v2.svg?color=blueviolet)](https://github.com/kamil559/pomodorr_v2/blob/master/LICENSE) 

Pomodorr is a Pomodoro timer and task management application that will help you stay
focused and motivated throughout your day-to-day work routine.


This project is a refactored version of [Pomodorr](https://github.com/kamil559/pomodorr) 
where some clean-architecture approach rules have been introduced as well as some changes of chosen libraries. 
This is only a demonstrative version prepared for local usage.


## Table of contents
* [General info](#Pomodorr_backend_v2)
* [Tech stack](#Tech-stack)
* [Project structure](#Project-structure)
* [Installation](#Installation)
* [Running tests](#Running-tests)
* [Local Flask server](#Local-Flask-server)
* [Flask commands](#Flask-commands)
* [Swagger UI](#Swagger-UI)

### Tech stack

* Base stack:
  * [Python (3.8)](https://www.python.org/)
  * [Flask (1.1.1)][Flask]
* Python packaging and dependency management:
  * [Poetry](https://github.com/python-poetry/poetry)
* Flask REST API-related libraries:
  * [Marshmallow](https://github.com/marshmallow-code/marshmallow)
  * [Flask-apispec](https://github.com/jmcarp/flask-apispec)
* Persistence layer:
  * [PostgreSQL](https://github.com/postgres/postgres)
  * [PonyORM](https://github.com/ponyorm/pony)
* Dependency injection:
  * [Injector](https://github.com/alecthomas/injector)
  * [Flask-Injector](https://github.com/alecthomas/flask_injector)
* Asynchronous tasks & monitoring:
  * [Celery](https://github.com/celery/celery)
  * [Redis](https://github.com/andymccurdy/redis-py)
  * [Flower](https://github.com/mher/flower)
* Containerization:
    * [Docker](https://github.com/docker)
    * [Docker Compose](https://github.com/docker/compose)
* Testing:
  * [pytest](https://github.com/pytest-dev/pytest)
  * [FactoryBoy](https://github.com/FactoryBoy/factory_boy)
* Linting:
  * [isort](https://github.com/PyCQA/isort)
  * [black](https://github.com/psf/black)
  * [flake8](https://github.com/PyCQA/flake8)
* Building:
  * [TravisCI](https://travis-ci.org/)
  * [CircleCi](https://circleci.com/)
    

### Project structure
The project consists of several packages that resemble the Onion architecture's layers:
* [pomodoros](https://github.com/kamil559/pomodorr_v2/tree/master/pomodoro_system/pomodoros) 
  package which is the innermost layer of the Onion architecture's diagram. 
  It contains the domain objects which are supposed to encapsulate the enterprise business rules.
  There is also an application part which contains the orchestration of business rules in the form of use cases.
  This is also a place for the interfaces the use cases rely on and which will be implemented and injected in the second package (infrastructure). 
* [pomodoros_infrastructure](https://github.com/kamil559/pomodorr_v2/tree/master/pomodoro_system/pomodoros_infrastructure)
  package is the one where the interfaces from the previous package have been implemented.
  For example these are concrete repositories, query objects (CQRS) that rely on a specific
  persistence strategy (in this case [SQLite3] for testing, [PostgreSQL] for usage and 
  [PonyORM] as a wrapper in order to make the communication with db engines easier and avoid writing bare SQL queries.)
* [web_app](https://github.com/kamil559/pomodorr_v2/tree/master/pomodoro_system/web_app)
  is the place where the input and output boundaries have been implemented, and a specific web framework has been chosen
  (in this case [Flask] is the weapon of choice). The package glues the use cases from the previous package and exposes 
  API endpoints which transform the incoming data into the DTOs used within the higher layers. This is also a place where
  all the web-specific stuff sits (e.g. authentication, authorization)
* [foundation](https://github.com/kamil559/pomodorr_v2/tree/master/pomodoro_system/foundation)
  is the place where all the most commonly used code among the whole project has been placed. 
  It contains the utils, value_objects, interfaces and exceptions used in the inner layer of the system
  and handled in the outermost web_app layer.
* [main](https://github.com/kamil559/pomodorr_v2/tree/master/pomodoro_system/main)
  is the package where the Inversion of Control Container is created and later used by Flask's integration 
  [Flask-Injector] which lets us avoid using the IoC Container explicitly.

### Installation

The easiest way of running Pomodorr_backend_v2 is building the [Docker] image and running the [Docker Compose] containers 
where all the external tools the project relies on are run separately.

The first thing in order to make the build successful is providing the environment variables. In order to recreate the structure
of directories of files containing environment variables, please create the following directory tree:  

```
<YOUR_REPOSITORY_ROOT>
│
└─── .envs
│    │   
│    └─── local
│    │    │   .application
│    │    │   .database
│    │    │   .mail
│    │    │   .security
│    │
│    │
│    └─── testing
│         │   .application
│         │   .database
│         │   .mail
│         │   .security
│
│
└─── pomodoro_system
│    │
│    └─── foundation
│    │
│    └─── main
│    │
│    └─── pomodoros
│    │
│    └─── pomodoros_infrastructure
│    │
│    └─── web_app
│    │
│    │ ...
│
│ ...
```


#### Example environment variables  
###### Local usage-specific variables:

```text
.envs/.local/.application

FLASK_APP=web_app/flask_app.py:create_app()  
FLASK_ENV=development  
SECRET_KEY=a5Uy2LuF4Q8zrnAxTecGq  
DEBUG=1  
TESTING=0
```
- - -

```text
.envs/.local/.database

DB_PROVIDER=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=xyz
POSTGRES_PASSWORD=xyz
POSTGRES_DB=pomodoro_db
```
- - -

```text
.envs/.local/.mail

MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_DEFAULT_SENDER="pomodoro_local@local.com"
```
- - -

```text
.envs/.local/.security

SECURITY_TOKEN_AUTHENTICATION_HEADER=Authorization
SECURITY_EMAIL_SUBJECT_REGISTER="Welcome to Pomodoro"
SECURITY_EMAIL_SENDER="pomodoro_local@local.com"
SECURITY_CONFIRM_EMAIL_WITHIN="1 days"
SECURITY_RESET_PASSWORD_WITHIN="1 days"
SECURITY_CONFIRM_SALT=_pomodoro_confirm_salt
SECURITY_RESET_SALT=_pomodoro_reset_salt
SECURITY_LOGIN_SALT=_pomodoro_login_salt
SECURITY_PASSWORD_SALT=_pomodoro_password_salt

```
- - -
 
###### Testing-specific variables:

```text
.envs/.testing/.application

FLASK_APP=web_app/flask_app.py:create_app()
FLASK_ENV=development
SECRET_KEY=xyz
DEBUG=1
TESTING=1
```
- - -

```text
.envs/.testing/.database
DB_PROVIDER=sqlite
DB_FILENAME=':memory:'
```
- - -

```text
.envs/.testing/.mail

MAIL_DEFAULT_SENDER="pomodoro_testing@test.com"
```
- - -

```text
.envs/.testing/.security

SECURITY_TOKEN_AUTHENTICATION_HEADER=Authorization
SECURITY_EMAIL_SENDER="pomodoro_testing@testing.com"
SECURITY_CONFIRM_SALT=_pomodoro_confirm_salt
SECURITY_RESET_SALT=_pomodoro_reset_salt
SECURITY_LOGIN_SALT=_pomodoro_login_salt
SECURITY_PASSWORD_SALT=_pomodoro_password_salt
```
- - -

Having recreated the .envs directory structure, the docker image is ready to be built.

```sh
$ docker-compose -f local.yml build
```

The last step is to run the docker-compose containers

```sh
$ docker-compose -f local up
```

### Running tests
For convenience purposes the project is by default built and tested outside the Docker Container.  
When it is done inside a CI tool, the tests are run through the make command, in local development [Poetry 'run' command][Poetry-run-command] 
is the most convenient approach, however it requires you to set up local [Poetry] environment and provide testing-specific environment variables manually.  

In order to set up the local environment with Poetry, first [install Poetry][Poetry-install].
Having done that, cd into the Project's root directory (the one pyproject.toml is placed) and execute the following commands

```shell
poetry install

export FLASK_APP="pomodoro_system/web_app/flask_app.py:create_app()"
export FLASK_ENV=testing
export APPLICATION_CONFIG=.envs/testing/.application
export DB_CONFIG=.envs/testing/.database
export SECURITY_CONFIG=.envs/testing/.security
export MAIL_CONFIG=.envs/testing/.mail
```
Now it is possible to run the tests with [Poetry 'run' command][Poetry-run-command] or straight with [pytest] command.

```shell
poetry run pytest
```
or
```shell
pytest .
```

You are also free to use the predefined make commands, e.g.

```shell
make run_pytest
make run_linters
make check_translations
```

### Local Flask server
Sometimes it is easier to debug an application when it is set up locally. In order to run the [Flask] server locally
it is necessary to provide the environment variables manually the same way as it was in the case of testing.

Execute the following commands:

```shell
export FLASK_APP="pomodoro_system/web_app/flask_app.py:create_app()"
export FLASK_ENV=development
export APPLICATION_CONFIG=.envs/local/.application
export DB_CONFIG=.envs/local/.database
export SECURITY_CONFIG=.envs/local/.security
export MAIL_CONFIG=.envs/local/.mail

source "${DB_CONFIG}"

export DB_HOST="localhost"
export DB_PORT="${POSTGRES_PORT}"
export DB_USER="${POSTGRES_USER}"
export DB_PASSWORD="${POSTGRES_PASSWORD}"
export DB_NAME="${POSTGRES_DB}"
```

Then run the server:

```shell
poetry run flask run --host=127.0.0.1 --port=8000
```

### Flask commands
In order to create a superuser, there is a [Flask command] available:
Note that this command also requires providing the environment variables 
(the same way as in case of [running Flask server locally](#Local-Flask-server))

```shell
poetry run flask users create_admin sample_admin@admin.com sample_password
```

### Swagger UI
Pomodorr_backend_v2 exposes a SwaggerUI endpoint which is accessible at:
```http request
http://127.0.0.1:8000/swagger-ui
```

![Swagger UI example image](https://github.com/kamil559/pomodorr_v2/blob/assets/swagger_ui.png?raw=True)


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
   [SQLite3]: <https://sqlite.org/whynotgit.html>
   [PostgreSQL]: https://www.postgresql.org/
   [PonyORM]: https://ponyorm.org/
   [Flask]: https://flask.palletsprojects.com/en/1.1.x/
   [Flask-Injector]: https://pypi.org/project/Flask-Injector/
   [Docker]: https://www.docker.com/
   [Docker Compose]: https://docs.docker.com/compose/
   [Poetry]: https://python-poetry.org/docs/
   [Poetry-run-command]: https://python-poetry.org/docs/cli/#run
   [Poetry-install]: https://python-poetry.org/docs/#installation
   [pytest]: https://docs.pytest.org/en/stable/
   [Flask command]: https://flask.palletsprojects.com/en/1.1.x/cli/
