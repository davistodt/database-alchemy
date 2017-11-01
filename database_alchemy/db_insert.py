import click
import json
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db_create import Analysis, Base, Result, Sample


def create_analysis(json_file):
    '''Create an instance of Analysis from a json metadata file.

    Args:
        json_file (Union[str, Path]): path to the metadata json file.

    Returns (:obj:`Analysis`): analysis object which can be inserted
        into the database with the SQLAlchemy ORM.
    '''
    with open(json_file) as of:
        json_data = json.load(of)

    json_data = json_data['Analysis']
    field_names = ['analysis_name', 'date', 'department', 'analyst']

    analysis_data = {}
    for field in field_names:
        if field in json_data:
            analysis_data[field] = json_data[field]
        else:
            # log warning
            pass

    return Analysis(**analysis_data)


def create_samples(json_file, analysis_obj):
    '''Create a list of Sample instances from a json metadata file.

    Args:
        json_file (Union[str, Path]): path to the metadata json file.
        analysis_obj (:obj:`Analysis`): analysis object to be used by
            SQLAlchemy for foreign key association with samples.

    Returns (List[:obj:`Sample`]): list of sample objects which
        can be inserted into the database with the SQLAlchemy ORM.
    '''
    with open(json_file) as of:
        json_data = json.load(of)

    json_data = json_data['Samples']
    field_names = ['sample_name', 'sample_type', 'sample_description']

    samples_list = []
    for sample in json_data:
        sample_data = {}
        for field in field_names:
            if field in sample:
                sample_data[field] = sample[field]
            else:
                # log warning
                pass
        sample_data['analysis'] = analysis_obj  # required for sample:analysis relationship
        samples_list.append(Sample(**sample_data))

    return samples_list


@click.command()
@click.argument('metadata_json', type=click.Path(exists=True, dir_okay=False))
@click.argument('results_csv', type=click.Path(exists=True, dir_okay=False))
@click.argument('db_name')
@click.option('-a', '--ip-address', default='127.0.0.1', show_default=True,
              help='the ip address of the postgresql server to bind to.')
@click.option('-p', '--port', default='5432', show_default=True,
              help='the port of the postgresql server to bind to.')
def main(metadata_json, results_csv, db_name, ip_address, port):
    '''Insert new project data into an existing database by supplying a results
    csv file and an accompanying metadata json file describing the analysis.

    The METADATA_JSON file has a fixed structure. It must be valid json
    containing the top-level fields {'Analysis', 'Samples'}. The Analysis block
    must be a mapping of analysis-level metadata. The Samples block must be an
    array of mappings of sample-level metadata. The schema is the following:

    \b
      {
        "Analysis": {
          "analysis_name": "Troubleshoot drop out rates",
          "date": "2017-09-20",
          "department": "IT",
          "analyst": "Guido van Rossum"
        },
        "Samples": [
          {
            "sample_name": "sample01",
            "sample_type": "Reference",
            "sample_description": "NA"
          },
          {
            "sample_name": "sample02",
            "sample_type": "Test",
            "sample_description": "NA"
          }
        ]
      }

    The RESULTS_CSV file must contain a column corresponding to the sample names
    in the JSON file, followed by a column for each metric. The format is the
    following:

    \b
      sample_name\t{metric_1}\t{metric_2}\t{metric_3}\t.
      ----------------+---------------+---------------+---------------+-----
      sample01\t\t0.6\t\t45\t\t1500\t\t.
      sample02\t\t0.9\t\t12\t\t3000\t\t.

    '''
    engine = create_engine(f'postgresql://{ip_address}:{port}/{db_name}')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a Session instance
    Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        analysis = create_analysis(metadata_json)
    except Exception as e:
        click.echo(e)
        raise
    else:
        session.add(analysis)

    try:
        samples = create_samples(metadata_json, analysis)
    except Exception as e:
        click.echo(e)
        raise
    else:
        session.add(*samples)

    # # Insert an analysis in the analyses table
    # new_analysis = Analysis(analysis_name='MSQ100', department='QC', analyst='DMT')
    # session.add(new_analysis)
    #
    # # Insert two samples in the samples table
    # sample_1 = Sample(sample_name='TEST1', sample_type='TEST', analysis=new_analysis)
    # sample_2 = Sample(sample_name='REF1', sample_type='REFERENCE', analysis=new_analysis)
    # session.add(sample_1, sample_2)
    #
    # # Insert two result sets, one for each sample
    # metrics_1 = {'first_name': 'Guido', 'second_name': 'Rossum', 'titles': ['BDFL', 'Developer']}
    # metrics_2 = {'first_name': 'Davis', 'second_name': 'Todt', 'titles': ['MR', 'Developer']}
    #
    # result_1 = Result(metrics=metrics_1, sample=sample_1)
    # result_2 = Result(metrics=metrics_2, sample=sample_2)
    # session.add(result_1, result_2)

    session.commit()