# Vault Skill
HashiCorp Vault integration for enterprise secret management.
## Usage
```python
from skills.vault import VaultClient
vault = VaultClient()
secret = vault.get_secret("myapp/config", "db_password")
vault.set_secret("myapp/config", {"db_password": "s3cret"})
```
