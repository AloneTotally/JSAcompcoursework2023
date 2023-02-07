# JSAcompcoursework2023

App/program that helps you decide what to eat judging by the locations near you and what you have eaten recently

## Tools

- KivyMD
- kv language
- firebase

Note: As ip address is used to find the user's location, it might not be as accurate as using the native features (Python has limitations)

## Planned updates

- Reviews to check if a restaurant is good
- A way to verify if a restaurant is real (by downvoting/reporting)
- A way to add a new location
  - Save as draft
- A way to recommend food places (1km radius?)
  - Maybe have presets to help? (In case food allergies, price range)

## How to set up project

### If the terminal is not already activated,

1. Open the project in whatever code editor you like, and open the terminal. You should have python installed for this
2. If you type `pip` in the terminal and it does not return a long message, carry out the following steps:
   - `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
   - `python3 get-pip.py`
3. Run `pip install virtualenv`
4. Now just type `virtualenv .env && source .env/bin/activate && pip install -r requirements.txt`. You should see a (.env) before your command prompt. This shows that the virtual environment has been installed.

- If this command does not work and returns something like `virtualenv: command not found`, run `pip uninstall virtualenv` then `pip install virtualenv`

5. To run the project, run `python3 main.py` and the app will start building
