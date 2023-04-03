# (A)ctually (S)aucy (V)ery (Z)esty Bot

## Installation
0. First make sure chrome browser is installed.

1. Install the repo:
```
git clone https://github.com/isaacjeffersonlee/Actually_Saucy_Very_Zesty
```
2. Enter the repo directory and install the required dependencies. (I would recommend doing
this in a separate python virtual environment).
```
cd Actually_Saucy_Very_Zesty/
pip install -r requirements.txt
```
Then everything should be installed.

## Config File
We specify our user id and password and what sports we would like to enroll for
in the config.yaml file.
This looks like:
```yaml
asvz_id: "changeme"
asvz_password: "changeme"
datetime_format: "%d.%m.%Y %H:%M"
urls: # Replace these with your own urls
  - "https://schalter.asvz.ch/tn/lessons/493925"
  - "https://schalter.asvz.ch/tn/lessons/440705"
  - "https://schalter.asvz.ch/tn/lessons/434726"

enrollment_times: # Replace these with the online enrollment times of the above urls.
  - "03.04.2023 11:05"
  - "03.04.2023 11:15"
  - "04.04.2023 07:45"
```
Firstly change the `asvz_id` and `asvz_password` fields to your corresponding
id and password. (id can be found in your settings/profile on the asvz website).

For each lesson we want to enroll for, go to https://asvz.ch/426-sportfahrplan
and find its corresponding url. E.g https://schalter.asvz.ch/tn/lessons/493925
(Note: in case you haven't used the ASVZ website before,
each lesson has its own unique webpage for each time.)

Then at the bottom of the page find the section that looks like:
```
Einschreibezeitraum
Mo, 03.04.2023 10:00 - Di, 04.04.2023 06:00
```
And copy the corresponding online enrollment start time to the list of enrollment_times.
So for this example, this would be: `"03.04.2023 10:00"`.
Make sure these are in the format specified by time_format.
Also make sure for every url above, there is a matching enrollment time below.
The bot will throw an error if the number of urls does not match the number
of enrollment times.

## Running the bot
Once everything has been installed correctly and the config has been set,
you should be able to run the bot with:
```shell
python bot.py
```
It will open a browser window and attempt to login and then wait to enroll.
Enrollments are sorted by their enrollment times, and we enroll in a loop
and then sleep when far away from the next enrollment. If the browser window is closed
but the loop is still running, the bot will attempt to open the window again when
it needs to enroll. So it *should be* safe to close the window and leave the script running
when enrollment times are far apart, although I would advise against it.

I would advice using this script close to the enrollment time, to avoid errors.

## Errors
If you encounter any errors, please contact me and I'll do my best to fix them ASAP,
or alternatively raise a GitHub issue in this repo.
