from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

 
Base = declarative_base()


class Analysis(Base):
    __tablename__ = 'analyses'
    # Here we define columns for the table analyses
    # Notice that each column is also a normal Python instance attribute.
    analysis_id = Column(Integer, primary_key=True)
    analysis_name = Column(String(20), nullable=False)
    date = Column(DateTime, default=func.now())
    department = Column(String(20))
    analyst = Column(String)
    samples = relationship("Sample", back_populates="analysis")


class Sample(Base):
    __tablename__ = 'samples'
    # Here we define columns for the table samples.
    # Notice that each column is also a normal Python instance attribute.
    sample_id = Column(Integer, primary_key=True)
    sample_name = Column(String(20), nullable=False)
    sample_type = Column(String)
    analysis_id = Column(Integer, ForeignKey('analyses.analysis_id'))
    analysis = relationship("Analysis", back_populates="samples")



def main():
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///sqlalchemy_example.db')
 
    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)