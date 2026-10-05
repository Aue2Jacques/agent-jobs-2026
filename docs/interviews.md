# 秋招 Agent 岗面经（牛客，2026-08 ~ 10）

来源：牛客网搜索接口，关键词"agent 面经""agent 二面 项目""harness 面经"等 12 组，按时间倒序取，人工挑出 Agent 方向、校招为主的帖子。索引在 `../data/interviews_nowcoder_index.json`（不转载全文，请看原帖）。

面经是作者自述，**没法核实**。下面问题都是 **[原文]**，"我的观察"是 **[推断]**。

## 一手面经（16 篇，参与统计）

| # | 面试或发帖日期 | 公司 / 岗位 / 轮次 | 作者标注 | 跟项目和 Agent 相关的问题（原文节选） | 链接 |
|---|---|---|---|---|---|
| 1 | 10-05 | 阿里云 Agent开发 一二面 | 27 届 | "Agent 自进化的原理，哪些因素会对自进化产生影响"；"了解过 DeepSeek Harness 吗" | [链接](https://www.nowcoder.com/feed/main/detail/fee780e1140147fbbad0f23a74e265c6) |
| 2 | 09-15 | 科大讯飞 Agent研发工程师-Harness方向 一面 | 27 届 | "简历上的 Agent项目是找的开源项目吗？是否投入过实际使用？"；"Agent Loop 的停止条件"；"如何理解 Harness"；"项目是你自己编写的，还是使用了 AI 工具辅助开发？" | [链接](https://www.nowcoder.com/feed/main/detail/671d2fa1d7c04322837ee1f5788dd69d) |
| 3 | 09-24 | 字节 Agent 秋招二面 | 27 届 | RAG 分块追问 7 层（"1,000 个 token，chunk size 为 400，最后剩余的 200 如何处理？"）；"企业级 RAG 与学习型 Demo 有哪些不同？" | [链接](https://www.nowcoder.com/discuss/932657562825027584) |
| 4 | 09-17 | 字节 AI Agent研发工程师 - AI算力基础设施 | 27 届 | "Agent Harness 最重要需要解决的问题是什么？"；"对 E2B 了解多少？是否使用过 E2B SDK 或类似的 Sandbox 方案？"；作者总结追问顺序"Agent Runtime → Agent Loop → Harness → Framework → Memory → Tool/Protocol → Sandbox" | [链接](https://www.nowcoder.com/discuss/930155293864914944) |
| 5 | 09-03 | 字节 Agent开发 一面 | 27 届 | "你如何理解Agent中Harness的概念？"；"长程的任务……平时5分钟就能结束……这次运行了15-20分钟……你会怎么分析这个延迟是什么导致的？"；"如何去保障工具调用的可靠性？"；"压缩或者摘要肯定会丢失信息，如何使得这个信息丢失最小化？" | [链接](https://www.nowcoder.com/discuss/925342611194286080) |
| 6 | 08-09 | 字节（TikTok）AI Agent开发 一面 | 27 届 | "上下文窗口是不是越大越好？"；"为什么选择多Agent协作，而不是单Agent完成所有任务？"；"多Agent系统为什么需要中心化编排？" | [链接](https://www.nowcoder.com/feed/main/detail/7b1b40fda3244715a82bcb4a821ca887) |
| 7 | 09-16 | 美团 AI Agent 一面 | 27 届 | "Agent流程较长，你们做了哪些保障措施，让每一步按预期推进？"；"置信度通过什么规则、约束来判断，什么情况需要二次确认用户？"；"项目的测试用例是你给出场景约束让AI生成，还是AI自己产出？"；"基础架构团队不能大面积使用AI，要做到什么程度才可以信任AI？" | [链接](https://www.nowcoder.com/feed/main/detail/50bcdc47e7754aa7be59b6318fea514b) |
| 8 | 08-28 | 蚂蚁 AI-Agent开发 一面 | 27 届 | "为什么选择使用Markdown方案进行记忆管理？相比RAG方案有什么考虑？"；"如果线上场景要求Agent全流程自动化，不依赖人工审核，如何设计机制保证系统稳定性和结果可靠？"；"Agent Harness包含哪些关键能力？为什么企业级Agent需要Harness？"；"Skill懒加载机制是如何实现的？" | [链接](https://www.nowcoder.com/feed/main/detail/6490526c86124f92b79a993e171f7222) |
| 9 | 08-17 | 阿里 Token Foundry AI应用研发 一面 | 未标 | "为什么不用react？"；"Critic 在整个工作流中主要解决什么问题？"；"为什么普通接口查询不能完全替代 Agent？" | [链接](https://www.nowcoder.com/feed/main/detail/6a7fbdcf484a4b2bbe4b900b2dbd5750) |
| 10 | 08-24 | 阿里 Token Foundry AI应用研发 二面 | 未标 | "如何防止 Planner、Executor 和 Critic 之间反复循环？"；"你对 RAG 做过哪些评测？如何分别评估召回质量和最终回答质量？"；"距离真正上线还有哪些工作要做？"；"哪些代码和设计是你亲自完成的，哪些是 AI Coding 辅助完成的？你如何验收 AI 生成的代码？" | [链接](https://www.nowcoder.com/feed/main/detail/ed25d2f60ddc4436b0139a7c52e62a61) |
| 11 | 09-03 | 阿里 Token Foundry AI应用研发 三面（挂） | 未标 | "你如何证明……方案是有效的？"；"业界通常是怎样处理长视频理解问题的？"；"本地 Agent 为什么会出现空转？"；"你认为 Claude Code 哪些功能做得比较好？" | [链接](https://www.nowcoder.com/feed/main/detail/bfd43b5c66784add8fbf5893c164697a) |
| 12 | 09-19 | 字节广告团队 agent 一二面 | 疑似社招 | 设计题"如何设计一个内部skill平台，包含skill的上传，下载，发布；本地runtime的设计"；"skill和Function Call的区别" | [链接](https://www.nowcoder.com/discuss/930870582843805696) |
| 13 | 09-22 | 理想 智能体应用开发 一面 | 27 届 | "Agent路由是怎么做的？LLM打分、关键词分类还是规则表？"；"如果用户一句话跨两类场景，路由是怎么处理的？" | [链接](https://www.nowcoder.com/feed/main/detail/5857f695ca2c4edda99e2befd20afafd) |
| 14 | 09-22 | vivo Agent开发 线下面 | 27 届 | "详细讲讲Harness吧"；"讲一个Agent工程中由于Harness环节做的不好而导致的问题，以及如何排查和解决" | [链接](https://www.nowcoder.com/discuss/932016298563809280) |
| 15 | 09-20 | 度小满 AI 全栈研发 二面 | 27 届 | 全程问实习里的 AI Coding 工作流："在代码生成阶段，你给 AI 提供了哪些辅助信息"；"实际去跑测试的 Agent 和负责验证结果正确性的 Agent，是同一个还是相互隔离的？"；"如果提取新记忆时发现与历史长期记忆有冲突……有什么解决冲突的逻辑？" | [链接](https://www.nowcoder.com/feed/main/detail/0bed1f22b62145f480d2c10c5ffd7951) |
| 16 | 09-16 | 阿里云 ai应用开发 一面 | 27 届 | "同事A和同事B都开发了一套RAG，你怎么选择，从哪些层面考虑"；"平时用什么ai coding工具" | [链接](https://www.nowcoder.com/feed/main/detail/7e27cf4dedb142d9b643471ba31276ed) |

## 话题出现次数（16 篇中）[统计]

关键词匹配后人工抽查过 Harness 和"AI 写的代码"两项，其他项未逐条核对。

| 话题 | 篇数 |
|---|---|
| 手撕算法 | 9 |
| 上下文膨胀 / 压缩 / 窗口 | 7 |
| RAG（切分 / 检索 / 重排） | 7 |
| 评测 / 怎么证明有效 | 7 |
| CS 基础八股（OS / 网络 / MySQL / Redis / Java） | 7 |
| Harness | 6 |
| 多 Agent / 角色拆分 / 路由 | 6 |
| 死循环 / 停止条件 / 空转 / 长任务 | 5 |
| 深挖候选人的 AI 编程过程（其中 4 篇问"哪些是你写的 / 怎么验收"） | 5 |
| 记忆（短期 / 长期 / 冲突） | 4 |
| Skill（懒加载 / Skill vs Tool） | 4 |
| 框架选型（LangChain / LangGraph / 手写） | 4 |
| 为什么用 Agent，不用规则或普通接口 | 4 |
| MCP | 3 |
| 工具调用可靠性 | 3 |
| 关注前沿（DeepSeek Harness / Claude Code） | 3 |
| 沙箱 / E2B / Runtime | 2 |

## 二手总结（5 篇，不参与统计，只作参考）

这些帖子是作者汇总别人的面经或"跟面试官聊"得来，有的带推广链接（培训课、题库），可信度低于一手面经。

| 帖子 | 说了什么 [原文] | 链接 |
|---|---|---|
| 近3个月Agent面试的题型，已经悄悄换了一套（08-21） | "Harness高频出现、评测体系成了必问项、成本优化开始被追问。这三个方向半年前几乎没人提"；"你们有没有fork过开源Harness，遇到upstream冲突怎么办" | [链接](https://www.nowcoder.com/discuss/920372737799979008) |
| Agent面试追问链（08-12） | "超过80%不是死在第一问，而是死在追问链的第三层或第四层"；"你的Agent调了三个工具就死循环了，异常处理在哪写的？"（称是字节的问题） | [链接](https://www.nowcoder.com/discuss/917092512525713408) |
| TikTok Agent工程师，面试到底考什么（08-18） | "LangChain/LangGraph你得熟，但在公司内部基本不用这些外部框架了"；"这个场景为什么用Agent而不用规则？badcase怎么回收？" | [链接](https://www.nowcoder.com/feed/main/detail/a9b91d99c9154a0da8876eaf56183930) |
| AI测开面试，开始追问"你怎么证明它做对了"（09-12） | "字节大模型测开三面让候选人为Coze的Skill设计评测集"；"只保存最后一句回答，往往看不出问题发生在哪一步" | [链接](https://www.nowcoder.com/feed/main/detail/3db2e6fcea514b2e8682995787730f98) |
| 去哪儿AI面试最后一题（09-15） | 多份去哪儿 AI 应用开发面试的最后一题都是"请分享一段你最近半年内主动学习AI工具或大模型相关技术，并尝试落地到实际开发场景的真实经历" | [链接](https://www.nowcoder.com/feed/main/detail/8eba647e1b0745038c68e324e69efbeb) |

另有一篇"美团AI全栈二面，过了"（[链接](https://www.nowcoder.com/discuss/932410744543379456)），回答写得像生成的范文、带精确提升数字，未采用。

## 我的观察 [推断]

1. **项目问得最深**。好几篇面经的一半以上篇幅在追问一个项目，追到"为什么这么设计 → 怎么证明有效 → 出错怎么查 → 离上线差什么"。
2. **"做了什么"不够，要"怎么知道做对了"**。评测在 JD 里占 54%，在面经里 7/16，二手总结也独立指出这一点。
3. **Harness 题在字节系和 DeepSeek 相关的面试里最多**，阿里/腾讯/美团的 JD 没写这个词，但阿里、蚂蚁的面试官也开始问。
4. **对 AI 编程的使用深度本身成了考点**：问你怎么用 AI 写代码、怎么验收、测试是谁生成的。
