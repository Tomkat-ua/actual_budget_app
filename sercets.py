from infisical_sdk import InfisicalSDKClient
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Ініціалізація клієнта
client = InfisicalSDKClient(host=os.getenv("INFISICAL_SITE_URL"))

# 2. Авторизація через Machine Identity
client.auth.universal_auth.login(
    client_id=os.getenv("INFISICAL_CLIENT_ID"),
    client_secret=os.getenv("INFISICAL_CLIENT_SECRET")
)

# # Отримання списку секретів
# secrets = client.secrets.list_secrets(
#     project_id=os.getenv("INFISICAL_PROJECT_ID"),
#     environment_slug="dev",
#     secret_path="/"
# )
#
# # Вивід результатів
# for s in secrets.secrets:
#     print(f"Ключ: {s.secretKey} | Значення: {s.secretValue}")

def get_secret_value(secret_name,env):
    secret = client.secrets.get_secret_by_name(
        secret_name=secret_name,
        project_id=os.getenv("INFISICAL_PROJECT_ID"),
        environment_slug=env,
        secret_path="/",
        expand_secret_references=True, # Optional
        view_secret_value=True, # Optional
        include_imports=True, # Optional
        version=None # Optional
    )
    return secret.secretValue
print (get_secret_value("budget_sync_id","prod"))