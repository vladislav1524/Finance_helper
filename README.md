# Finance_helper 💰

### Project description 📊:
This is a website for financial accounting assistance that will help you visualize your income and expenses, set a goal for accumulation that depends on your income and expenses.
Also on the site you can get advice from the neural network based on your expenses, income and goals.

### Technologies used in the project:
- *Redis*: Caching of page elements to reduce queries to the database and to the exchange rate API.
- *Celery, RabbitMQ*: asynchronous sending of emails to the mail for password recovery.
- *DRF*: API for getting information about site users from external applications.
- *PostgreSQL*: database.
- *Someone else's API*: getting exchange rates.
- *Django-allauth and social-django*: user authentication via a website or social networks.
- *Docker*: Containerization

_______________________________________________________________________________________
### To run the project, you need to:
1) Add 'localhost' or your domain of Ngrok (about this is written below) if you use that to the allowed_hosts parameter in `settings.py`. 🛠️
2) Add a `.env` file with your own variables (add to the directory at the level of `manage.py`) 📂
3) run in main directory at the level of `manage.py`:
```plaintext
docker-compose up --build -d
```
 and run 
```plaintext
docker-compose exec web python manage.py migrate
```
 to stop docker container run:
 ```plaintext
 docker-compose down
```
4) to create superuser run:
 ```plaintext
 docker-compose exec web python manage.py createsuperuser
```
### if you want to test authentication via social networks 🌐, then you need to perform the steps below :
1) you need to install Ngrok to use your computer as a server and distribute the site with https. [Link to Ngrok](https://ngrok.com/)
2) Then in console of Ngrok run
```plaintext
 ngrok http 8000
 ```
or
```plaintext
 ngrok config add-authtoken <your_authtoken>
 ```
 to use a single domain when each time you start listening to the port (authtoken can be obtained on the website in the profile)
 
3) add your domain of Ngrok to CSRF_TRUSTED_ORIGINS and ALLOWED_HOSTS and run docker container
_______________________________________________________________________________________
what does .env 📄 looks like 
(without spaces and buckets):
```plaintext
SECRET_KEY=...
DATABASE_NAME=...
DATABASE_USER=...
DATABASE_PASSWORD=...
DATABASE_HOST=...
DATABASE_PORT=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
SOCIAL_AUTH_VK_OAUTH2_KEY=...
SOCIAL_AUTH_VK_OAUTH2_SECRET=...
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=...
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=...
SOCIAL_AUTH_DISCORD_KEY=...
SOCIAL_AUTH_DISCORD_SECRET=...
CELERY_BROKER_URL=...
API_THEB_KEY=...
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost # and your Ngrok domain
CSRF_TRUSTED_ORIGINS=127.0.0.1,localhost # and your Ngrok domain
```
