import json,re,collections
d=json.load(open("jobs_raw.json"))
U=json.load(open("jobs_agent.json"))
eng=[v for v in U if v['cls']=='eng']
# add Tencent/Meituan AI app dev roles that mention Agent in text
extra_titles={'腾讯':['AI应用工程师','AI全栈工程师'],'美团':['AI应用开发工程师','AI后端开发工程师','AI全栈工程师','AI大模型后台开发']}
for v in d.values():
    if v['title'] in extra_titles.get(v['company'],[]) and re.search('agent|智能体',v['duty']+v['req'],re.I):
        v=dict(v,cls='eng'); eng.append(v)
st=json.load(open('jobs_startups.json'))
ds=json.load(open('deepseek.json'))
dsj=[dict(company='DeepSeek',title=x['title'],duty=x['text'],req='',url=x['detailUrl']) for x in ds['jobs'] if x['title'] in ('Agent Harness 团队','服务端开发工程师','Agent 弹性计算研发工程师')]
allj=eng+[dict(s) for s in st]+dsj
print('eng big4',len(eng),collections.Counter(v['company'] for v in eng)); print('total',len(allj))
K={
 'RAG/知识库':r'RAG|检索增强|知识库',
 '工具调用/Function Calling':r'工具调用|Function ?Call|Tool ?Use|tool calling|调用工具|工具系统',
 'MCP':r'\bMCP\b',
 'Skill(s)':r'\bSkills?\b|SKLLS',
 'A2A':r'\bA2A\b',
 'Memory/记忆':r'Memory|记忆',
 '上下文工程/Context':r'上下文工程|Context Engineering|上下文管理|上下文压缩|上下文',
 'Harness':r'Harness',
 '规划/Planning/推理':r'规划|Planning|Plan',
 '多Agent':r'多Agent|多智能体|Multi-?Agent|多 Agent',
 '评测/Eval':r'评测|评估|Eval|Benchmark|基准',
 'Badcase/数据飞轮/反馈闭环':r'badcase|bad case|数据飞轮|闭环|反馈',
 '可观测/Trace/日志':r'可观测|Trace|链路追踪|trajectory|轨迹|监控',
 '沙箱/隔离':r'沙箱|Sandbox|隔离|gVisor|E2B',
 '安全/权限':r'安全|权限|Guardrail|护栏',
 '成本/Token/缓存':r'成本|Token|KV ?Cache|缓存命中|Prompt Cach',
 '稳定性/可靠性':r'稳定性|可靠性|可靠|容错|重试|降级',
 '长程任务/状态/检查点':r'长程|长任务|长周期|状态管理|检查点|checkpoint|断点',
 '自进化/自我改进':r'自进化|自我进化|自演化|自我改进|self-?evol',
 'Prompt工程':r'Prompt|提示词',
 'RL/后训练':r'强化学习|\bRL\b|RLHF|GRPO|PPO|后训练|Post-?train',
 'SFT/微调':r'SFT|微调|fine-?tun|LoRA',
 'LangChain':r'LangChain',
 'LangGraph':r'LangGraph',
 'AutoGen/CrewAI/MetaGPT':r'AutoGen|CrewAI|MetaGPT',
 'Dify/Coze等平台':r'Dify|Coze|扣子|n8n',
 'Claude Code/Codex/Cursor/AI Coding':r'Claude Code|Codex|Cursor|AI ?Coding|Vibe ?Coding|AI 编程|AI编程|Trae|TRAE',
 'GUI/Computer/Browser Use':r'GUI|Computer ?Use|Browser|浏览器',
 'Python':r'Python',
 'Go':r'\bGo(lang)?\b|Golang',
 'Java':r'Java(?!Script)',
 'TypeScript/前端':r'TypeScript|React|Vue|前端|Node',
 'C++':r'C\+\+',
 'Rust':r'Rust',
 '分布式/高并发/微服务':r'分布式|高并发|微服务',
 '云原生/K8s/Docker':r'K8s|Kubernetes|Docker|云原生|容器|Serverless',
 'MySQL/Redis/MQ':r'MySQL|Redis|Kafka|消息队列|数据库',
 '开源贡献':r'开源',
 '顶会论文':r'顶会|论文|ACL|NeurIPS|ICML|ICLR',
 '竞赛(ACM等)':r'ACM|竞赛|比赛|ICPC|Kaggle',
 '端到端落地/产品化':r'落地|产品化|上线|生产环境|规模化',
}
def count(js):
    c=collections.Counter()
    for v in js:
        t=v['title']+'\n'+v['duty']+'\n'+v['req']
        for k,p in K.items():
            if re.search(p,t,re.I): c[k]+=1
    return c
c=count(allj); n=len(allj)
for k,x in c.most_common(): print(f"{k}\t{x}\t{x/n:.0%}")
json.dump(dict(n=n,counts=dict(c),companies=dict(collections.Counter(v['company'] for v in allj))),open('stats.json','w'),ensure_ascii=False)
json.dump(allj,open('jobs_final.json','w'),ensure_ascii=False,indent=1)
