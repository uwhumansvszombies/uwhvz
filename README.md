# University of Waterloo - Humans vs Zombies

## About

New UW HvZ website built on Django. Front-end uses a mix of Bootstrap 4 and Sass custom styling that lives in `static/stylesheets`.

## Development Setup

To start a local server do the following:
```bash
git clone git@github.com:uwhumansvszombies/uwhvz.git
pipenv install
pipenv shell
python manage.py migrate
python manage.py runserver
```

To make a migration after changing models, etc., use
`python manage.py makemigrations app`.

## Production Setup

We currently use CSC hosting, and use a detached screen to run Gunicorn, which lets us run the site. Important commands are `screen -ls`, which should list 1 detached screen where Gunicorn is running the site, and `screen -r`, for resuming the Gunicorn screen.

If no screen is found, do the following:
```bash
source venv/bin/activate
gunicorn --bind 0.0.0.0:53271 uwhvz.wsgi
```
Exit out of the screen session (but keep it running) with `Ctrl+A+D`, and then check if the website is running. If so, you're all set.

## Useful things

Generate a bunch of fake data for testing purposes: `python manage.py seed_data`

## Contributing

1. If anything is wrong, make an issue on the repo. 
2. If you are willing to take an issue/task on, do step 1, assign yourself, and
   make a PR!
3. Your PR needs to be approved by either [Tiffany Yeung][@tiffanynwyeung] if
   it's related to the styling/views/frontend, or
   [Tristan Ohlson][@tso] for anything re: backend.


[@tiffanynwyeung]: https://github.com/tiffanynwyeung
[@tso]: https://github.com/tso
