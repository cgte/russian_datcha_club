# What is this for ?

This code automatically downloads podcasts from russianpodcast.eu to my computer, both mp3 and pdf (and print them)

This way i get podacasts quickly and since i added the destination folder
to my seafile (an opensource dropbox/google drive alternative)
i get them on my phone so as to listen to them wherever i want.

# Who is this for ?

For now: people with at least little python experience.
If you have experience on Windows and Python feel free to help.


# How to install ?

I assume you have python2 and virtualenv installed.

You need `firefox webdriver` installed, the sofitware will check it can use it.
the on shell:

```shell
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
    python get_podcasts.py
```

Once you checked it worked fine you can change the line (line 53 at time of writing) `quiet = False` to `quiet = True`



# Notes

- This was a quick and dirty script to `get the job done` i know the coding style is awful. Do not do this at work !

- Printing is disabled by default for public code and to facilitate use for potential python windows people (command is typically a linux one). Change the code according to.

- Some parameters are in the code instead of proper argparse, feel free to adapt.
    - `print` sends pdfs to printer
    - `quiet_mode` do not display firefox window
    - `target_subfolder` for episodes (mostly for setup)


