import os
import sys

#モジュール探索パス追加
p = ['../','../../']
for e in p: sys.path.append(os.path.join(os.path.dirname(__file__),e))

import datetime
from datetime import timedelta, timezone

def get_currenttime() -> str:
    #JSTタイムゾーンを作成
    jst = timezone(timedelta(hours=9),'JST')

    #JSTで日付を作成
    now = datetime.datetime.now(jst)
    time = now.strftime(r'%Y/%m/%d %H:%M:%S')
    return time