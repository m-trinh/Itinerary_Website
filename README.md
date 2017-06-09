# Itinerary_Website

## Setup
Use Python 3 and PostgreSQL 9.6
Make sure the right paths have been added to the Environment Variables

#### Clone repo:
```
> git clone https://github.com/m-trinh/Itinerary_Website.git
```

#### Create virtual environment:
```
> cd Itinerary_Website
> virtualenv venv
```

#### Start virtual environment:
```
> venv/Scripts/activate
```

#### Download modules:
```
> pip install -r requirements.txt
```

#### Create database:
In a separate terminal
```
> postgres -D "path/to/postgres/data"
```
In original terminal
```
> psql -U postgres
```
Enter password
```
postgres=# CREATE DATABASE itinerary_db;
postgres=# CREATE USER admin WITH PASSWORD 'admin';
postgres=# GRANT ALL PRIVILEGES ON itinerary_db TO admin;
```
Quit postgres with CTRL+C
```
> python manage.py makemigrations
> python manage.py migrate
```

## Starting App
#### Start the database:
```
> postgres -D "path/to/postgres/data"
```

#### Start app:
```
> cd Itinerary_Website
> venv/Scripts/activate
> python manage.py runserver
```
