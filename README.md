# University of Waterloo - Humans vs Zombies

## About
The latest UWaterloo HvZ website. Built on Django.

## Development Setup

To start a local server, do the following:
```bash
git clone git@github.com:uwhumansvszombies/uwhvz.git
pipenv install
pipenv shell
python manage.py migrate
python manage.py runserver
```

To make a migration after changing models, etc., use `python manage.py makemigrations app`.

## Production Setup

### General
The site is currently hosted on: Computer Science Club (CSC) servers.

We use a detached screen to run Gunicorn, which lets us run the site. Important commands include:
- `screen -ls`: should list exactly one detached screen where Gunicorn is running the site
- `screen -r`: resumes the Gunicorn screen

If no screen is found, do the following:
```bash
source venv/bin/activate
gunicorn --bind 0.0.0.0:53271 uwhvz.wsgi
```
Exit out of the screen session (but keep it running) with `Ctrl+A+D`, and then check if the website is running. If so, you're all set.

### Assets
If frontend-related changes are not refreshed on the site originally upon `pull`ing, use `python manage.py collectstatic`, and restart the server. If that doesn't work, do the following:
```bash
rm -rf /static/
python manage.py collectstatic
python manage.py compress --engine jinja2
``` 
The last line is for optimizing the size of our assets. **Failing to run the last line will cause a 500 error.**

## Useful things
- Generate a bunch of fake data for testing purposes: `python manage.py seed_data`

## Contributing
1. If anything is wrong, make an issue on the repo. 
2. If you are willing to take an issue/task on, do step 1, assign yourself, and make a PR!
3. Your PR needs to be approved by either [Tiffany Yeung][@tiffanynwyeung] or [Tristan Ohlson][@tso].
4. Once you're approved, you can merge and celebrate :tada:

[@tiffanynwyeung]: https://github.com/tiffanynwyeung
[@tso]: https://github.com/tso
