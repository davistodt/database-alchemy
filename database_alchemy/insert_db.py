from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .create_db import Analysis, Base, Result, Sample


def main():
    db_name = 'sqlalchemy_example.db'
    engine = create_engine(f'sqlite:///{db_name}')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a Session instance
    Base.metadata.bind = engine

    Session = sessionmaker(bind=engine)
    # A Session() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = Session()

    # For SQLite, foreign keys hve to be explicitly enforced with the following:
    session.execute('pragma foreign_keys=on')

    # Insert an Analysis in the analyses table
    new_analysis = Analysis(analysis_name='MSQ100', department='QC', analyst='DMT')
    print(new_analysis)
    session.add(new_analysis)

    # Insert a Sample in the samples table
    new_sample = Sample(sample_name='TEST1', sample_type='TEST', analysis=new_analysis)
    print(new_analysis)
    session.add(new_sample)

    # Insert a Result set into the results table
    new_result = Result(metric1=0.99, metric2=0.809, metric3=1.000005, sample=new_sample)
    session.add(new_result)

    session.commit()