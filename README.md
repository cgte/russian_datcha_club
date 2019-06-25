## Refactor in progress (this may no be accurate)


# What is this for ?

This code automatically downloads podcasts from russianpodcast.eu to my computer, both mp3 and pdf (and print them).

This way I could get podacasts quickly and since i added the destination folder
to my [Seafile](https://www.seafile.com) have them on my phone easily.

# Who is this for ?

For now: people with at least little python experience.
If you have experience on Windows and Python feel free to help.


# How to install ?

I assume you have python3 and virtualenv installed.

You need `firefox webdriver` installed, the sofitware will check it can use it.


```shell
    git clone https://github.com/cgte/russian_datcha_club
    cd russian_datcha_club
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    #An error with ipython does not prevents you from using the code
    cp credentials_template.py credentials.py

```

edit credentials file to set up login and password

# How to use


```shell
    source venv/bin/activate
    python get_episodes.py
```


# Notes

- Refacto in progress, this code used to be a simple script. Then i decided to shared i and afterwards to make mor like a 'real' python project.

- The content (podcasts) you will download is copyrighted, be careful not to add it in git and push it to any public location.
