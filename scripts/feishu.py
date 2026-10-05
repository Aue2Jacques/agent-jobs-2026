import requests, json, sys
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36"
def search(base, keyword, portal_type=None, extra=None, limit=50, wp=None):
    s=requests.Session(); s.headers.update({"User-Agent":UA,"Referer":base+"/","Origin":base,"Content-Type":"application/json","website-path":wp or ("campus" if "bytedance" in base else "index")})
    r=s.post(base+"/api/v1/csrf/token",json={"portal_entrance":1}); 
    tok=r.json().get("data",{}).get("token") if r.ok else None
    s.headers["x-csrf-token"]=tok or ""
    body={"keyword":keyword,"limit":limit,"offset":0,"job_category_id_list":[],"location_code_list":[],"subject_id_list":[],"recruitment_id_list":[],"portal_type":portal_type or 3,"job_function_id_list":[],"portal_entrance":1}
    if extra: body.update(extra)
    r=s.post(base+"/api/v1/search/job/posts",json=body)
    return r.status_code, r.text[:300] if not r.ok else r.json()
if __name__=="__main__":
    code,d=search(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else None)
    if isinstance(d,str): print(code,d); sys.exit()
    print(code, d.get("code"), d.get("message"), d.get("data",{}).get("count"))
    for p in d.get("data",{}).get("job_post_list",[])[:60]:
        print(p.get("id"), p.get("title"), (p.get("recruit_type") or {}).get("name"), (p.get("recruit_type") or {}).get("parent",{}) and (p.get("recruit_type") or {}).get("parent",{}).get("name"), p.get("publish_time"))
