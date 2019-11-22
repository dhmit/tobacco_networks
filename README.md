# tobacco_networks

To get started, clone this repository and set it up in PyCharm
just like you did with the rereading project. See the tutorial here: https://urop.dhmit.xyz/rereading.html 

Finally, from the main directory, run `python setup.py develop`
to set up the name_disambiguation package

To create or update Django databases, run in terminal (in the backend folder):

1. python manage.py makemigrations
2. python manage.py migrate

Note: 
- the api does not work at (http://127.0.0.1:8000/api/) as it's not set up for this repo.  You can skip the step.
- there is no `frontend/src/App.js`. Use `frontend/src/main/main.js`
instead.
