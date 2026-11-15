from sqlalchemy import Column,Integer,String,Float,JSON,Text,Boolean,ForeignKey,UniqueConstraint
from src.config.database import Base
class User(Base):
 __tablename__='users'
 id=Column(Integer,primary_key=True);email=Column(String(100),unique=True,nullable=False);password=Column(String(200));role=Column(String(20))
class Metric(Base):
 __tablename__='metrics';__table_args__=(UniqueConstraint('code','version'),)
 id=Column(Integer,primary_key=True);code=Column(String(40),nullable=False);version=Column(Integer,nullable=False);name=Column(String(100));numerator=Column(String(200));denominator=Column(String(200));numerator_mode=Column(String(20));denominator_mode=Column(String(20));note=Column(Text,default='');locked=Column(Boolean,default=False)
class Fact(Base):
 __tablename__='facts';__table_args__=(UniqueConstraint('class_code','day'),)
 id=Column(Integer,primary_key=True);class_code=Column(String(50),nullable=False);day=Column(String(10),nullable=False);mode=Column(String(20));enrolled=Column(Integer);attended=Column(Integer);completed=Column(Integer);refunds=Column(Integer);note=Column(Text,default='')
class Snapshot(Base):
 __tablename__='snapshots'
 id=Column(Integer,primary_key=True);metric_id=Column(Integer,ForeignKey('metrics.id'));baseline_id=Column(Integer,ForeignKey('snapshots.id'),nullable=True);date_from=Column(String(10));date_to=Column(String(10));state=Column(String(20),default='queued');result=Column(JSON,nullable=True);error=Column(Text,default='');note=Column(Text,default='');approval=Column(String(20),default='draft');approved_by=Column(String(100),default='')
class Audit(Base):
 __tablename__='audits'
 id=Column(Integer,primary_key=True);actor=Column(String(100));action=Column(String(200));created=Column(String(40))
class FactEvent(Base):
 __tablename__='fact_events'
 id=Column(Integer,primary_key=True);fact_id=Column(Integer,nullable=False);op=Column(String(10),nullable=False,default='upsert');before=Column(JSON,nullable=True);after=Column(JSON,nullable=False);created=Column(String(40))
class Tracker(Base):
 __tablename__='trackers'
 id=Column(Integer,primary_key=True);snapshot_id=Column(Integer,ForeignKey('snapshots.id'),unique=True,nullable=False);state=Column(String(20),default='building');date_from=Column(String(10));date_to=Column(String(10));metric=Column(JSON);signed=Column(JSON);numerator=Column(Float,default=0.0);denominator=Column(Float,default=0.0);value=Column(Float,nullable=True);groups=Column(JSON,default=list);applied_event_id=Column(Integer,default=0);error=Column(Text,default='');updated=Column(String(40))
class TrackerContrib(Base):
 __tablename__='tracker_contribs';__table_args__=(UniqueConstraint('tracker_id','fact_id'),)
 id=Column(Integer,primary_key=True);tracker_id=Column(Integer,ForeignKey('trackers.id'),nullable=False);fact_id=Column(Integer,nullable=False);class_code=Column(String(50));day=Column(String(10));n=Column(Float,default=0.0);d=Column(Float,default=0.0)
