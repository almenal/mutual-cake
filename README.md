<div align="center">
    <img  src="./assets/logo.png" width=20% height=100%>
</div>
<h1 align='center'> MutualCake </h1>
An app for employees to make cakes to each other.


## 💡 Features

- Easy **sign up** form: provide name, date of birth and allergies
- **Your cakes, at glance**: who you have been assigned and what cake you've 
chosen. You can change both partner and cake, and even submit your own!
- **Your data, under your control**: View and modify your profile details, or 
delete your profile to quit the app for good.


## 🛠 Tech Stack

- Client: [Flet](https://flet.dev/)
- Server:
  - REST API: [FASTAPI](https://fastapi.tiangolo.com/)
  - Database implementation: [SQLite](https://www.sqlite.org/index.html)
  - Database handling: [SQLAlchemy](https://docs.sqlalchemy.org/)

## 🚂 Usage

0. Requires **Python 3.9** or higher

1. Create a virtual environment

```shell
python -m virtualenv mutualcake
source mutualcake/bin/activate
```

2. Install dependencies

```shell
python -m pip install -r requirements.txt
```

3. Initialize app. The app consists on a server and a client, and you start them both. To do that, run from the terminal

```shell
bash deploy.sh
```