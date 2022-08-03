import json
import requests
import pandas as pd
import config as conf
from sqlalchemy import create_engine


engine = create_engine(f"mysql://{conf.db_username}:{conf.db_pwd}@{conf.db_host}:{conf.db_port}/{conf.db_name}")
con = engine.connect()

headers = {
	"X-RapidAPI-Key": conf.api_key,
	"X-RapidAPI-Host": conf.api_host
}
querystring = {"page": "0", "per_page": "100"}

# Get teams
url_teams = f"{conf.api_base_url}/teams"
teams = requests.request("GET", url_teams, headers=headers)
teams_json = json.loads(teams.text)
df_teams = pd.DataFrame(teams_json["data"])
print(df_teams)
df_teams.to_sql(con=con, name='teams', index=False, if_exists="append")