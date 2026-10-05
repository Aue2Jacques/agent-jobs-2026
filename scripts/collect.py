import requests, json, time
from feishu import search as fs_search
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36"
KW=["Agent","智能体","大模型应用","AI应用","Harness","Coding"]
out={}
def add(co,id,title,url,duty,req,meta):
    k=f"{co}:{id}"
    if k not in out: out[k]=dict(company=co,id=str(id),title=title,url=url,duty=duty or "",req=req or "",meta=meta)

# ByteDance
for kw in KW:
    for off in range(0,400,100):
        c,d=fs_search("https://jobs.bytedance.com",kw,3,extra={"offset":off,"recruitment_id_list":["201"]},limit=100)
        L=(d.get("data") or {}).get("job_post_list") or []
        for p in L:
            rt=p.get("recruit_type") or {}
            if rt.get("name")!="正式": continue
            subj=((p.get("job_subject") or {}).get("name") or {}).get("zh_cn")
            add("字节跳动",p["id"],p["title"],f"https://jobs.bytedance.com/campus/position/{p['id']}/detail",p.get("description"),p.get("requirement"),{"subject":subj,"publish":p.get("publish_time"),"city":(p.get("city_info") or {}).get("name"),"category":(p.get("job_category") or {}).get("name")})
        if len(L)<100: break
print("bd",len(out))

# Tencent
s=requests.Session(); s.headers["User-Agent"]=UA
for kw in KW:
    for page in range(1,8):
        d=s.post("https://join.qq.com/api/v1/position/searchPosition",json={"projectIdList":[],"projectMappingIdList":[],"keyword":kw,"bgList":[],"workCountryType":0,"workCityList":[],"recruitCityList":[],"positionFidList":[],"pageIndex":page,"pageSize":50},timeout=30).json()
        L=(d.get("data") or {}).get("positionList") or []
        for p in L:
            if "实习" in (p.get("projectName") or "") or "应届" not in (p.get("recruitLabelName") or ""): continue
            k=f"腾讯:{p['postId']}"
            if k in out: continue
            det=s.get("https://join.qq.com/api/v1/jobDetails/getJobDetailsByPostId",params={"postId":p["postId"]},timeout=30).json().get("data") or {}
            add("腾讯",p["postId"],p["positionTitle"],f"https://join.qq.com/post_detail.html?postid={p['postId']}",det.get("desc"),det.get("request"),{"project":p.get("projectName"),"bgs":p.get("bgs")})
            time.sleep(0.2)
        if len(L)<50: break
print("tx",len(out))

# Meituan
for kw in KW:
    for page in range(1,10):
        d=s.post("https://zhaopin.meituan.com/api/official/job/getJobList",json={"page":{"pageNo":page,"pageSize":50},"jobShareType":"1","keywords":kw,"cityList":[],"department":[],"jfJgList":[],"jobType":[{"code":"1","subCode":[]}],"typeCode":[],"specialCode":[]},timeout=30).json()
        L=(d.get("data") or {}).get("list") or []
        for p in L:
            add("美团",p["jobUnionId"],p["name"],f"https://zhaopin.meituan.com/web/position/detail?jobUnionId={p['jobUnionId']}",p.get("jobDuty"),(p.get("jobRequirement") or "")+"\n"+(p.get("precedence") or ""),{"special":p.get("jobSpecialCode"),"first":p.get("firstPostTime"),"family":p.get("jobFamily")})
        if len(L)<50: break
print("mt",len(out))

# Alibaba
base="https://campus-talent.alibaba.com"; a=requests.Session(); a.headers["User-Agent"]=UA
a.get(base+"/campus/position-list?campusType=freshman&lang=zh",timeout=20); tok=a.cookies.get("XSRF-TOKEN")
h={"Referer":base+"/campus/position-list","Origin":base,"x-xsrf-token":tok}
for kw in KW:
    for page in range(1,10):
        c=a.post(base+"/position/search?_csrf="+tok,json={"channel":"new_campus_group_official_site","language":"zh","batchId":100000760001,"searchKey":kw,"pageIndex":page,"pageSize":50},headers=h,timeout=30).json()["content"]
        L=c.get("datas") or []
        for p in L:
            add("阿里巴巴",p["id"],p["name"],f"https://campus-talent.alibaba.com/campus/position/{p['id']}",p.get("description"),p.get("requirement"),{"circles":p.get("circleNames"),"modify":p.get("modifyTime"),"category":p.get("categoryName"),"project":p.get("niuKeProjectName")})
        if len(L)<50: break
print("ali",len(out))
json.dump(out,open("jobs_raw.json","w"),ensure_ascii=False,indent=1)
