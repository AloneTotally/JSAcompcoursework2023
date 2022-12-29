# JSAcompcoursework2023

App/program that helps you decide what to eat judging by the locations near you and what you have eaten recently

## Tools

- KivyMD
- kv language
- firebase

## Backend firebase

- collections
  - Users
    - email
  - locations
    - long & latitude
  - ## history

## Planned updates

- Reviews to check if a restaurant is good
- A way to verify if a restaurant is real (by downvoting/reporting)
- A way to add a new location
  - Save as draft
- A way to recommend food places (1km radius?)
  - Maybe have presets to help? (In case food allergies, price range)

## How to set up project

### If the terminal is not already activated,

1. Open the project in whatever code editor you like, and open the terminal.
2. Now just type `virtualenv .env && source .env/bin/activate && pip install -r requirements.txt`. You should see a (.env) before your command prompt. This shows that the virtual environment has been installed.
3. To run the project, run `python3 main.py` and the app will start building
