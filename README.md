# Kronos Filler

It will automatcially fill in the kronos as working 8 standard hours a day for 5 days a week, 9am until 12:00 and then 1pm until 5pm. 
It will identify Holidays and PTO and will verify and the end of the program that it has been successfully completed.
It will then submit it for approval.

### Within a Mac or Linux terminal:

```bash
git clone https://github.com/callum-osborne/kronos-filler
```

```bash
cd kronos-filler
```

Install this package, it allows python to create its own browser. 

For Mac OS:
```bash
brew install geckodriver
```

For Linux systems:
```bash
sudo apt-get install firefox-geckodriverr
```

### Install library:

```bash
pip install selenium
```

Put your username and password into the login.txt file:
* Replace usernameHere with your username
* Replade passwordHere with your password

### Run the python script:
If you run into an error with an import run python3...

```bash
python run.py
```

or 

```bash
python3 run.py
```

### Virtual Code:

The first time you run the program you will have to enter the one time passcode sent to your email, it will then save the cookies so, it does not require the code again (if logged into every 30 days).