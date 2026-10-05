import requests,json,re,html,time,sys
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0"})
P=json.load(open('nc_posts.json'))
IDS=sys.argv[1].split(',')
out={}
try: out=json.load(open('nc_full.json'))
except: pass
for pid in IDS:
    p=P[pid]
    if p['type']==74:
        d=S.get(f"https://gw-c.nowcoder.com/api/sparta/detail/moment-data/detail/{p['uuid']}",timeout=20).json()['data']
        body=d.get('content') or ''; url=f"https://www.nowcoder.com/feed/main/detail/{p['uuid']}"
    else:
        d=S.get(f"https://gw-c.nowcoder.com/api/sparta/detail/content-data/detail/{pid}",timeout=20).json()['data']
        body=d.get('content') or ''; url=f"https://www.nowcoder.com/discuss/{pid}"
    body=html.unescape(re.sub(r'<br\s*/?>|</p>|</li>','\n',body)); body=re.sub(r'<[^>]+>','',body)
    out[pid]=dict(p,url=url,body=body,ip=d.get('ip4Location'))
    time.sleep(0.3)
json.dump(out,open('nc_full.json','w'),ensure_ascii=False,indent=1)
for pid in IDS:
    o=out[pid]; print('#####',pid,o['title'],o['url'],o['work'],o['author']); print(o['body'][:2500]); print()
