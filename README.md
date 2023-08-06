# foodgram-project-react - Дипломный проект в Яндекс.Практикум

## Продуктовый помощник Foodgram

### Описание проекта:

«Продуктовый помощник»: это приложение, в котором зарегистрированные пользователи могут публиковать свои рецепты,
подписываться на публикации других авторов и добавлять понравившиеся рецепты в избранное, добавлять рецепты в корзину (список покупок). Во кладке «список покупок» пользователь может скачать список продуктов (.txt), которые необходимо купить для приготовления выбранных блюд.


###  Cсылк на развёрнутое приложение:

- #### http://84.252.139.221/recipes


###  Логин и пароль superuser (админки):

- #### login: TheXimik
- #### password: Microlab_09

### Подготовка и запуск проекта на сервере.
У вас должен быть установлен Docker и вы должны быть зарегистрированы на [DockerHub](https://hub.docker.com/)
- Клонировать проект с помощью `git clone git@github.com:TheXimik-DA/foodgram-project-react.git`
- Перейти в папку \foodgram-project-react\backend и выполнить команды:
```bash
sudo docker build -t <логин на DockerHub>/<название образа для бэкенда, какое хотите> .
sudo docker login
sudo docker push <логин на DockerHub>/<название образа для бэкенда, которое написали> 
```
- Перейти в папку \foodgram-project-react\frontend и выполнить команды:
```bash
sudo docker build -t <логин на DockerHub>/<название образа для фронтэнда, какое хотите> .
sudo docker login
sudo docker push <логин на DockerHub>/<название образа для фронтэнда, которое написали> 
```
- Изменить файл \foodgram-project-react\infra\deploy\docker-compose.yml:
```
backend:
  image: <логин на DockerHub>/<название образа для бэкенда, которое написали>
  
frontend:
  image: <логин на DockerHub>/<название образа для фронтэнда, которое написали>
```
- Изменить файл \foodgram-project-react\.github\workflows\foodgram_workflow.yml:
```
build_and_push_to_docker_hub:
.......
    tags: ${{ secrets.DOCKER_USERNAME }}/<название образа для бэкенда, которое написали>
    
deploy:
.......
    sudo docker pull ${{ secrets.DOCKER_USERNAME }}/<название образа для бэкенда, которое написали>
```
- Выполнить вход на удаленный сервер
- Установить docker на сервер:
```bash
sudo apt install docker.io 
```
- Установить docker-compose на сервер:
```bash
sudo apt-get update
sudo apt install docker-compose
```
- Скопировать файл docker-compose.yml и nginx.conf из директории infra на сервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
```
- Для работы с Workflow добавить в Secrets GitHub переменные окружения:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS= ваш ip или домен
DEBUG=False # значение True или False
SECRET_KEY=django-insecure--123 # ваш ключ джанго

DOCKER_PASSWORD=<пароль DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<ID своего телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего телеграм бота>
```
- После деплоя в git, дождитесь выполнения всех Actions.

- Проект стал доступен по вашему IP-адресу или домену.


### Технологии и необходимые ниструменты:

- Python 
- Django Rest Framework
- Docker
- PostgreSQL
- Djoser
- Nginx
- Gunicorn
- Django (backend)
- Reactjs (frontend)


### Автор

- Шахбанов Гаджи - [GitHub](https://github.com/TheXimik-DA)