# Mailing service

## Task description

- Implement methods for creating a new mailout, viewing the created ones, and getting statistics on completed mailouts.
- Implement the service itself for sending notifications to an external API. Design and develop a service that launches a mailout according to a mailing list of customers.

[Task in Russian](https://github.com/kooznitsa/test-projects/blob/main/mailing_service/task.md)

## Tech stack

<img src="https://img.shields.io/badge/FastAPI-fc884d?style=for-the-badge&logo=fastapi&logoColor=black"/> <img src="https://img.shields.io/badge/Redis-fc884d?style=for-the-badge&logo=Redis&logoColor=black"/> <img src="https://img.shields.io/badge/Celery-fc884d?style=for-the-badge"/> <img src="https://img.shields.io/badge/Pytest-fc884d?style=for-the-badge&logo=Pytest&logoColor=black"/> <img src="https://img.shields.io/badge/PostgreSQL-f5df66?style=for-the-badge&logo=PostgreSQL&logoColor=black"/> <img src="https://img.shields.io/badge/Docker-9a7b4d?style=for-the-badge&logo=Docker&logoColor=black"/>

## Tasks

- [x] API Dockerization.
- [x] Infrastructure with Docker Compose. Prepare docker-compose to start all project services with one command.
- [x] SQLModel for tables.
- [x] Connection with PostgreSQL.
- [x] Testing with Pytest. Write tests for the code.
- [x] Make it so that the page with Swagger UI opens at /docs/ and it displays a description of the developed API. Example: https://petstore.swagger.io.
- [x] Authentication using JWT.
- [x] Clear documentation on running the project with all its dependencies.
- [x] API documentation for integration with the developed service. Description of implemented methods in OpenAPI format.
- [x] Obtaining general statistics on the created mailouts and the number of sent messages on them, grouped by status.
- [x] Obtaining detailed statistics of sent messages for a specific mailout.
- [x] Processing active mailouts and sending messages to customers. Messages are sent to the remote service https://probe.fbrq.cloud/v1/send using the received token.
- [x] Automatic launch of mailouts according to the schedule (once per minute) with Celery.
- [x] Implement the return of metrics in the prometheus format and document the endpoints and exported metrics.
- [x] Provide detailed logging at all stages of request processing, so that during operation it is possible to find all information on:
  - mailout id: all logs for a specific mailout (both API requests and external requests to send specific messages);
  - message id: for a specific message (all requests and responses from an external service, all processing of a specific message);
  - customer id: any operations that are associated with a specific customer (adding, editing, sending a message, etc.).
- [x] Flower tracking web interface.
- [ ] Implement an additional service that sends statistics on processed mailouts to an email address once a day.
- [ ] Provide automated build/testing with GitLab CI.
- [ ] Write configuration files (deployment, ingress, etc.) to run the project in Kubernetes and describe how to apply them to a running cluster.
- [ ] Implement an administrator Web UI to manage mailouts and get statistics on sent messages.
- [ ] Provide integration with an external OAuth2 authorization service for the administrative interface. Example: https://auth0.com.

## Database structure

![Schema](https://github.com/kooznitsa/test-projects/blob/main/mailing_service/api/db/db_schema.png)

## Endpoints

| Method             | Endpoint                                  | Description               |
|--------------------|-------------------------------------------|---------------------------|
| **---GENERAL**     | /                                         |                           |
| GET                | /                                         | Root                      |
| GET                | /docs                                     | Documentation             |
| GET                | /metrics                                  | prometheus_client metrics |
| GET                | /api                                      | Home                      |
| POST               | /auth/token                               | Login                     |
| POST               | /api/search                               | Search customer           |
| **---CUSTOMERS**   | **/api/customers/**                       |                           |
| POST               | /                                         | Add customers             |
| GET                | /                                         | Get customers             |
| GET                | /{customer_id}                            | Get customer by ID        |
| PUT                | /{customer_id}                            | Change customer by ID     |
| DELETE             | /{customer_id}                            | Delete customer by ID     |
| POST               | /{customer_id}/tags                       | Create customer tag       |
| POST               | /{customer_id}/tags/{tag_id}              | Delete customer tag       |
| **---MAILOUTS**    | **/api/mailouts/**                        |                           |
| POST               | /                                         | Add mailouts              |
| GET                | /                                         | Get mailouts              |
| GET                | /{mailout_id}                             | Get mailout by ID         |
| PUT                | /{mailout_id}                             | Change mailout by ID      |
| DELETE             | /{mailout_id}                             | Delete mailout by ID      |
| POST               | /{mailout_id}/tags                        | Create mailout tag        |
| POST               | /{mailout_id}/tags/{tag_id}               | Delete mailout tag        |
| POST               | /{mailout_id}/phone_codes                 | Create mailout phone_code |
| POST               | /{mailout_id}/phone_codes/{phone_code_id} | Delete mailout phone_code |
| GET                | /{mailout_id}/start                       | Start mailout             |
| **---MESSAGES**    | **/api/messages/**                        |                           |
| POST               | /                                         | Add message               |
| GET                | /                                         | Get mailouts              |
| GET                | /{message_id}                             | Get mailout by ID         |
| PUT                | /{message_id}                             | Change mailout by ID      |
| DELETE             | /{message_id}                             | Delete mailout by ID      |
| GET                | /stats                                    | Get general statistics    |
| GET                | /stats/{mailout_id}                       | Get detailed statistics   |
| GET                | /{message_id}/start                       | Start mailout             |
| **---PHONE CODES** | **/api/phone_codes/**                     |                           |
| POST               | /                                         | Add phone code            |
| GET                | /                                         | Get phone codes           |
| GET                | /{phone_code_id}                          | Get phone code by ID      |
| PUT                | /{phone_code_id}                          | Change phone code by ID   |
| DELETE             | /{phone_code_id}                          | Delete phone code by ID   |
| **---TIMEZONES**   | **/api/timezones/**                       |                           |
| POST               | /                                         | Add timezone              |
| GET                | /                                         | Get timezones             |
| GET                | /{timezone_id}                            | Get timezone by ID        |
| PUT                | /{timezone_id}                            | Change timezone by ID     |
| DELETE             | /{timezone_id}                            | Delete timezone by ID     |
| **---TAGS**        | **/api/tags/**                            |                           |
| PUT                | /{tag_id}                                 | Change tag by ID          |
| DELETE             | /{tag_id}                                 | Delete tag by ID          |

## Prometheus metrics

- ```mailouts_total_created```: total number of mailouts created
- ```customers_total_created```: total number of customers created
- ```messages_total_sent```: total number of messages successfully sent per mailout id
- ```messages_total_failed```: total number of messages failed (after a number of retries) per mailout id

## Commands

### Project setup

- Create .env file in the root of the project:
```
TITLE=Mailing Service
DESCRIPTION=Mailing Service
OPENAPI_PREFIX=""
DEBUG=True

POSTGRES_SERVER=db_postgres
POSTGRES_USER=postgres
POSTGRES_PORT=5432
POSTGRES_PASSWORD=your_password              <- change this
POSTGRES_DB=mailing_db
POSTGRES_DB_TESTS=mailing_db_2

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
```
- Create network: ```docker network create my-net```
- Start the containers: ```docker-compose up -d --build```

After setting up the project, visit the mailing service at ```localhost:8000/docs```.
Visit the Flower web service at ```localhost:5555```. (Flower metrics: ```localhost:5555/metrics```.)

### Additional commands

- Run tests: ```docker exec -it fastapi_service poetry run pytest```
- Run tests and get a coverage report: ```docker exec -it fastapi_service poetry run pytest --cov```
- Remove the containers: ```docker-compose down```
- Start Celery workers from inside the container:
  - ```docker exec -it fastapi_service /bin/sh```
  - ```poetry run celery -A services.sender.celery_worker worker --loglevel=info```
- In new CMD tab, launch Flower monitoring web service from inside the container:
  - ```docker exec -it fastapi_service /bin/sh```
  - ```poetry run celery --broker=redis://redis:6379 --result-backend=redis://redis:6379 flower```
