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
        'Flask==1.1.2',
        'Flask-Assets==2.0',
        'Flask-Babel==1.0.0',
        'Flask-Login==0.5.0',
        'Flask-Mail==0.9.1',
        'Flask-Misaka==1.0.0',
        'Flask-Migrate==2.5.3',
        'Flask-SQLAlchemy==2.4.4',
        'Flask-WTF==0.14.3',
        'hashids==1.3.1',
        'passlib>=1.7.4',
        'pytz>=2020.5',
    ],
    extras_require={
        'dev': [
            'rcssmin==1.0.6',
            'Flask-DebugToolbar>=0.11.0',
            'libsass>=0.20.1'
        ],
        'tasks': [
            'celery==5.0.5',
        ],
    },

    entry_points={
        'console_scripts': [
            'myapp=app.cli:cli.main',
        ]
    }
)
