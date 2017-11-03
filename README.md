# Database Alchemy
Learning databases with SQLAlchemy, PostgreSQL and Alembic.

## Setup and Installation

### Clone the repository
```
$ git clone https://github.com/16967143/database-alchemy.git
```

### Initial environment setup
In order to install this package, it is recommended to make use of a separate anaconda environment to avoid 
dependency conflicts. Anaconda can be easily downloaded and installed using the steps found 
[here](https://conda.io/miniconda.html).

Once installed, create a new conda environment:
```
$ conda create --name project-database --file requirements.env
```
Install all remaining package dependencies:
```
$ source activate project-database
$ pip install requirements.txt
$ pip install .
```
### PostgreSQL
To test and/or make use of these tools, an instance of PostgreSQL must be running. Although this is usually the
job of an IT/devops team, in some cases one may wish to set up their own local instance for these purposes. If 
this is required then the following steps can be taken:
```
$ source activate project-database
$ conda install --channels anaconda postgresql -y
```
Once installed, create a new database cluster:
``` 
$ initdb {Databases}  # where {Databases} is the name of a directory to store the databases in
```
And finally, start up a server:
```
$ pg_ctl -D {Databases} -l logfile start
```
Once an active server is running, new databases can be created for projects with the following command:
``` 
$ createdb {projectx}  # where {projectx} is the name of the new database to be created
```

## Usage Instructions

### Initialise a new project database
To set up a project database with the appropriate schema:
```
$ db-create {projectx}
```
**Note:** this script initialises an existing (but empty) database. In order to use it a database must already exist. 
To create an empty database, first run `createdb {projectx}`.
 
### Add data to a database
To add project metadata and results to a project database:
```
$ db-insert metadata.json results.csv {projectx}
```
More instructions to follow.

### Query a database
``` 
$ db-query [commands]
```
More instructions to follow.

## Learning Resources
* Original SQLAlchemy tutorial can be found at: http://pythoncentral.io/introductory-tutorial-python-sqlalchemy/.
* Great open source tool for interacting with PostgreSQL database: https://github.com/sqlectron/sqlectron-gui.
