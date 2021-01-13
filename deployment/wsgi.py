#!/srv/myapp/venv/python
# Change above line to point to Python in virtual environment
import os
os.environ['APP_CONFIG'] = 'PATH_TO_CONFIG'
os.environ['FLASK_ENV'] = 'production'

# Change 'myapp' to package name
from myapp import init_app

app = init_app()

if __name__ == '__main__':
	app.run()
