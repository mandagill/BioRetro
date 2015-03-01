from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

ENGINE = None
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
	start_datetime = Column(DateTime)
	end_datetime = Column(DateTime)

	user = relationship("User", backref = backref("data_point", order_by=start_time) )

	def __repr__(self):
		
		return """I am a data point. TODO make a for realsies __repr__ method."""

		# """<User id: %r, bpm: %r, start_time: %r,
		#  end_time: %r, start_datetime: %r, end_datetime: %r>""" % self.id, self.bpm, self.start_time, self.end_time, self.start_datetime, self.end_datetime


class User(Base):

	__tablename__ = "Users"

	id = Column(Integer, primary_key=True)
	email = Column(String, nullable = False)

	def __repr__(self):
		return "<User email: %s>" % self.email


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


