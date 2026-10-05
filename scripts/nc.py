import requests,json,time,re,datetime
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
posts={}
Q=["agent 面经","agent开发 一面","agent 二面 项目","大模型应用开发 面经","AI应用开发 面经","字节 agent 面经","阿里 agent 面经","腾讯 agent 面经","美团 agent 面经","agent 秋招 面经 拷打","harness 面经","智能体 面经"]
for q in Q:
  for page in (1,2,3):
    d=S.post("https://gw-c.nowcoder.com/api/sparta/pc/search",json={"type":"post","query":q,"page":page,"tag":[],"order":"create","gioParams":{}},timeout=20).json()
    for x in (d.get("data") or {}).get("records") or []:
        c=x.get("contentData") or x.get("momentData") or {}
        if not c.get("id"): continue
        ts=c.get("createTime") or c.get("showTime") or 0
        posts[c["id"]]=dict(id=c["id"],uuid=c.get("uuid"),title=c.get("title"),ts=ts,type=x.get("contentType"),author=(x.get("userBrief") or {}).get("authDisplayInfo"),work=(x.get("userBrief") or {}).get("workTime"),snippet=(c.get("content") or "")[:200])
    time.sleep(0.3)
json.dump(posts,open("nc_posts.json","w"),ensure_ascii=False,indent=1)
print(len(posts))
for p in sorted(posts.values(),key=lambda p:-p['ts']):
    t=datetime.datetime.fromtimestamp(p['ts']/1000).strftime('%Y-%m-%d') if p['ts'] else '?'
    if p['ts'] and p['ts']>datetime.datetime(2026,7,15).timestamp()*1000 and re.search(r'面|拷打|问',p['title'] or ''):
        print(t,p['id'],p['type'],p['work'],'|',p['title'])
