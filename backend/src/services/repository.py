from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from src.models.entities import Metric,Fact,FactEvent
from src.services import tracking

def save_metric(s,data,i=None):
 r=s.get(Metric,i) if i else Metric()
 if not r:raise HTTPException(404,'口径版本不存在')
 if r.locked:raise HTTPException(409,'已签核口径不可覆盖，请建立新版本')
 for k,v in data.model_dump(mode='json').items():setattr(r,k,v)
 s.add(r)
 try:s.commit()
 except IntegrityError:s.rollback();raise HTTPException(409,'相同指标代码和版本已存在')
 return r

def save_fact(s,data,i=None):
 s.execute(text('SELECT pg_advisory_xact_lock(:k)'),{'k':tracking.LOCK_KEY})
 r=s.get(Fact,i) if i else Fact()
 if not r:raise HTTPException(404,'班级日事实不存在')
 before=tracking.row_dict(r) if i else None
 for k,v in data.model_dump(mode='json').items():setattr(r,k,v)
 s.add(r)
 try:s.flush()
 except IntegrityError:s.rollback();raise HTTPException(409,'相同班级与日期已有事实，请修订原记录')
 s.add(FactEvent(fact_id=r.id,op='upsert',before=before,after=tracking.row_dict(r),created=tracking.now()))
 try:s.commit()
 except IntegrityError:s.rollback();raise HTTPException(409,'相同班级与日期已有事实，请修订原记录')
 return r
