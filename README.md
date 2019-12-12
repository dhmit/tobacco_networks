# tobacco_networks

To get started, clone this repository and set it up in PyCharm
just like you did with the rereading project. See the tutorial here: https://urop.dhmit.xyz/rereading.html 

Finally, from the main directory, run `python setup.py develop`
to set up the name_disambiguation package

To create or update Django databases, run in terminal (in the backend folder):

1. python manage.py makemigrations
2. python manage.py migrate

Note: 
- there is no `frontend/src/App.js`. Use `frontend/src/main/main.js`
instead.

The api is functional: (http://127.0.0.1:8000/api/person_info/)

If you would like to find a person through the API,
paste the above url, followed by:

?full_name=Relevant Person Name

If the person is not in the database, 
the API will return an "empty" person whose full name will be
shown as: Relevant Person Name not found.
Otherwise, a dictionary with the information in the
database associated with that person will be returned.
