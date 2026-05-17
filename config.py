import os
from dotenv import load_dotenv
from infisical_sdk import InfisicalSDKClient

load_dotenv()
secret_env = os.getenv("ENV")

# 1. Ініціалізація клієнта
client = InfisicalSDKClient(host = os.getenv("INFISICAL_SITE_URL"))

# 2. Авторизація через Machine Identity
client.auth.universal_auth.login(
    client_id=os.getenv("INFISICAL_CLIENT_ID"),
    client_secret=os.getenv("INFISICAL_CLIENT_SECRET")
)

def get_secret_value(secret_name,env,path):
    secret = client.secrets.get_secret_by_name(
        secret_name=secret_name,
        project_id=os.getenv("INFISICAL_PROJECT_ID"),
        environment_slug=env,
        secret_path=path,
        expand_secret_references=True, # Optional
        view_secret_value=True, # Optional
        include_imports=True, # Optional
        version=None # Optional
    )
    return secret.secretValue

db_host        = get_secret_value("DB_HOST", secret_env,"/database")
db_port        = int(get_secret_value("DB_PORT", secret_env,"/database"))
db_user        = get_secret_value("DB_USER", secret_env,"/database")
db_password    = get_secret_value("DB_PASSWORD", secret_env,"/database")
db_name        = get_secret_value("DB_NAME", secret_env,"/database")
bank_api_url   = get_secret_value("MONO_API_URL",secret_env,"/bank")
actual_api_url = get_secret_value("ACTUAL_API_SERVER_URL",secret_env,"/actual")
actual_sync_id = get_secret_value("ACTUAL_SYNC_ID",secret_env,"/actual")
actual_api_key = get_secret_value('ACTUAL_API_KEY',secret_env,"/actual")
cur_rate_url   = get_secret_value('CUR_RATE_URL',secret_env,"/bank")
###################################################################################################################


