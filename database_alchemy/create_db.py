from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float,func
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Analysis(Base):
    __tablename__ = 'analyses'

    # Here we define columns for the table analyses
    analysis_id = Column(Integer, primary_key=True)
    analysis_name = Column(String(20), nullable=False)
    date = Column(DateTime, default=func.now())
    department = Column(String(20))
    analyst = Column(String)
    samples = relationship("Sample", back_populates="analysis")


    def __repr__(self):
        return f"Analysis('{self.analysis_id}', {self.analysis_name}', " \
               f"'{self.date}', '{self.department}', '{self.analyst}, '{self.samples}')"


class Sample(Base):
    __tablename__ = 'samples'

    # Here we define columns for the table samples.
    sample_id = Column(Integer, primary_key=True)
    sample_name = Column(String(20), nullable=False)
    sample_type = Column(String)
    analysis_id = Column(Integer, ForeignKey('analyses.analysis_id'))
    analysis = relationship("Analysis", back_populates="samples")
    results = relationship("Result", back_populates="sample")


    def __repr__(self):
        return f"Sample('{self.sample_id}', '{self.sample_name}', '{self.sample_type}')"



class Result(Base):
    __tablename__ = 'results'

    # Here we define columns for the table results
    result_id = Column(Integer, primary_key=True)
    sample_name = Column(String, ForeignKey('samples.sample_name'))
    metric1 = Column(Float)
    metric2 = Column(Float)
    metric3 = Column(Float)
    sample = relationship("Sample", back_populates="results")


    def __repr__(self):
        return f"Result('{self.result_id}', '{self.sample_name}', '{self.metric1}', " \
               f"'{self.metric2}', '{self.metric3}')"



def main():
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///sqlalchemy_example.db')
 
    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)