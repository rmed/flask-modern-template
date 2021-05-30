from setuptools import setup, find_packages

setup(
    name='myapp',
    version='1.0.0',

    description='A Flask template',
    long_description='',

    url='https://github.com/rmed/flask-modern-template',

    author='Rafael Medina García',
    author_email='',

    license='',

    classifiers=[],

    keywords='flask template',

    packages=find_packages(exclude=('tests',)),

    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'bcrypt>=3.2.0',
        'email-validator==1.1.2',
        'Flask==2.0.1',
        'Flask-Assets==2.0',
        'Flask-Babel==2.0.0',
        'Flask-Login==0.5.0',
        'Flask-Mail==0.9.1',
        'Flask-Misaka==1.0.0',
        'Flask-Migrate==3.0.0',
        'Flask-SQLAlchemy==2.5.1',
        'Flask-WTF==0.15.1',
        'hashids==1.3.1',
        'passlib>=1.7.4',
        'pytz>=2021.1',
    ],
    extras_require={
        'dev': [
            'rcssmin==1.0.6',
            'Flask-DebugToolbar>=0.11.0',
            'libsass>=0.21.0'
        ],
        'tasks': [
            'celery==5.1.0',
        ],
    },

    entry_points={
        'console_scripts': [
            'myapp=app.cli:cli.main',
        ]
    }
)
