from datetime import datetime,timezone
from sqlalchemy import func
from src.config.database import Session
from src.models.entities import Fact,FactEvent,Tracker,TrackerContrib
from src.services.expression import parse,execute
from src.services.analysis import ratio
LOCK_KEY=20261115
def now():return datetime.now(timezone.utc).isoformat()
def row_dict(f):return {c.name:getattr(f,c.name) for c in f.__table__.columns}
class RowFailure(Exception):
 def __init__(self,class_code,day,reason):super().__init__(f'班级 {class_code} 日期 {day} 行级计算失败：{reason}。已保留上次完整结果，修正该班级日事实后自动恢复。')
def contribution(metric,date_from,date_to,ntree,dtree,row):
 if row['day']<date_from or row['day']>date_to:return None
 n=execute(ntree,row) if metric['numerator_mode']=='全部' or row['mode']==metric['numerator_mode'] else 0.0
 d=execute(dtree,row) if metric['denominator_mode']=='全部' or row['mode']==metric['denominator_mode'] else 0.0
 return n,d
def set_contrib(s,tracker,ntree,dtree,row):
 try:c=contribution(tracker.metric,tracker.date_from,tracker.date_to,ntree,dtree,row)
 except ValueError as e:raise RowFailure(row.get('class_code','?'),row.get('day','?'),str(e))
 existing=s.query(TrackerContrib).filter_by(tracker_id=tracker.id,fact_id=row['id']).first()
 if c is None:
  if existing:s.delete(existing)
  return
 if not existing:existing=TrackerContrib(tracker_id=tracker.id,fact_id=row['id']);s.add(existing)
 existing.class_code=row['class_code'];existing.day=row['day'];existing.n,existing.d=c
def refresh(s,tracker):
 rows=s.query(TrackerContrib).filter_by(tracker_id=tracker.id).all()
 n=sum(r.n for r in rows);d=sum(r.d for r in rows);per={}
 for r in rows:
  g=per.setdefault(r.class_code,[0.0,0.0]);g[0]+=r.n;g[1]+=r.d
 tracker.numerator=n;tracker.denominator=d;tracker.value=ratio(n,d)
 tracker.groups=[dict(class_code=c,numerator=v[0],denominator=v[1],value=ratio(v[0],v[1])) for c,v in sorted(per.items())]
 tracker.updated=now()
def apply_events(s,tracker,ntree,dtree):
 events=s.query(FactEvent).filter(FactEvent.id>tracker.applied_event_id).order_by(FactEvent.id).all()
 latest={}
 for e in events:latest[e.fact_id]=e
 for e in latest.values():set_contrib(s,tracker,ntree,dtree,e.after)
 if events:tracker.applied_event_id=events[-1].id
 return len(events)
def build(s,tracker,ntree,dtree):
 s.query(TrackerContrib).filter_by(tracker_id=tracker.id).delete()
 for f in s.query(Fact).filter(Fact.day>=tracker.date_from,Fact.day<=tracker.date_to).all():set_contrib(s,tracker,ntree,dtree,row_dict(f))
 apply_events(s,tracker,ntree,dtree)
def fail(s,tid,message):
 s.rollback();t=s.query(Tracker).filter(Tracker.id==tid).with_for_update().first();t.state='error';t.error=message;t.updated=now();s.commit()
def process_one(tid):
 with Session() as s:
  t=s.query(Tracker).filter(Tracker.id==tid).with_for_update().first()
  if not t:return
  try:
   ntree,dtree=parse(t.metric['numerator']),parse(t.metric['denominator'])
   if t.state=='building':build(s,t,ntree,dtree)
   else:apply_events(s,t,ntree,dtree)
   refresh(s,t);t.state='tracking';t.error='';s.commit()
  except RowFailure as e:fail(s,tid,str(e))
  except ValueError as e:fail(s,tid,'聚合计算失败：'+str(e))
def process_due():
 with Session() as s:
  max_id=s.query(func.max(FactEvent.id)).scalar() or 0
  due=[t.id for t in s.query(Tracker).all() if t.state=='building' or t.applied_event_id<max_id]
 for tid in due:process_one(tid)
