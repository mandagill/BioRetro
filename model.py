from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

ENGINE = create_engine('postgresql://localhost:5432/BioRetro', echo=True)
Session = None

Base = declarative_base()
# Base.query = session.query_property()

def make_tables():
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
	day_id = Column(Integer, ForeignKey("Days.id"), nullable = False)
	is_stressful = Column(Boolean, nullable = False)

	user = relationship("User", backref = backref("data_point", order_by=start_time) )

	def __repr__(self):
		
		return """I am a data point. TODO make a for realsies __repr__ method."""

		# """<User id: %r, bpm: %r, start_time: %r,
		#  end_time: %r, start_datetime: %r, end_datetime: %r>""" % self.id, self.bpm, self.start_time, self.end_time, self.start_datetime, self.end_datetime


class User(Base):

	__tablename__ = "Users"

	id = Column(Integer, primary_key = True)
	email = Column(String, nullable = True)

	def __repr__(self):
		return "<User email: %s>" % self.email


class Day(Base):

	__tablename__ = "Days"

	id = Column(Integer, primary_key = True)
	date = Column(String, nullable = False)
	is_stressful = Column(Boolean, nullable = False)

	datapoints = relationship("HRDataPoint", backref("day"))

	def __repr__(self):
		return "<Day object %s, Stressful is %r>" % self.date, self.is_stressful


def connect():

	global ENGINE
	global Session
	
	ENGINE = create_engine('postgresql://localhost:5432/BioRetro', echo=True)
	Session = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

	return Session()


def main():
	"""In case we need it """
	pass


if __name__ == '__main__': 
	main()

make_tables()

