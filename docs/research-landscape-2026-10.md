# harness 评测与找 bug：论文和项目调研（2026-10-05）

> 用户定的方向：**给主流 harness 做评测、做分析、找问题**，不开发 harness，不做红蓝对抗、安全攻防。
> 本文回答三个问题：别人做到哪了？空位在哪？怎么做得更深？
>
> 读法说明：
> - "读全文"：网页版全文由抓取工具概括，或者本地解析 PDF 后读原文。
> - "只看摘要"：只读了搜索结果里的概括，**没核对全文**，引用前要补读。

## 一、结论

1. **这个方向确实很热**，今年至少有 4 个学术组在做（约克大学、港科大、Queen's 大学、南洋理工），论文按月出。
2. **现有工作分成两派，中间有空位**：
   - 一派**人工读 issue 做统计**，不复现；
   - 另一派**用真实模型跑基准**，贵、噪声大，而且分不清问题出在模型还是 harness。
   - 港科大和 Queen's 的论文**都明确呼吁**有人去做"模拟模型行为、专测 harness"的确定性测试和发版回归测试，但**还没人做出来**。
3. **E1 小实验正好是这个空位的雏形**。要做深，要往三处加深：
   - 注入的行为从"传输故障"扩展到港科大总结的 8 类模型异常；
   - 解决"静默错误怎么判定"这个公认难点；
   - 跨版本、跨 harness 做系统比较，产出别人没有的数据。

## 二、别人在做什么

### A. 人工读 issue，统计 bug 规律

