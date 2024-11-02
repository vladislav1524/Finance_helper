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
## How to launch a project 🛠️:
1. Add `localhost` or your Ngrok domain to the `ALLOWED_HOSTS` parameter in the file `settings.py `.
2. Create a `.env` file with your variables (add it to the directory, at the `manage.py `).

what does .env 📄 looks like (without spaces and buckets)::
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
3. Run in the main directory at the `manage.py `:
```bash
docker-compose up --build
```
Then run:
```bash
docker-compose exec web python manage.py migrate
```
To create a superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```
## If you want to test authentication via social networks 🌐:
1. Install Ngrok to use your computer as a server and publish the site with HTTPS. [Link to Ngrok](https://ngrok.com/)

2. In the Ngrok console, run:
```bash
ngrok http 8000
```
Or get a free domain in your personal account and do the following:
```bash
ngrok http --hostname=<your host> 8000  
```
3. Create and configure applications to log in via social networks, add data to .env:

Vk: https://dev.vk.com/ru

discord: https://discord.com/developers/applications

google: https://console.cloud.google.com/cloud-resource-manager

4. Add your Ngrok domain to CSRF_TRUSTED_ORIGINS and ALLOWED_HOSTS and run the container:
```bash
   docker-compose up --build
```
_______________________________________________________________________________________
