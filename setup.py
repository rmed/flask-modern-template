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
        'bcrypt>=3.2.2',
        'email-validator==1.2.1',
        'Flask==2.1.3',
        'Flask-Assets==2.0',
        'Flask-Babel==2.0.0',
        'Flask-Login==0.6.1',
        'Flask-Mail==0.9.1',
        'Flask-Misaka==1.0.0',
        'Flask-Migrate==3.1.0',
        'Flask-SQLAlchemy==2.5.1',
        'Flask-WTF==1.0.1',
        'hashids==1.3.1',
        'passlib>=1.7.4',
        'pytz>=2022.1',
    ],
    extras_require={
        'dev': [
            'rcssmin==1.1.0',
            'Flask-DebugToolbar>=0.13.1',
            'libsass>=0.21.0'
        ],
        'tasks': [
            'celery==5.2.7',
        ],
    },

    entry_points={
        'console_scripts': [
            'myapp=app.cli:cli.main',
        ]
    }
)
