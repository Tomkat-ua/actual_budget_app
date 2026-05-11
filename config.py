import secret as s
secret_env = "dev"

db_host = s.get_secret_value("DB_HOST", secret_env)
db_port = int(s.get_secret_value("DB_PORT", secret_env))
db_user = s.get_secret_value("DB_USER", secret_env)
db_password = s.get_secret_value("DB_PASSWORD", secret_env)
db_name = s.get_secret_value("DB_NAME", secret_env)
bank_api_url = s.get_secret_value("BANK_API_URL",secret_env)
actual_api_url = s.get_secret_value("ACTUAL_API_SERVER_URL",secret_env)
actual_sync_id = s.get_secret_value("ACTUAL_SYNC_ID",secret_env)
actual_api_key = s.get_secret_value('ACTUAL_API_KEY',secret_env)