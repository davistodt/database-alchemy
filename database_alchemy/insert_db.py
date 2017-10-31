import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .create_db import Analysis, Base, Result, Sample


@click.command()
@click.argument('db_name')
@click.option('-a', '--ip-address', default='127.0.0.1', show_default=True,
              help='the ip address of the postgresql server to bind to.')
@click.option('-p', '--port', default='5432', show_default=True,
              help='the port of the postgresql server to bind to.')
def main(db_name, ip_address, port):
    '''Perform bulk CRUD operations on the database in the project context.

    So far, this script is only able to perform a hardcoded set of operations
    to demonstrate that the insert operation is successful. This will be expanded on.
    '''
    engine = create_engine(f'postgresql://{ip_address}:{port}/{db_name}')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a Session instance
    Base.metadata.bind = engine

    Session = sessionmaker(bind=engine)
    session = Session()

    # Insert an analysis in the analyses table
    new_analysis = Analysis(analysis_name='MSQ100', department='QC', analyst='DMT')
    session.add(new_analysis)

    # Insert two samples in the samples table
    sample_1 = Sample(sample_name='TEST1', sample_type='TEST', analysis=new_analysis)
    sample_2 = Sample(sample_name='REF1', sample_type='REFERENCE', analysis=new_analysis)
    session.add(sample_1, sample_2)

    # Insert two result sets, one for each sample
    metrics_1 = {'first_name': 'Guido', 'second_name': 'Rossum', 'titles': ['BDFL', 'Developer']}
    metrics_2 = {'first_name': 'Davis', 'second_name': 'Todt', 'titles': ['MR', 'Developer']}

    result_1 = Result(metrics=metrics_1, sample=sample_1)
    result_2 = Result(metrics=metrics_2, sample=sample_2)
    session.add(result_1, result_2)

    session.commit()