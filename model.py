from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
import os

ENGINE = None
Session = None
DATABASE_URL = os.environ.get(DATABASE_URL)


Base = declarative_base()
# Base.query = session.query_property()

def make_tables():
	""" This function intended for use when seeding the DB after making a schema change;
	it's hardcoded to the local DB for this reason."""
	ENGINE = create_engine('postgresql://localhost:5432/BioRetro', echo=False)
	Base.metadata.create_all(ENGINE)


class HRDataPoint(Base):

	__tablename__ = "HRDataPoints"

	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey("Users.id"), nullable = False)
	bpm = Column(Integer, nullable = False)
	start_time = Column(String, nullable = False)
	end_time = Column(String, nullable = False)
	start_datetime = Column(DateTime, nullable = True)
	end_datetime = Column(DateTime, nullable = True)
	day_of_point = Column(String, nullable = False)
	# This needs to be nullable since this info needs to be calculated after the HR record is created.
	is_stressful = Column(Boolean, nullable = True)

	def __repr__(self):
		
		return "<BPM: %r, date: %r>" % (self.bpm, self.day_of_point)


class User(Base):

	__tablename__ = "Users"

	id = Column(Integer, primary_key = True)
	email = Column(String, nullable = True)

	def __repr__(self):
		return "<User email: %s>" % self.email


def connect():

	global ENGINE
	global Session
	
	ENGINE = create_engine(DATABASE_URL, echo=False)
	Session = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

	return Session()


def main():
	"""In case we need it """
	pass


if __name__ == '__main__': 
	main()

# make_tables()
