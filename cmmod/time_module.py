import datetime
from datetime import timedelta, timezone

#現在の日付時刻を取得
def get_currenttime() -> str:
    #JSTタイムゾーンを作成
    jst = timezone(timedelta(hours=9),'JST')

    #JSTで日付を作成
    now = datetime.datetime.now(jst)
    time = now.strftime(r'%Y/%m/%d %H:%M:%S')
    return time

#文字列->日付時刻へ変換
def str_to_datetime(tstr:str) -> datetime.datetime:
    tdatetime = datetime.datetime.strptime(tstr,r'%Y/%m/%d %H:%M:%S')
    return tdatetime