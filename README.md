## Create a virtual enviroment (Windows)

`py -m venv venv`

`.\venv\Scripts\activate`

`pip3 install flask`



## Run tests 

`python test_gra.py`



## Run server

`python gra.py`



## URLs


### Get shortest and longest winning intervals

http://127.0.0.1:5000/awards/min_max



### Get awards by producer

http://127.0.0.1:5000/awards/producer/(producer)

e.g. http://127.0.0.1:5000/awards/producer/adam%20sandler



### Get awards by year

http://127.0.0.1:5000/awards/year/(year)

e.g. http://127.0.0.1:5000/awards/year/1994


### Get all winners

http://127.0.0.1:5000/awards/winners


### Get winner by year

http://127.0.0.1:5000/awards/winner/(year)

e.g. http://127.0.0.1:5000/awards/winner/1996


### Get awards by studio

http://127.0.0.1:5000/awards/studio/(studio)

e.g. http://127.0.0.1:5000/awards/studio/Miramax%20Films
