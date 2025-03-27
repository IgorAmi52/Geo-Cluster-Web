from app import create_app
from app.config import ENV_CONFIG
app = create_app()
if __name__ == '__main__':
    app.run(debug=ENV_CONFIG.DEBUG, port=ENV_CONFIG.PORT)
