# University of Waterloo - Humans vs Zombies

## About
The latest UWaterloo HvZ website. Built on Django.

## Dev Setup

To create a local instance of the site for development:
```bash
git clone git@github.com:uwhvz/uwhvz.git
pipenv install
pipenv shell
python manage.py migrate
python manage.py runserver
```

## Useful things
- `python manage.py seed_data` generates a bunch of fake data for testing purposes.
- `python manage.py makemigrations app` to make a migration after changing models, etc.

## Production Setup

### General
The site is currently hosted on: Computer Science Club (CSC) servers.

We use a detached screen to run Gunicorn, which lets us run the site. Important commands include:
- `screen -S gunicorn`: create a new screen to be detachable named "gunicorn"
- `screen -ls`: should list exactly one detached screen where Gunicorn is running the site
- `screen -r`: resumes the Gunicorn screen

If no screen is found, do the following:
```bash
screen -S gunicorn
source venv/bin/activate
gunicorn --bind 0.0.0.0:53271 uwhvz.wsgi
```
Exit out of the screen session (but keep it running) with `Ctrl+A+D`. **Failure to do this will make restarting the server significantly harder.** Afterwards, check if the website is online.

### Assets
If frontend-related changes are not refreshed on the site originally upon `pull`ing, use `python manage.py collectstatic`, and restart the server. If that doesn't work, do the following:
```bash
rm -rf /static/
python manage.py collectstatic
python manage.py compress --engine jinja2
``` 
The last line is for optimizing the size of our assets. **Failure to run the last line will cause a 500 error.**

## Contributing
1. If anything is wrong, make an issue on the repo. 
2. If you are willing to take an issue/task on, do step 1 if it's not already logged, assign yourself, and make a PR!
3. Your PR needs to be approved by an admin.
4. Once you're approved, you can merge and celebrate :tada:
