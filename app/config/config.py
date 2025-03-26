import os

# if different list of PMIDs is used, change the import statement below
from .data.PMIDs_config import PMIDsConfig as PMIDs_CONFIG
from .data.Eutils_API_config import EutilsApiConfig as API_CONFIG
# Check the environment and import the corresponding configuration
if os.getenv("FLASK_ENV") == "production":
    from app.config.env.prod_config import ProdConfig as ENV_CONFIG
elif os.getenv("FLASK_ENV") == "development":
    from app.config.env.dev_config import DevConfig as ENV_CONFIG
else:
    # Default to development
    from app.config.env.dev_config import DevConfig as ENV_CONFIG
