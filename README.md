# Teamwork Analysis Dashboard

### Requirements:

The application is run using Python 3.7, but anything above 3.5 should be a safe bet.
> **Note:** You may need to use `python3` before your commands to ensure you use the correct Python path. e.g. `python3 --version`

```bash
python --version

-- or --

python3 --version
```

The web framework being used is Django (2.2.11), which is in the requirements file, and will be installed later.


### Installation:

It's recommended, although **not** required, to create a virtual environment before installation. [Here's][virtualenv-link] a guide on using virtualenv, if you do choose this route. Note, the git files are within this project folder itself, and the virtual environment is simply a wrapper - the files of the virtual environment are **not** to be included in this repo. In other words, everyone should be able to choose any IDE or workflow. 


First, clone this repo onto your system. Then, follow the steps below.

**Using PyPi (pip):**

On your terminal, navigate to the root directory (the directory which has the manage.py file in it). Then run the following:

```bash
$ pip3 install -r requirements.txt

-- or, if your pip defaults to python3 --

$ pip install -r requirements.txt
```

### Basic Usage

Run the following in the root directory:

If this is your first time setting up, you might need to migrate the database. Run the following:

```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

You can also create an admin (superuser) account for yourself to view database tables on the Django Admin UI Dashboard.
```bash
$ python3 manage.py createsuperuser
```

Then, run the following to run the server.

```bash
$ python3 manage.py runserver
```

Go to [localhost][localhost-link] on your browser (typically 127.0.0.1, port 8000) to view the application. Visit /admin to login as an administrator and view the database tables (although currently, we have no major tables).

<!-- Markdown links -->

[localhost-link]: http://localhost:8000/
[virtualenv-link]: https://virtualenv.pypa.io/en/latest/installation.html
