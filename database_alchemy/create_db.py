import click
from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSON
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


class Result(Base):
    __tablename__ = 'results'

    # Here we define columns for the table results
    result_id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('samples.sample_id'))
    metrics = Column(JSON)
    sample = relationship("Sample", back_populates="results")


    def __repr__(self):
        return f"Result('{self.result_id}', '{self.sample_id}', '{self.metrics}'"


@click.command()
@click.argument('db_name')
@click.option('-a', '--ip-address', default='127.0.0.1', show_default=True,
              help='the ip address of the postgresql server to bind to.')
@click.option('-p', '--port', default='5432', show_default=True,
              help='the port of the postgresql server to bind to.')
def main(db_name, ip_address, port):
    '''Set up a project database for tracking analyses, samples, and results.

    The database schema applied to the database is generic in the sense that
    it should be suitable for most projects. The schema is the following:

    \b
      Table\tField\t\tType
      ---------+---------------+--------------
      Analyses:\tanalysis_id\t(Integer, PK)
               \tanalysis_name\t(String)
               \tdate\t\t(DateTime)
               \tdepartment\t(String)
               \tanalyst\t\t(String)
    \b
      Table\tField\t\tType
      ---------+---------------+--------------
      Samples:\tsample_id\t(Integer, PK)
              \tanalysis_id\t(Integer, FK)
              \tsample_name\t(String)
              \tsample_type\t(DateTime)
    \b
      Table\tField\t\tType
      ---------+---------------+--------------
      Results:\tresult_id\t(Integer, PK)
              \tsample_id\t(Integer, FK)
              \tmetrics\t\t(JSON)

    DB_NAME should be the name of a blank database which has already been created
    prior to running this script. To create a database, execute the following,
    where {project_x} refers to the name of the project/database:

    \b
      $ initdb Databases
      $ pg_ctl -D Databases -l logfile start
      $ createdb {projectx}
    '''
    engine = create_engine(f'postgresql://{ip_address}:{port}/{db_name}')
    Base.metadata.create_all(engine)