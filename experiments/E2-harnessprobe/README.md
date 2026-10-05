# harnessprobe

用模拟的模型服务给 agent harness（Claude Code、Codex、OpenCode，或公司内部的 harness）找 bug。

**思路**：harness 的很多 bug 是被模型服务的某种返回触发的，比如空回复、流断在半路、工具参数不完整、过载报错。真实模型很难稳定地产生这些情况，用模拟服务就能每次都复现。所以这里的测试：
- **不调用真实模型**，不花钱；
- **结果确定**，同一场景每次跑的结果都一样；
- **只测 harness 自身的代码**，比如它怎么判断一轮结束、怎么重试、怎么执行工具。

## 用法

```bash
python3 -m harnessprobe list                       # 每家 harness 支持哪些场景
python3 -m harnessprobe run --harness cc,codex,oc  # 跑全部场景（三家并行）
python3 -m harnessprobe run --harness oc --scenarios EMPTY,RAW_NOFINISH
python3 -m harnessprobe summary --out out          # 输出"harness × 场景"的判定表
```

用环境变量指定各程序的路径：`HP_AIMOCK_BIN`、`HP_CLAUDE_BIN`、`HP_CODEX_BIN`、`HP_OPENCODE_BIN`。

## 结构

```
harnessprobe/
  adapters/      一家 harness 一个适配器（接入新 harness 只改这里）
    base.py        适配器要回答的四个问题
    claude_code.py codex.py opencode.py
  scenarios.py   场景：只用通用动作写一次，适配器负责翻译
  runner.py      启动模拟服务 → 在隔离目录里跑 harness → 统计请求次数 → 判定
  mock/rawsse.py aimock 表达不了的流故障（没有结束标记、开始后卡住、只发保活包、真实的长度截断事件）
```

正常回复、工具调用、报错和"发到第 N 块断开"由 [aimock](https://github.com/CopilotKit/aimock) 提供；它表达不了的流故障由 `rawsse.py` 提供。

## 接入一家新 harness

写一个 `Adapter` 子类，回答四个问题：

1. **怎么启动**：`command()` 给出无界面运行的命令，`env()` 和 `setup()` 用隔离的配置目录把模型地址指向模拟服务。
2. **说哪种协议**：`protocol`，可选 `anthropic`、`chat`、`responses`。
3. **工具怎么对应**：`tools` 把通用动作映射到这家的工具名和参数名。比如"执行命令"在 Claude Code 是 `Bash.command`，在 Codex 是 `exec_command.cmd`，在 OpenCode 是 `bash.command`。
4. **怎么读结果**：`parse()` 从它的输出里取出退出码、最终文本、报错和工具调用记录。

## 判定

| 判定 | 含义 |
|---|---|
| PASS | 正确：如实报错，或者完整恢复 |
| FALSE_SUCCESS | 假成功：出了故障却以成功结束，结果是空的或半截的 |
| RETRY_STORM | 重试风暴：一次运行里发了 50 次以上请求 |
| HANG | 卡死：超时，而且只发过 1 次请求 |
| SLOW_RETRY | 超时，但期间一直在重试 |
| EXECUTED_INVALID | 执行了不完整或不合法的工具调用 |
| NOT_EXECUTED | 正常的工具调用没有执行 |

## 已知局限

- 还没有"请求合法性"判定，也就是校验 harness 发出的请求能不能被真实接口接受；这是下一步。
- aimock 在 Responses 协议下发"因长度截断"的事件不符合真实接口，所以 Codex 的 LEN0 场景要以 RAW_INCOMPLETE 为准。
- `rawsse.py` 在 Chat Completions 协议下还没实现"因长度截断"。
- 只测了无界面模式。
