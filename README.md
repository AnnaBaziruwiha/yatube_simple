# Yatube
Yatube is a simple social network site, where users can get subscribed to each other, write and edit posts and comment each other's posts.

**NOTE**: This is a study project that was meant to be done in Russian only. Sorry for the inconvenience.

![Screenshot_2](https://user-images.githubusercontent.com/46953758/131117390-c43297f7-1b5d-4df4-aad6-33861d0de72e.jpg)

## Introduction

Yatube is a project made entirely on Django: authentication, automatic admin interface, Unittest were used. 

In Yatube, users can sign up, sign in and then post text and pictures. Users can edit their own posts. Every registered user gets a personal page, where all of the user's posts can be found, and where other users can subscribe. Each registered user can leave comments on posts. Users can also join groups.

## Technologies

- Python 3.9.0
- Django 2.2.6

## Launch in developer mode

- Clone the repository.
- Create a virtual environment in the project's root directory and activate it:
```sh
python3 -m venv venv # create virtual environment

source ./venv/bin/activate # for Unix or MacOS

source ./venv/scripts/activate # for Windows
```

- Install requirements:
```sh
pip install -r requirements.txt
```

- Apply existing migrations:
```sh
python manage.py migrate
```

- Collect static files in /static folder:
```sh
python manage.py collectstatic
```

- Create superuser:
```sh
python manage.py createsuperuser
```

- And finally, start Django server
```sh
python manage.py runserver
```

## Author

Anna-Maria Baziruwiha

You can contact me [here](abaziruwiha@gmail.com) for feedback and requests.

[This](https://www.linkedin.com/in/annabaziruwiha/) is my linkedin.

Check out my other projects here on github!

