from infisical_sdk import InfisicalSDKClient

# 1. Ініціалізація клієнта
client = InfisicalSDKClient(host="https://vault.tomkat.in")

# 2. Авторизація через Machine Identity
client.auth.universal_auth.login(
    client_id="f069ef92-8c63-40fa-a04e-ce9e8b06cf00",
    client_secret="849c6eb6c62650b2b8af58b1ad486d6cc944987278c323d06870c261bf206a34"
)

# Отримання списку секретів
secrets = client.secrets.list_secrets(
    project_id="d6d3e764-7ce7-4a6a-b878-33c64433b9de",
    environment_slug="dev",
    secret_path="/"
)

# Вивід результатів
for s in secrets.secrets:
    print(f"Ключ: {s.secretKey} | Значення: {s.secretValue}")