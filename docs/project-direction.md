# 简历核心项目：从 JD 倒推（2026-10-05）

> 标记：**[实测]** 用 GitHub API / 官方接口取到的数；**[原文]** 引用；**[推断]** 我的判断；**[估计]** 没有实测的数。
> 选题标准沿用长期记忆：面试吸引力、真需求有证据、模型再强也替代不了、不太重、挂在已有 harness 上、二开的底座要几百星以上且一个月内在更新、不碰已否掉的方向。

## 一、结论

**推荐：做"Agent Loop 的流式故障注入测试"，底座二开 [CopilotKit/aimock](https://github.com/CopilotKit/aimock)。**

一句话说清楚：模型服务和网关经常返回各种"坏掉的流"，比如空回复、缺结束标记、发到一半断开、只发保活包。各家 harness 常把这些误判成"任务正常完成"，或者卡住不动。这个项目把 6 家 harness 里反复出现的这类故障整理成一套可复现的故障清单，放进 aimock 这个模拟模型服务里，再对真实的 harness 做黑盒测试，找出"假成功、卡死、不重试"的 bug，把修复提交回上游。

它不是我拍脑袋想出来的，是按"JD 要什么"和"已否掉的方向"两头排除后剩下的（第三节）。这个推荐**还有一个关键假设没验证**：在最新版的 harness 上还能不能复现出没修的 bug（第九节）。建议先花 2–3 天做个免费的小实验，再决定。

## 二、JD 和面经说明，项目要能证明四件事

来自 [README.md](README.md) 的统计：

1. **做的是 Agent 系统，不是调 API**：72% 的 JD 要求有 Agent 实践经验，83% 提"落地/上线"。[统计]
2. **能讲清 Harness 那一层**：字节 24 条 JD、DeepSeek 专门的团队都写了 Harness；16 篇面经里 6 篇问到；追问链是"Agent Loop → Runtime → Harness → Memory → Tool → Sandbox"。[统计][原文]
3. **能证明有效**：评测在 JD 里占 54%；面经最常追问"你怎么证明方案有效""离上线还差什么"。[统计][原文]
4. **懂可靠性**：58% 的 JD 提到稳定性、可靠性、重试、长任务、检查点这类词。面试题有"长任务从 5 分钟变成 20 分钟怎么查""Agent Loop 的停止条件""工具调用的可靠性怎么保证"。腾讯云 Agent Runtime 的招聘帖点名要"长任务……状态持久化、暂停恢复"。[统计][原文]

## 三、用否决清单筛一遍 JD 里的高频方向 [推断]

| JD 里的方向 | 占比 | 能不能做 | 原因 |
|---|---|---|---|
| RAG / 知识库 | 55% | 不做 | 面经里已经当基础题问，学生简历上太常见 |
| 多 Agent | 33% | 不做 | 已否（常见、agent-conway 太重） |
| 记忆 | 34% | 不做 | 已否 |
| 上下文 / 省 token / 缓存 | 39% / 18% | 只能当功能 | 已否当主项目 |
| 可观测 / Trace / 轨迹 | 32% | 不做 | 已否（录制、trace 一类） |
| 沙箱 / 安全 | 11% / 28% | 不做 | 已否（不喜欢） |
| Skills / 规则文件 | 7% | 不做 | 模型变强就被吃掉；skill 评测官方已内置（`claude plugin eval`） |
| 代码理解 / 验收 AI 代码 | 面经 5/16 | 不做 | 已否（直接让模型 review 就行） |
| **Agent Loop 可靠性：终止判定、重试续跑、长任务卡死** | 58%（宽口径）；失败恢复类 10%，长任务类 11% | **剩下的这个** | 问题出在网络、网关、模型服务，模型再强也修不了；是 harness 自己的职责 |

## 四、需求证据：同一类故障在各家反复出现 [实测]

### 4.1 五类故障 × 各家 harness（只列标题里看得出来的，2026-07-05 之后新建的）

| 故障类型 | 例子（仓库 #编号） |
|---|---|
| ① 空回复或异常回复被当成"正常完成" | OpenCode #41469（开着）、#37735（开着）、#50949（开着）、#40527（开着，子 agent 静默返回空）；Codex #32389（开着）；OpenClaw #108958、#126840；Hermes #82662、#92502、#118367（定时任务把退化输出当成功）；Pi #8233；Goose #10353；Claude Code #86427、#93419 |
| ② 流结束了却没有 finish_reason，或停在半句话却标成 stop | OpenCode #43379（开着）、#43882、#50146、#44385；Pi #8496、#8460、#7062；Hermes #132362（开着）、#126217（开着）、#102766；Claude Code #84551 |
| ③ 空闲看门狗判断错误：模型还在思考或只发保活包时被掐断，或者流卡死了却一直不超时 | Claude Code #85322、#95696（开着）、#82822（开着）、#75980；Codex #39771、#50775（开着，`codex exec` 卡死不超时）；OpenClaw #128354、#152535（开着）、#161915（开着）、#113323；Pi #9976；Hermes #120174、#96981；OpenCode #52049 |
| ④ 工具参数被截断后仍然执行，或被直接丢掉 | Pi #8501；Hermes #74798（开着）、#123832、#101899；OpenCode #52691 |
| ⑤ 网络错误不重试或重试策略不对，长会话中途死掉 | OpenCode #44540（开着）、#44641；Pi #9002、#10487；Hermes #58670、#74916；Codex #41810；Claude Code #89429 |

可以看出：Pi 一般当天就修；OpenCode、Hermes、OpenClaw、Codex 有不少已经开了几周到两个多月。每家都是一个个修，没有共享的测试清单，所以同一类问题在别家又出现一次。

### 4.2 粗略规模：近三个月标题命中数

关键词是 truncat、empty response、stream idle、stream interrupted、mid-task、stops responding、finish_reason。**含噪声、没有逐条筛**，只用来看量级：Claude Code 160、Hermes 138、OpenCode 85、OpenClaw 70、Codex 52、Pi 31、Qwen Code 15、Goose 4。

### 4.3 证据的弱点

- **单条 issue 票数很低**，大多是 0–11 个反应。证据靠的是"多、散、反复出现"，不是高票。
- 各家仓库里**已经有很多针对单个 bug 的单元测试**（代码搜索 "empty response test"：Hermes 940、Codex 916、Qwen Code 982 处命中）。所以空位不是"没人测"，而是"没有一套从真实故障整理出来、对真实程序做端到端黑盒测试的共享清单"。

## 五、为什么模型再强也替代不了

- 这些故障来自网络（NAT 4–5 分钟断开空闲连接，CC #82822）、网关（OpenCode Go、OpenRouter 不发 finish_reason）、模型服务（空回复、只有思考内容），不是模型笨。harness 要靠代码判断"这一轮到底完成了没有"。
- AgentChaos（[arXiv 2608.06790](https://arxiv.org/html/2608.06790)，ASE '26 录用，中山大学等）[原文]："The ranking is consistent across models, suggesting that robustness depends on system implementation rather than model capability." 它还测出 61–66% 的故障是**静默失败**（不报错）。
  - **它的局限**：测的是 AutoGen、MapCoder 等研究系统（在 Google ADK 上重新实现），**没有测 Claude Code、Codex、OpenCode 这类生产级 harness**；65 种配置平均每种只触发约 4.6 个任务，样本小；故障类型较粗（Empty、Truncate、Timeout 等），没有细到"缺 finish_reason""只发保活包"这一层。正好留出了我们的位置。

## 六、现有项目（正反两面）

| 项目 | 规模 [实测] | 做了什么 | 和我们的关系 |
|---|---|---|---|
| [CopilotKit/aimock](https://github.com/CopilotKit/aimock) | 960 星，MIT，TypeScript，10-05 还在更新；最近 100 个已关闭 PR 里，合并的有维护者 57 个、一位外部贡献者 16 个 | 模拟 11 家模型服务、22 种接口，支持流式、工具调用、录制回放；故障注入有 500、坏 JSON、断连接、429；fixture 能设 `finishReason`、`reasoning`，以及"发到第 N 块断开"（`truncateAfterChunks`）、"N 毫秒后断开"（`disconnectAfterMs`） | **底座**。缺的是"连接正常收尾、但内容语义有问题"这一类：没有 finish_reason 就收尾、只发保活不发内容、工具参数截断却标成 tool_calls、200 返回 HTML 错误页 |
| [MockServer](https://www.mock-server.com/mock_server/chaos_testing.html) | 4983 星，Java | 通用 HTTP 故障注入，有 LLM 模拟 | 太通用，不懂 agent 的语义 |
| [AgentChaos](https://github.com/IntelligentDDS/AgentChaos) | 4 星，8 月后没更新，CC BY-NC-ND | 论文代码 | 引用它当动机，不当底座 |
| agentic-chaos、agent-chaos、各种 OpenAI 兼容网关测试小工具 | 0–34 星 | 通用的 LLM 调用故障注入、网关兼容性测试 | 说明这个点子不难想到，**区别必须靠"在真实 harness 上找到真 bug"** |
| 各家 harness 自己的单元测试 | 见 4.3 | 每修一个 bug 补一个测试 | 我们是黑盒、跨版本、可复用的补充，不是替代 |

## 七、具体做什么

1. **整理故障清单**（约 1 周 [估计]）：从第四节这批 issue 里归纳出 10–15 种故障，每种写清楚线上的字节长什么样，以及期望 harness 怎么做（报错、重试、续写、超时）。这是数据工作，AI 替代不了的部分就在这里。
2. **二开 aimock**（约 1 周 [估计]）：大部分故障用现有 fixture 就能写出来；只补上面那几种它还不支持的故障，尽量提成上游 PR。
3. **跑真实 harness**（约 1 周 [估计]）：用无界面模式（`claude -p`、`codex exec`、`opencode run`、`pi -p`、`qwen -p`），通过 base URL 指向 aimock，输出"每种故障下 harness 有没有正确处理"的结果表。**全程不调真实模型，不花钱。**
4. **报 bug、提修复**（约 1 周 [估计]）：优先 OpenCode、Hermes、Qwen Code。这几家开源、接受外部 PR（OpenCode、Hermes 最近合并的 PR 里外部贡献者占 55%、62% [实测]），Qwen Code 还是阿里的项目。

规模：一个人约 4 周 [估计]。和你已有的积累有关：无界面跑 agent、隔离环境、中转站 62 秒截断这个坑你自己踩过。

**面试怎么讲** [推断]："我分析了 6 个主流 harness 近三个月的几百个 issue，归纳出 N 类流式故障，做成故障注入测试，在真实 harness 上复现出 X 个假成功或卡死的 bug，其中 Y 个修复被合并。"这能接住几个高频追问：Agent Loop 停止条件、长任务卡住怎么查、工具调用可靠性、怎么证明有效，也能讲清 Harness 层的职责边界。

## 八、风险

1. **可能找不到新 bug**：成熟的 harness 修得快（Pi 当天修），最新版也许都已经处理好了。这是最大风险，所以要先做第九节的实验。
2. **点子不新**：同类小工具很多，论文也有。价值只能靠真实 bug 的数量和合并的修复来证明。
3. **看起来像测试岗**：如果只停在"找 bug"，会被归到质量方向。所以第 4 步"自己修 Agent Loop 并被合并"不能省，这一步才是"Agent 开发"。
4. **会跑好几家 harness**：这是为了收集证据，不是做跨 harness 同步工具。产品本身是一套故障清单，用户只接自己用的那一家。需要你确认这样可以接受。
5. **Claude Code 不开源**：只能报 issue，提不了修复。
6. **aimock 维护者不一定收**：维护者自己写了大部分代码，有自动化的漂移检查流程。不收的话，就做成依赖 aimock 的独立仓库。

## 九、先验证再决定（免费，约 2–3 天 [估计]）

假设：**在最新版的 OpenCode、Codex（`codex exec`）、Hermes 上，用 aimock 现有的 fixture，至少能复现第四节五类故障里的 3 类，而且至少有 1 类是"假成功"。**

- 成立：方向站得住，开始做故障清单。
- 不成立：都修好了，说明需求已经被吃掉，换方向。不花钱，只花时间。

### 结果（2026-10-05，E1）

**假设成立**，详见 [experiments/E1-stream-faults.md](experiments/E1-stream-faults.md)。换成你说的"常见 harness"，测的是 Claude Code、Codex、OpenCode 的最新版：
- 5 类里复现了 3 类，三家都有"空回复当成功"。
- Codex 不发响应头时会一直干等。
- OpenCode 在没有结束标记时死循环，300 秒发了 2001 次请求。

但复现出的问题基本都已有人报过，讲法要从"找新 bug"改成"修 OpenCode 的 Agent Loop 终止判定"。

## 十、考虑过、排在后面的方向

| 方向 | 为什么排后 |
|---|---|
| 给招聘方自己的开源框架做贡献（字节 Eino 1.3 万星、阿里 AgentScope 3.3 万星） | 面试官认得，但要先在里面找到真需求，没有现成的需求证据；也不是"挂在 harness 上" |
| 无人值守 agent 的守护进程（卡死检测、自动续跑） | 是本方向的运行时版本。Codex `/goal` 等官方功能已覆盖"按目标续跑"，空位只剩"判断失败"，和本推荐重合 |
| harness 版本升级后行为回归检测（如 Claude Code Auto Mode 的提示词让 agent 滥用 bash，#87971 97 赞） | 离已否的"PR 行为差异报告""trace"太近 |
| 模型网关（claude-code-router 3.8 万星、new-api 4.9 万星）上做流修复 | 已否过类似的 GoModel；claude-code-router、new-api 近三个月标题里带 empty response / finish_reason 的 issue 只有个位数，问题主要暴露在 harness 一侧（判断"这一轮完成没有"是 harness 的事） |