| 论文 | 数据 | 主要发现 | 局限 | 读法 |
|---|---|---|---|---|
| [Engineering Pitfalls in AI Coding Tools](https://arxiv.org/abs/2603.20847)（约克大学、Concordia，**FSE '26 已录用**） | Claude Code 2343 + Codex 1192 + Gemini CLI 329 = 3864 个已关闭 bug，人工标注（κ=0.82） | 67% 是功能 bug；根因前三：API 与集成 21.4%、配置 15.9%、交互 11.1%；**模型行为只占 10%**；bug 集中在工具编排 37.6% 和命令执行 25.0% | 原文："we did not reproduce the studied bugs"；只有三家；人工标注主观 | 读全文；数据公开：[zenodo](https://zenodo.org/records/18342487) |
| [Agent-Reactive Bugs at the Model-Harness Boundary](https://arxiv.org/abs/2607.15684)（港科大，07-17，预印本） | Codex、Gemini CLI、LangChain、CrewAI，从 32373 个 issue 里筛出 255 个"模型行为触发的 harness bug" | 症状：**静默错误 42%**、崩溃 28%、报错 13%、重试死循环 13%、卡死 4%。触发行为 8 类：不遵守指令 67、工具参数异常 62、消息格式和模板冲突 49、harness 接口不成熟 23、编造状态 20、空回复 12、上下文溢出 11、调用不存在的工具 11。**同一种模型行为在不同 harness 上症状不同**。用户提的 PR 只有 38% 被合并 | **没做工具**；只统计，靠人工推断；没覆盖 Claude Code（闭源） | 读全文；未见数据链接 |
| [Where Agent Frameworks Fall Short](https://arxiv.org/abs/2602.21806)、[Understanding Bugs in Modern Agentic Frameworks](https://arxiv.org/abs/2604.08906) | AutoGen、CrewAI、LangChain 等框架的几千个 bug | 根因分类、触发条件组合 | 对象是开发框架，不是 CLI harness | 只看摘要 |

### B. 用真实模型跑基准，比较 harness

| 论文 | 做法 | 主要发现 | 局限 | 读法 |
|---|---|---|---|---|
| [Don't Blame the LLM](https://arxiv.org/abs/2607.03691)（Queen's 大学 Ahmed Hassan 组，07-20，投 TOSEM） | 固定模型 Qwen3-Next-80B，测 **Qwen Code 的 35 个连续版本** × 50 道 SWE-bench Verified × 2 次，共 3500 次运行 | **35 个版本没有统计显著的进步**，后期版本 token 和工具调用将近翻倍；回归能定位到具体 PR 和组件。原文呼吁："the absence of Agentic Quality Assurance, i.e., automated quality regression testing" | 只深入测了一家；一个模型；每题 2 次 | 读全文（本地解析 PDF） |
| [Finding the Right Fit](https://arxiv.org/abs/2610.00917)（南洋理工，**10-01**） | 4 个 harness（OpenHands、DSH、Pi、openJiuwen）× 5 个模型 × 3 个基准，6204 条轨迹 | 同一模型换 harness，排名能反转 38 个点。**关键原因是 harness 怎么把失败交还给模型**：Pi 的 shell 没有默认超时，34 次运行卡死；OpenHands 遇到格式错误的工具调用就终止；openJiuwen 把超时作为结构化反馈交还给模型。35 次失败的运行全部声称"已验证所有要求" | 每题只跑 1 次；设置不完全对齐 | 读全文；[代码和轨迹公开](https://github.com/liyix/finding-the-right-fit) |
| [The Scaffold Effect](https://arxiv.org/abs/2607.22585)（Sentient Labs） | Goose、OpenCode、OpenHands-SDK × 2 个模型 × 50 道 Terminal-Bench Pro | 每道解出的题，token 消耗最多差 40 倍；通过率只差 0–8 个点；OpenCode 平均每题有 2 个"什么都不做"的轮次 | n=50，很多差异在噪声范围内 | 读全文 |
| [Empirical Study of Harness Design](https://arxiv.org/abs/2609.20804)（UMass 等，09-17） | 自建 harness，在 4 个模型、2 个基准上拆分组件：上下文管理 5 档、规划、工具集与只用 bash | 组件的效果取决于模型大小和预算，没有通用最优解 | 不测现成的 harness；每题只跑 1 次 | 读全文 |
| [Stop Comparing LLM Agents Without Disclosing the Harness](https://arxiv.org/abs/2605.23950)（**ICML '26**，立场论文） | 控制论形式化加方差分解 | harness 带来的方差可以超过模型带来的方差 | 立场论文，没有新实验 | 只看摘要 |

### C. 自动化测试、找 bug

| 论文 | 做法 | 结果 | 局限 | 读法 |
|---|---|---|---|---|
| [ABTest](https://arxiv.org/abs/2604.03362)（约克大学，和 FSE 那篇同一组） | 从 400 个用户报告的 issue 抽出 47 种交互模式和 128 种动作，生成 647 个测试，**用真实模型**跑 Claude Code、Codex、Gemini CLI | 1573 个异常里人工确认 642 个，**查准率 40.8%**；花了 **2100 多美元**；**大多数异常跟具体模型有关**，几家之间很少重叠 | 只用了一个仓库（Click）；模型都是小模型（Haiku、mini、Flash-Lite） | 读全文 |
| [LogicHunter](https://arxiv.org/abs/2607.06195)（华中科大，07-07） | 对 LangChain、LlamaIndex、CrewAI 的 API 做模糊测试，用"agent 当判定器" | 找到 40 个 bug，确认 30 个，修复 26 个；判定查准率 91% | 测的是框架 API，**不是 CLI harness** | 读全文 |
| [AgentChaos](https://arxiv.org/abs/2608.06790)（中山大学等，**ASE '26**） | 在 LLM 接口层注入 6 种故障 | 稳健性取决于实现，不取决于模型；61–66% 是静默失败 | 测的是研究系统的重新实现，不是生产级 harness | 读全文（见 project-direction.md） |

### D. 单个机制的评测

- [Lost in Compaction](https://arxiv.org/abs/2608.11242)：上下文压缩后，会话约束平均只保留 17%。**只看摘要**。
- [Beyond Token Savings](https://arxiv.org/abs/2609.32961)：压缩策略会让一部分原本做对的题变错。**只看摘要**。

### E. 综述和源码研究

- [Harness Engineering: A Source-Code Study of Eleven Systems](https://arxiv.org/abs/2609.00006)（Wavestone）：读了 Claude Code、Codex、OpenCode、Pi、Hermes、OpenClaw 等 11 家，约 400 万行源码。没有一家用 LangChain 这类框架，全是手写循环；9/11 支持 Skills，8/11 支持 MCP。读全文。**适合做背景知识**。
- [Engineering Reliable Coding Agents](https://arxiv.org/abs/2608.13867)：一个人写的 313 页综述，没有同行评审，证据强度低，只当参考。

### 排除

- [ClayBuddy](https://arxiv.org/abs/2606.19380)：做安全和对齐（危险命令、越权），属于用户说的不碰方向。
- promptfoo 的红队、渗透测试功能：同上。

## 三、开源项目

| 项目 | 规模 [实测] | 是什么 | 和我们的关系 |
|---|---|---|---|
| [harbor-framework/harbor](https://github.com/harbor-framework/harbor) | 5839 星，10-05 还在更新 | Terminal-Bench 团队做的评测框架，能跑 Claude Code、Codex、OpenHands 等，上面几篇论文都用它 | 可以当 harness 运行器二开；**但本地要 Docker，我们的开发机没有 Docker 守护进程** |
| [CopilotKit/aimock](https://github.com/CopilotKit/aimock) | 960 星 | 模拟模型服务 | 可以当注入层；E1 发现它有 5 处不够用 |
| [neosigmaai/auto-harness](https://github.com/neosigmaai/auto-harness) | 545 星，09-16 更新 | 从基准运行中挖失败，自动改进 harness | 方向是"改 harness"，不是"测 harness" |
| [ai-boost/awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) | 4712 星 | 资料清单 | 用来查漏 |
| 论文附带的仓库（finding-the-right-fit、LogicHunter 等） | 1–5 星 | 复现代码 | 有数据可以用（南洋理工的 6204 条轨迹） |

## 四、空位在哪 [推断，依据见上]

1. **没人复现，就没法回归**：FSE 那篇统计了 3864 个 bug，但不复现；港科大那篇只做统计。人工统计的结论没法在 harness 下次发版时自动检查。
2. **用真实模型跑，测的是"模型 + harness"的混合体**：ABTest 发现大多数异常跟模型有关；南洋理工和 Scaffold 那两篇每题只跑 1 次。又贵又有噪声，分不清问题出在谁身上。
3. **两篇论文都点名要这个东西**：
   - 港科大原文："tests should preserve or mock the triggering behavior of LLMs, including the specific tool arguments, template-breaking message, or long context"，还建议做"trace-based oracles"（根据执行记录判定结果的检查器）；
   - Queen's 原文呼吁"automated quality regression testing"，在每次发版时做。
4. **南洋理工找到的"失败怎么交还给模型"**，恰好是可以确定性测量的 harness 属性，不需要真实模型。

所以空位是：**一套确定性、不依赖真实模型、能跨 harness、跨版本运行的测试**。它把"已知会触发 harness bug 的模型行为"固定成脚本，回放给真实的 harness 程序，再自动判定 harness 处理得对不对。

## 五、怎么做深（建议，待你确认）

### 技术深度：三个硬问题

1. **行为注入要真实**：注入的不只是 E1 的传输故障，还要覆盖港科大的 8 类模型异常：工具参数异常、破坏模板的消息、调用不存在的工具、空回复、超长输出、编造状态等。要覆盖 Anthropic、Chat Completions、Responses 三种协议，而且字节级忠实。E1 已经发现 aimock 在 Responses 协议上不忠实，所以要拿真实服务的流做对照校验。
2. **静默错误怎么判定**（公认难点，港科大说这类 bug 42% 没有明确的判定标准）。打算用三种办法互相印证：
   - **差分判定**：同一个注入，几家 harness 的结果互相对照；
   - **蜕变关系**：比如把空回复换成"空回复加一个空格"，正确的处理结果应该不变；
   - **核对状态**：把 harness 声称的结果和工作目录、请求日志里的实际情况对照。
3. **测试从真实 bug 自动生成**：用 FSE 公开的 3864 个 bug 和港科大的分类，把 issue 转成注入脚本。这一步可以用模型辅助，但每条要能在真实 harness 上复现，才算数。

### 发现深度：可能有的独家结论（都还没验证）

- **同一种模型异常，在各家 harness 上的症状分布**。港科大是从 issue 推断的，我们是实测，而且能覆盖 Claude Code。
- **harness 的失败处理能力随版本变好还是变差**。Queen's 只看了通过率，我们看失败处理；而且不花模型费用，可以扫几十个版本。
- **确定性测出的"失败处理画像"，能不能解释南洋理工看到的排名反转**。用他们公开的轨迹做对照，只用来验证我们的测量，不做轨迹归因工具（那是已否方向）。

## 六、风险和反面证据

1. **拥挤**：4 个组在做，约克大学一年出了两篇，下一篇很可能就是"确定性复现"。要快，而且要差异化：做真实 harness、确定性、跨版本。
2. **维护者不一定收**：港科大统计用户 PR 只有 38% 被合并；E1 里 OpenCode 那几个 issue 都开了一两个月。
3. **模拟可能不真实**：E1 已经踩到两次。模拟服务的忠实度本身要验证，否则测出来的是假 bug。
4. **静默错误的判定可能做不好**：这是最难的部分，也可能是做不成的部分。
5. **Harbor 要 Docker**：要么在开发机上想办法，要么继续用自己写的运行器（E1 已经跑通三家）。
6. **边界**：不做安全和红蓝对抗；不做轨迹失败归因；用南洋理工的轨迹只做验证。

## 七、下一步（一次只做一件）

先把港科大的 8 类触发行为和 FSE 的公开数据集读透，定下第一批要注入的模型行为，以及每种行为对应的"正确处理"判定标准。这一步不写代码，不花钱。
