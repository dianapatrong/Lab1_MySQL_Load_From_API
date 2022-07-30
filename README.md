# Lab 1 - Load data from an API into a dockerized MySQL

The objective of this lab is for you to be able to have a bit of hands-on with data extraction through Python. 
We are going to use the [NBA API](https://rapidapi.com/theapiguy/api/free-nba/) to collect data about NBA games, players
and teams. There are going to be multiple exercises that will help us achieve our goal of loading the data into a 
dockerized MySQL db. 

The following diagram can give you a visual overview of how are we going to connect our services together. 
![Lab1 Architecture Diagram](documentation_images/Lab1_ArchitectureDiagram.png)

**Pre-requisites:** 
* Python3
* Install Docker : 
    * Windows: https://docs.docker.com/desktop/install/windows-install/
    * Mac with intel chip: https://docs.docker.com/desktop/install/mac-install/
    * Mac with m1 chip: https://docs.docker.com/desktop/mac/apple-silicon/
* Install a db client or use the mysql cli
* Create an [NBA API](https://rapidapi.com/theapiguy/api/free-nba/) account
* Clone this repository


## 1. The API
The [NBA API](https://rapidapi.com/theapiguy/api/free-nba/) has historical NBA related data and has many endpoints. 
We are going to use three endpoints: 
* Get All Games
* Get All Players
* Get All Teams

### 1.1 Endpoints 
Let's review the schema of each of the endpoints. 

Games: 
```yaml
{
    "id": 47179
    "date": "2019-01-30T00:00:00.000Z"
    "home_team": {...}
    "home_team_score": 126
    "period": 4
    "postseason": false
    "season": 2018
    "status": "Final"
    "time": " "
    "visitor_team": {...}
    "visitor_team_score": 94
}
```

Teams: 
```yaml
{
    "id": 1
    "abbreviation": "ATL"
    "city": "Atlanta"
    "conference": "East"
    "division": "Southeast"
    "full_name": "Atlanta Hawks"
    "name": "Hawks"
}
```

Players: 
```yaml
{
    "id": 14
    "first_name": "Ike"
    "height_feet": NULL
    "height_inches": NULL
    "last_name": "Anigbogu"
    "position": "C"
    "team": {...}
    "weight_pounds": NULL
}
```


### ✏️ Exercise 1: 
Generate the DDL's for creating the tables for Players, Games and Teams and put them in a file called `create_nba_tables.sql`.

## 2. Data extraction through Python
Now that have taken a look at the API and at the schema of each endpoint, let's get started with 
our python script that will help us load the data from each endpoint into each of the tables in our db. 

### 2.1 The requirements.txt
We are going to use mainly 4 modules: 
* json - to transform text into json
* requests - to make the API call
* configparser - for configuration management
* pandas - to load our json into a DataFrame 
* sqlalchemy - to make the connection between Python and MySQL

Create a new virtual environment, activate it and install the requirements: 
```shell script
python3 -m venv /path/to/new/virtual/environment
source /newvirtualenvironment/bin/activate
pip install -r requirements.txt
```

### 2.2 The [ConfigParser](https://docs.python.org/3/library/configparser.html)
We are going to define all of our important variables inside a file called `config.ini`, this file
should never be committed since it holds important data such as passwords or secrets and is intended to live directly
on the server or in an external secrets manager service. 

### ✏️ Exercise 2: Create your own `config.ini` file following the below template
```
[api]
key = your_key
host = your_host
base_url = your_base_url

[db]
username = your_username
password = your_password
port = your_port
name = your_db_name
host = your_host
```

>NOTE: We are going to read from the `config.ini` file and reference such values in our python 
>code so nobody but us have access to it. 


### 2.4 Let's call the API 

Now that we have our connection setup we need let's start building our API call: 

#### API Headers
API headers are an extra source of information for each API call you make. They represent the meta-data associated 
with an API request and response. In this case, the documentation in the [NBA API](https://rapidapi.com/theapiguy/api/free-nba/)
tells us how to send them.  

```python 
headers = {
	"X-RapidAPI-Key": api_key,
	"X-RapidAPI-Host": api_host
}
```
#### Query parameters
You can use query parameters to control what data is returned in endpoint responses. 

In this API, there are two query parameters that we have to keep in mind: 
* page - The Page number, used for pagination
* per_page - The number of results returned per call, used for pagination

We now that we want to pull in batches of 100 players/games, and each batch
will come in a different page, starting with page 0. 
```python
querystring = {"page": "0", "per_page": "100"}
```
#### The endpoint 

If we take a look at the 3 endpoints that we are going to query, we can notice that all of them 
start with the same url, so that is our `api_base_url`, then we can start constructing
the url for each of the endpoints. 

Let's start with the teams endpoint, according to the documentation the endpoint will be: 
```python
url_teams = f"{api_base_url}/teams"
```

Then, we are going to use the `requests` library to get the data: 
```python
teams = requests.request("GET", url_teams, headers=headers, params=querystring)
```

>NOTE: Take into account that the previous line returns a response object and not plain text

#### The DataFrame
After converting our data into a json-like format, we can now load our data into a pandas DataFrame
```python
df_teams = pd.DataFrame(teams_json["data"])
```

Example of our loaded dataframe: 
```
    id abbreviation           city conference   division               full_name           name
0    1          ATL        Atlanta       East  Southeast           Atlanta Hawks          Hawks
1    2          BOS         Boston       East   Atlantic          Boston Celtics        Celtics
2    3          BKN       Brooklyn       East   Atlantic           Brooklyn Nets           Nets
3    4          CHA      Charlotte       East  Southeast       Charlotte Hornets        Hornets
4    5          CHI        Chicago       East    Central           Chicago Bulls          Bulls
5    6          CLE      Cleveland       East    Central     Cleveland Cavaliers      Cavaliers
```

#### ✏️ Exercise 3: 
Build each of the endpoints and create the logic to extract the requested data: 
* Get All Games: we are going to extract **700** games in batches of **100** games
* Get All Players: we are going to extract **500** players in batches of **100** players
* Get All Teams: we are going to extract **all** the teams  


## 3. MySQL container
For creating our database we are going to use docker-compose:
```dockerfile
version: "3"
services:
    db:
        container_name: container_name
        image: mysql:5.7
        ports:
            - "32001:3306"
        environment:
            MYSQL_ROOT_PASSWORD: yoursecretpassword
            MYSQL_DATABASE: db_name
```
* The first line is the version of docker compose 
* Then, the `services`, which in this case is only going to have a single database `db
* Next we have to define the name of our container
* The image tag will pull the version 5.7 of the mysql image from Docker Hub
* The `ports` tag is used to map the port in which the MySQL runs in the container to our localhost. MySQL by default runs on 3306, thus we map it to 32001 in our local machine.
* `MYSQL_ROOT_PASSWORD` under environment specifies the password that will be set for the MySQL **root** superuser account.
* `MYSQL_DATABASE`, this variable is optional and allows you to specify the name of a database to be created on image startup.

#### ✏️ Exercise 4:
Create your own docker-compose.yml file like the template above and run it


### 3.1 Building and running the image
Now that you have the docker-compose.yml file we are ready to build the MySQL image for our project. 
```shell script
$ docker-compose up -d
```
The **up** command runs the docker-compose.yml file and builds all the images declared. The **-d** flag is used 
to mention that we want it to done in detached mode, so that we can use our command line interface.

To make sure your container is up and running you can check it through: 
```shell script
$ docker ps
```
And you should see something similar to: 
````
CONTAINER ID   IMAGE       COMMAND                  CREATED             STATUS             PORTS                                NAMES
1bff2e2f5b3b   mysql:5.7   "docker-entrypoint.s…"   About an hour ago   Up About an hour   33060/tcp, 0.0.0.0:32001->3306/tcp   container_name
````

### 3.2 Connect to the MySQL db
You can either connect through a database client like Workbench
![Workbench connection](documentation_images/workbench_connection.png)

Or you can do it through the cli: 
```shell script
mysql --host=127.0.0.1 --port=32001 -u root -p
```
Make sure to change the port according to the one defined in your `docker-compose.yml` file and the password
will be the one defined in the `MYSQL_ROOT_PASSWORD` variable.

#### ✏️ Exercise 5: 
Now that you are connected to the database, create the tables using the DDL's that you generated in exercise 1

## 4 The [SQL connector](https://docs.sqlalchemy.org/en/14/core/engines.html)
Now we are going to leverage SQLAlchemy framework to connect our Python application with our MySQL database.

### 4.1 SQLAlchemy URIs
The connection string containing the information needed to connect to the database: 
```
dialect://username:password@host:port/database
```

### 4.2 SQLAlchemy Engine
The **engine** is an object that is used to connect to databases using the information of our URI.
```python
engine = create_engine(f"mysql://{db_username}:{db_pwd}@{db_host}:{db_port}/{db_name}")
con = engine.connect()
```

### 4.3 Pandas [to_sql()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html)
The `to_sql()` pandas method allows us to upload our DataFrame to a SQL database as a table. 
```python
df_teams.to_sql(con=con, name='teams', index=False, if_exists="append")
```
The parameters that we need: 
* `con`: The connection to mysql that we previously created
* `name` : Name of the SQL table
* `index` :  Writes the index as a column, we will set it to false.
* `if_exists`: Tells how to behave if the table already exists, we will set it to append mode


### ✏️ Final Exercise
Now that you are all set, execute your python script and load the data into each of their tables. 
Commit all your exercises and upload them to .... AWS CodeCommit? 

Don't forget to check the evaluation rubric to make sure you are not missing anything and to stop your container
when you are done with the lab.

```
docker-compose down 
```