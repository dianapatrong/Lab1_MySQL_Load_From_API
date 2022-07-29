import json
import requests
import pandas as pd
from sqlalchemy import create_engine
from config import *

engine = create_engine(f"mysql://{db_username}:{db_pwd}@{db_host}:{db_port}/{db_name}")
con = engine.connect()

headers = {
	"X-RapidAPI-Key": api_key,
	"X-RapidAPI-Host": api_host
}
querystring = {"page": "0", "per_page": "100"}

# Get teams
url_teams = f"{api_base_url}/teams"
teams = requests.request("GET", url_teams, headers=headers)
teams_json = json.loads(teams.text)
df_teams = pd.DataFrame(teams_json["data"])
print(df_teams)
df_teams.to_sql(con=con, name='teams', index=False, if_exists="append")