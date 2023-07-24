# JSAcompcoursework2023

App/program that helps you decide what to eat judging by the locations near you. This was developed as a group project with 3 members. Here is the link to the app demo: https://drive.google.com/file/d/1nYLLBabQlykz2ZQTm3M4rLVkXQ2YbaYz/view?usp=sharing



## Tools

- KivyMD
- kv language
- firebase

> Note: As ip address is used to find the user's location, it might not be as accurate as using the native features (Python has limitations)
## Planned updates

- A way to verify if a restaurant is real (by downvoting/reporting)
- A way to recommend food places (1km radius?)
  - Maybe have presets to help? (In case food allergies, price range)

## How to set up project

> f-strings are used, so python 3.6 minimum for this project to work

### If the terminal is not already activated,

1. Open the project in whatever code editor you like, and open the terminal. You should have python installed for this
2. If you type `pip` in the terminal and it does not return a long message, carry out the following steps:
   - `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
   - `python3 get-pip.py`
3. Run `pip install virtualenv`
4. Now just type `virtualenv .env && source .env/bin/activate && pip install -r requirements.txt`. You should see a (.env) before your command prompt. This shows that the virtual environment has been installed.

- If this command does not work and returns something like `virtualenv: command not found`, run `pip uninstall virtualenv` then `pip install virtualenv`

5. To run the project, run `python3 main.py` and the app will start building

> Note: There are some problems in the app which made need the app to rerun (I have no idea why, its just like that)

- One example is the add history item screen, where the green mapmarker would appear over the old mapmarker (After reloading the green mapmarker would replace the old mapmarker)
