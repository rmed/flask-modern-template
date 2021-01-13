# Deployment example

The following example assumes the following scenario:

- Application will be installed to `/srv/myapp` using a virtualenvironment (`/srv/myapp/venv`)
- Application will be executed with **uWSGI** and use **Nginx** as a reverse proxy
- A Celery broker has been installed and configured (e.g. Redis)
- Assuming a Debian system

## Preparation

First it is necessary to prepare the virtual environment:

```shell
$ cd /srv/myapp
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install <PATH_TO_PACKAGE>
```

Note that it will be necessary to also prepare the database and perform any pending migrations.

## Files

Below is an explanation for every file in this directory.

### `wsgi.py`

This file serves as the **launcher** for the application through uWSGI. It simply sets the `APP_CONFIG` environment variable to point to the **absolute path of the configuration file**. This must be done **before the application is initialized**.

### `celery_worker.py`

This file initializes a celery daemon to handle asynchronous tasks. It has almost the same structure as `wsgi.py`, but pushes the application context instead of running the application.

### `myapp.ini`

This is the uWSGI configuration file for the application. Note that the name of the file matters, as it will be used to refer to the application in Nginx.

The `touch-reload` parameter allows specifying a file which will be monitored by uWSGI for changes. If a change is detected (i.e. `touch restart`), the application will be restarted.

In addition, the `attach-daemon` parameter makes sure that the Celery daemon will be started and stopped with the application, preventing any dangling instance of the daemon being executed.

### `nginx-conf`

This Nginx configuration will redirect any HTTP request to HTTPS and pass the requests to the running uWSGI application.
