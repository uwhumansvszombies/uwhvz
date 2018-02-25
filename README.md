# University of Waterloo — Humans vs Zombies

## About

Humans vs zombies is a week long of fun.

## Contributing

few sentences on how to contribute maybe?

## Development Setup

To start a local server do the following:
```bash
git clone git@github.com:tiffanynwyeung/uwhvz.git
cd uwhvz
python3.6 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir tmp # sorry
python manage.py migrate
python manage.py runserver
```
