import os,time,json,logging
from pathlib import Path
import redis
from src.config.database import Session
from src.models.entities import Snapshot
from src.services.analysis import calculate
from src.services import tracking
r=redis.Redis.from_url(os.environ['REDIS_URL'])
ARTIFACTS=os.environ.get('ARTIFACTS_DIR','/artifacts')
with Session() as recovery:
 for pending in recovery.query(Snapshot).filter(Snapshot.state.in_(['queued','running'])).all():
  pending.state='queued';r.rpush('camp:snapshots',pending.id)
 recovery.commit()
while True:
 Path('/tmp/heartbeat').touch()
 try:
  item=r.blpop(['camp:snapshots','camp:tracking'],timeout=3)
  if item and item[0]==b'camp:snapshots':
   with Session() as s:
    row=s.get(Snapshot,int(item[1]))
    if row and row.state=='queued':
     snapshot=row.result['snapshot'];row.state='running';s.commit()
     try:
      row.result={**calculate(snapshot),'snapshot':snapshot};row.state='done'
      Path(ARTIFACTS+'/'+str(row.id)+'.json').write_text(json.dumps(row.result,ensure_ascii=False))
     except Exception as e:row.state='failed';row.error=str(e)
     s.commit()
  tracking.process_due()
 except Exception:logging.exception('worker');time.sleep(2)
