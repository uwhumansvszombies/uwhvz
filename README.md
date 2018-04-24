# University of Waterloo - Humans vs Zombies

## About

New UW HvZ website, built on Django. Front-end uses custom styling via
Sass/SCSS in the `static/` folder.

## Development Setup

To start a local server do the following:
```bash
git clone git@github.com:tiffanynwyeung/uwhvz.git
pipenv install
pipenv shell
python manage.py migrate
python manage.py runserver
```

To make a migration after changing models, etc., use
`python manage.py makemigrations app`.

## Useful things

Generate a bunch of seed data: `python manage.py seed_data`

## Contributing

1. If anything is wrong, make an issue on the repo. 
2. If you are willing to take an issue/task on, do step 1, assign yourself, and
   make a PR!
3. Your PR needs to be approved by either [Tiffany Yeung][@tiffanynwyeung] if
   it is related to any front-end, styling, and views overall, OR
   [Tristan Ohlson][@tso] for anything regarding the backend.

## Notes

UW HVZ Website Requirements

## Dashboard

Certain UI aspects for Humans and Zombies must be distinct, but the core must
be the same for all players.

- All players must be able to:
  - see their player score/team score
  - See team-specific news
  - submit kill reports
  - see statistics of signups, tags/kills per day, etc

- Humans must be able to:
  - submit supply codes
  - be able to see how much of their score is supply codes

- Zombies must be able to:
  - Have their point value change per stun
  - NOT see supply code UI
  - reset their score upon original death/turning
  - be able to see zombie trees

- Spectators must be able to:
  - NOT use any humans/zombies UI
  - See analytics of both teams
  - See news from both teams


[@tiffanynwyeung]: https://github.com/tiffanynwyeung
[@tso]: https://github.com/tso
