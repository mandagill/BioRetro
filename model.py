"""TODO integrate SQLAlchemy, implement data model and seed the DB with 2014 data"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref


ENGINE = create_engine('postgresql://localhost:5432/BioRetro', echo=True)
Session = scoped_session(sessionmaker(bind=ENGINE, autocommit=False, autoflush=False))

Base = declarative_base()
# Base.query = session.query_property()

def make_tables():
	Base.metadata.create_all(ENGINE)


class HRDataPoint(Base):

	__tablename__ = "HRDataPoint"

	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey("User.id"), nullable = False)
	start_time = Column(String, nullable = False)
	end_time = Column(String, nullable = False)
	start_datetime = Column(DateTime)
	end_datetime = Column(DateTime)

	user = relationship("User", backref = backref("data_point", order_by=start_time) )

	def __repr__(self):
		
		return """I am a test object. My maker put me in the DB to better
		understand how to use SQLAlchemy and PostgreSQL together.
		I really don't do anything."""


class User(Base):

	__tablename__ = "User"

	id = Column(Integer, primary_key=True)
	email = Column(String, nullable = False)

	def __repr__(self):
		return "<User email: %s>" % self.email


def connect():
	pass #will need this after seeding the DB
	# global ENGINE
	# global Session
	
	# return Session()


def main():
	"""In case we need it """
	pass


if __name__ == '__main__': 
	main()

make_tables()


