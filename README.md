# University of Waterloo - Humans vs Zombies

## About

New UW HvZ website, built on Django. Front-end uses custom styling via Sass/SCSS in the `static/` folder.

## Development Setup

To start a local server do the following:
```bash
git clone git@github.com:tiffanynwyeung/uwhvz.git
python3.6 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir tmp # sorry
python manage.py migrate
python manage.py runserver
```

To make a migration after changing models, etc., use `python manage.py makemigrations app`.

## Contributing

1. If anything is wrong, make an issue on the repo. 
2. If you are willing to take an issue/task on, do step 1, assign yourself, and make a PR!
3. Your PR needs to be approved by either Tiffany Yeung ([@tiffanynwyeung](https://github.com/tiffanynwyeung)) if it is related to any front-end, styling, and views overall, OR Tristan Ohlson ([@tso](https://github.com/tso)) for anything regarding the backend. 

## Notes

UW HVZ Website Requirements

Dashboard
Certain UI aspects for Humans and Zombies must be distinct, but the core must be the same for all players. 

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

## Technical Notes

### Models

A person has an account created for them in person by a mod. In this case, they
are AUTO ADDED to the current game (because there's no reason to create an 
account otherwise).

What does this really mean?? It means we're in a SIGNUP period. Games have
SIGNUP periods where:
- People who do not have an account already can signup in person
- People who DO have an account can simply go to the website and click "sign up"

Constraints:
1. Every user has at LEAST one player
2. Every player is mapped one to one to a game
3. From 1 and 2: every user has been in at least one game
4. Every player is owned by a user
5. At any given point at MOST a SINGLE game is visible to the user

Game states: SIGNUP -> RUNNING -> FINISHED
