import datetime
from collections import OrderedDict

import click
import pandas as pd
from sqlalchemy import create_engine, cast, Date
from sqlalchemy.orm import sessionmaker

from .db_create import Analysis, Base, Result, Sample


def return_dataframe(query):
    '''Convert a SQLAlchemy query object into a data frame for plotting.

    The query object assumes that instances of both Sample and Result are
    present.

    Args:
        query (:obj: `Query`): SQLAlchemy query result

    Returns (:obj: `DataFrame`): pandas data frame with columns corresponding
      to sample names and metrics from the results table (flattened from json).
    '''
    rows = []
    for record in query:
        result, sample = record
        row = OrderedDict([('sample_name', sample.sample_name), ('analysis_id', sample.analysis_id)])
        row.update(result.metrics.items())
        rows.append(row)

    return pd.DataFrame(rows)


def get_results_by_analysis(session, analysis_id=None):
    '''Query the database for all samples and associated metrics linked
    to one or more analysis_id and return the result as a pandas data frame.

    The metrics in the results table are stored in the database as json.
    This function also unpacks these metrics as key:value pairs and creates
    separate columns for them in the resulting data frame.

    Args:
        session (:obj: `Session`): SQLAlchemy session instance to query
        analysis_id (Union[int, List[int]]): analysis id(s) to use for filtering
        records.

    Returns (:obj: `DataFrame`): pandas data frame with columns corresponding
      to sample names and metrics from the results table (flattened from json).
    '''
    query = session.query(Result, Sample).join(Sample)
    print(type(query))

    if analysis_id and isinstance(analysis_id, list):
        query = query.filter(Sample.analysis_id.in_(analysis_id)).all()
    elif analysis_id:
        query = query.filter(Sample.analysis_id == analysis_id).all()

    return return_dataframe(query)


def get_results_by_sample(session, sample_name=None):
    '''Query the database for all results linked to one or more sample and
    return the result as a pandas data frame.

    Samples can be supplied as either a sample_name (str) or list of sample_names
    if multiple samples are to be queried.

    Args:
        session (:obj: `Session`): SQLAlchemy session instance to query
        sample_name (Union[str, List[str]]): sample name(s) to use for filtering
        records.

    Returns (:obj: `DataFrame`): pandas data frame with columns corresponding
      to sample names and metrics from the results table (flattened from json).
    '''
    query = session.query(Result, Sample).join(Sample)

    if sample_name and isinstance(sample_name, list):
        query = query.filter(Sample.sample_name.in_(sample_name)).all()
    elif sample_name:
        query = query.filter(Sample.sample_name == sample_name).all()

    return return_dataframe(query)


@click.command()
@click.argument('db_name')
@click.option('-a', '--ip-address', default='127.0.0.1', show_default=True,
              help='the ip address of the postgresql server to bind to.')
@click.option('-p', '--port', default='5432', show_default=True,
              help='the port of the postgresql server to bind to.')
def main(db_name, ip_address, port):
    '''Perform a query on a project database.

    Currently, all queries have been hardcoded as a proof of concept.
    Eventually however, this script will be able to perform useful queries at the user's demand.
    Results will also be able to be saved as csv files if requested.
    '''
    engine = create_engine(f'postgresql://{ip_address}:{port}/{db_name}')
    Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    session = Session()

    # find all analyses:
    analyses = session.query(Analysis)
    for analysis in analyses:
        print(analysis.analysis_id)

    # find all analyses where date < or > x
    analysis = session.query(Analysis).filter(cast(Analysis.date, Date) <= '2017-09-20').all()
    analysis = session.query(Analysis).filter(cast(Analysis.date, Date) <= datetime.date.today()).all()
    print(analysis)

    # find all analyses where analyst/department/etc = x
    analysis = session.query(Analysis).filter(Analysis.analyst == 'DMT').all()
    analysis = session.query(Analysis).filter(Analysis.department == 'QC').all()
    print(analysis)

    # find all samples and results for a given analysis and return as a pandas data frame
    df = get_results_by_analysis(session, analysis_id=[1])
    print(df)

    # find all results for a given sample and return as a pandas data frame
    df = get_results_by_sample(session, sample_name=['S01'])
    print('\n', df)

    # find results of a single metric across all samples for a given analysis