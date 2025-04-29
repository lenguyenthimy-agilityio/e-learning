from decouple import config
from split_settings.tools import include


available_environments = ("local", "test", "dev", "stag", "prod")

# Managing environment via DJANGO_ENV variable:
environment = config("DJANGO_ENV", default="local")
print(f"Using environment: {environment}")

include(
    "components/common.py",
    "components/database.py",
    *(f"environments/{environment}.py",) if environment in available_environments else (),
)
