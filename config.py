import configparser

config = configparser.ConfigParser()
config.read("config.ini")
api_key = config['api']['key']
api_host = config['api']['host']
api_base_url = config['api']['base_url']
db_username = config['db']['username']
db_pwd = config['db']['password']
db_port = config['db']['port']
db_name = config['db']['name']
db_host = config['db']['host']
