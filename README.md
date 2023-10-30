### DataDev Day November 2023
# Tableau Webhooks + AWS Lambda
##### Kyle Massey | *Twitter/X*: @UpInYourVizness | *github*: @kjmassey
---

# Event Logger Backend
- Django + djangorestframework
- MySQL via AWS RDS
- tableauserverclient (TSC)

### Installation
##### NOTE: Exact cli/terminal syntax may vary by OS
1. Clone this repo
2. Create Python virtual environment:
   - *python -m venv name_of_env*
   - *name_of_env* = your virtual environment name
   - 'venv' is just fine :)
3. In a Terminal, run:
   - *pip install -r requirements.txt*
   - *django-admin --version*
   - If your terminal returns a version number, you're good to go!

### Database Configuration
##### NOTE: This can be done with any database that django/drf supports! AWS MySQL is used here.
1. Open **config > settings.py**
2. Starting on line 86:
   ```
   DATABASES = {
        "default": {
            ### CHANGE THIS BASED ON YOUR DB
            "ENGINE": "django.db.backends.mysql",
            "NAME": "{{ DATABASE/SCHEMA NAME }}",
            "USER": "{{ YOUR DB UID }}",
            "PASSWORD": "{{ YOUR DB PW }}",
            "HOST": "{{ YOUR DB HOST }}",
            "PORT": "3306",
        }
   }
    ```

### Starting the API
1. Run: *python manage.py runserver 0.0.0.0:8000*
2. Visit [http://localhost:8000](http://localhost:8000)
3. If you see the page below, everything went swimmingly!
   ![image](./assets/django_root.png)