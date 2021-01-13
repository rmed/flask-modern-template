#!/srv/myapp/venv/python
# Change above line to point to Python in virtual environment
import os
os.environ['APP_CONFIG']= 'PATH_TO_CONFIG'
os.environ['FLASK_ENV'] = 'production'

# Change 'myapp' to package name
from myapp import init_app, celery

app = init_app()

# Change 'myapp' to package name
from myapp.async_tasks import async_mail

app.app_context().push()
