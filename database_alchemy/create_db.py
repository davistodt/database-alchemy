import click
import pandas as pd
from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy import Integer, String, DateTime, Float, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Analysis(Base):
    __tablename__ = 'analyses'

    # Declaration of columns for the table analyses
    analysis_id = Column(Integer, primary_key=True)
    analysis_name = Column(String(20), nullable=False)
    date = Column(DateTime, default=func.now())
    department = Column(String(20))
    analyst = Column(String)
    samples = relationship("Sample", back_populates="analysis")


    def __repr__(self):
        return f"Analysis('{self.analysis_id}', {self.analysis_name}', " \
               f"'{self.date}', '{self.department}', '{self.analyst}, " \
               f"'{self.samples}')"


class Sample(Base):
    __tablename__ = 'samples'

    # Declaration of columns for the table samples.
    sample_id = Column(Integer, primary_key=True)
    sample_name = Column(String(20), nullable=False)
    sample_type = Column(String)
    analysis_id = Column(Integer, ForeignKey('analyses.analysis_id'))
    analysis = relationship("Analysis", back_populates="samples")
    results = relationship("Result", back_populates="sample")


    def __repr__(self):
        return f"Sample('{self.sample_id}', '{self.sample_name}', " \
               f"'{self.sample_type}')"


def get_data_types(csv_path):
    '''Generates a list of tuples containing (metric_name, SQLAlchemy Type)
     from a csv file.

    Args:
        csv_path (Union[str, Path]): path to the csv file

    Returns (List[Tuple[str, Class]]): list of (metric name, type)
     compatible with DB models
    '''
    metrics = pd.read_csv(csv_path).T
    metrics = metrics.itertuples()
    allowed_types = {'Boolean': Boolean, 'Float': Float, 'Integer': Integer,
                     'String': String}

    # replaces string representation of type with
    # the true SQLAlchemy type, using allowed_types
    data_types = [(metric[0], allowed_types[metric[1]])
                  if metric[1] in allowed_types.keys()
                  else (metric[0], String) for metric in metrics]

    return data_types


@click.command()
@click.argument('db_name')
@click.argument('metrics_declaration_csv')
def main(db_name, metrics_declaration_csv):
    '''Create a new project database.

    DB_NAME should be the name of the project (database) to be created,
    followed by '.sqlite'. For example: 'projectX.sqlite'.

    METRICS_DECLARATION_CSV should be a csv file containing the names and
    Python types of each of the metrics to be included as fields in the
    Results table. It should have the following structure:

    \b
      metric1,metric2,metric3
      Float,Float,Integer

    The following is a list of accepted data types: {Boolean, Float, Integer, String}
    '''
    engine = create_engine(f'sqlite:///{db_name}', echo=True)
    data_types = get_data_types(metrics_declaration_csv)

    attr_dict = {'__tablename__': 'results',
                 'result_id': Column(Integer, primary_key=True),
                 'sample_name': Column(String, ForeignKey('samples.sample_name')),
                 'sample': relationship("Sample", back_populates="results")}

    for metric_name, metric_type in data_types:
        attr_dict[metric_name] = Column(metric_type)

    # creates a new class 'Results' which inherits from
    # Base and has the attributes in attr_dict
    Result = type('Result', (Base,), attr_dict)

    Base.metadata.create_all(engine)