## 目标

* 构建一个面向 CTF 的 MCP Server，可被各类 agent/客户端连接，用于密码算法识别、经典与现代密码的解密、编码/混淆处理与辅助分析。

* 提供结构化输出、进度回报、日志提示与用户信息征询，提升竞赛解题效率。

## 技术选型

* **协议实现**：使用 FastMCP 高层接口，快速暴露 Tools/Resources/Prompts（参考 `d:\project\Key-Kid\MCP-README.md:139`, `d:\project\Key-Kid\MCP-README.md:308`）。

* **传输**：开发阶段用 `stdio`；部署面向 agent 使用 Streamable HTTP（参考 `d:\project\Key-Kid\MCP-README.md:1191`）。

* **结构化输出**：基于 Pydantic/TypedDict 等自动校验与模式生成（参考 `d:\project\Key-Kid\MCP-README.md:354`）。

* **进度/日志/采样/征询**：通过 Context 提供 `report_progress`、日志、采样与 `elicit()`（参考 `d:\project\Key-Kid\MCP-README.md:682`, `d:\project\Key-Kid\MCP-README.md:861`, `d:\project\Key-Kid\MCP-README.md:816`）。

* **认证（可选）**：支持 Token 验证与 OAuth 2.1 RS 模式（参考 `d:\project\Key-Kid\MCP-README.md:943`）。

## 目录与运行方式

* **代码位置**：`src/server.py`（主服务）、`src/tools/`（工具实现）、`src/resources/`（资源提供）、`src/prompts/`（提示模板）。

* **本地调试**：`uv run mcp dev src/server.py`（参考 `d:\project\Key-Kid\MCP-README.md:1086`）。

* **Claude 安装**：`uv run mcp install src/server.py`（参考 `d:\project\Key-Kid\MCP-README.md:1101`）。

* **HTTP 部署**：`python src/server.py` 或 `uv run mcp run src/server.py`，并启用 `streamable-http`（参考 `d:\project\Key-Kid\MCP-README.md:1191`）。

## 依赖与实现策略

* **必需**：`mcp[cli]`。

* **经典密码**：纯 Python 自实现，避免额外依赖（Caesar/ROT、Vigenère、Affine、Playfair、Rail Fence、列/行置换、Atbash、Baconian、Morse）。

* **现代密码/编码**：

  * 编码类：Base64/32/85/91、Hex、Binary/Octal、URL、Unicode escape。

  * XOR 家族：单字节、重复密钥；英语打分/IoC/Kasiski/Babbage 辅助。

  * 现代分组流密码（可选）：如需 AES/RC4/DES，计划引入 `cryptography` 或 `pycryptodome`，但以“需要密钥/IV/模式”的工具形态提供；若参数缺失，通过 `elicit()` 征询。

* **打分器**：英文字母频率/二元/三元模型与 IoC；可在首次版本采用简化频率 + IoC，后续再扩展。

## Tools 设计（首批）

* `detect_encoding(text)`：检测常见编码/变体，输出候选与置信度。

* `decode_common(text, tries=...)`：批量尝试常见编码（BaseX、Hex、URL、Unicode）并返回可能结果集。

* `rot_all(text)`：遍历 ROT\[1..25] 返回可读性评分最高的前 N 条。

* `caesar_break(ciphertext)`：频率分析 + 最佳移位；可选明文词典校验。

* `vigenere_break(ciphertext, max_key_len=16)`：IoC/Kasiski 估计密钥长度，枚举/启发式还原密钥候选。

* `affine_break(ciphertext)`：遍历 `(a,b)` 合法组合，评分选优。

* `playfair_break(ciphertext, key_hint=None)`：带 key\_hint 的半自动；无 hint 时先给评分最高的若干候选。

* `rail_fence_break(ciphertext, max_rails=10)`：枚举轨数并评分选优。

* `transposition_break(ciphertext, max_key_len=12)`：列置换枚举/启发式。

* `xor_single_break(data_hex|b64|raw)`：单字节 XOR 打分求解。

* `xor_repeating_break(data_hex|b64|raw)`：通过 Hamming 距离估计密钥长度并破解。

* `hash_identify(text)`：依据长度/字符集识别常见哈希（MD5/SHA1/SHA256 等），输出可能类型；不做暴力破解。

* `aes_decrypt(ciphertext_hex|b64, mode, key_hex|b64, iv_hex|b64)`：参数缺失时 `elicit()`。

* `rc4_decrypt(ciphertext_hex|b64, key_hex|b64)`：直接解密；参数缺失时 `elicit()`。

* 所有工具返回结构化模型 `DetectionResult`/`BreakResult` 等，便于 agent 消费（参考结构化输出 `d:\project\Key-Kid\MCP-README.md:454`）。

## Resources 设计

* `wordlist://{name}`：提供常用词表（如 `rockyou` 精简版、英文常用词、CTF 常见 key 列表）。

* `alphabet://{name}`：不同字母表/符号集。

* `samples://{id}`：内置样例密文用于快速验证。

* 资源数据采用只读方式，必要时用分页暴露（参考 `d:\project\Key-Kid\MCP-README.md:1919`）。

## Prompts 设计

* `AnalyzeCiphertext`：指导模型如何调用工具，何时征询缺失参数，如何解读结构化结果。

* `GuideBruteforce`：在密钥空间较大时提醒用户缩小范围/提供线索。

## 结构化输出模型

* `DetectionCandidate {name, score, decoded?}`。

* `BreakResult {algorithm, plaintext, key?, confidence, steps[]}`。

* `KeyCandidate {value, score}`。

* 所有模型通过 Pydantic 定义，自动生成 schema 并校验（参考 `d:\project\Key-Kid\MCP-README.md:354`）。

## 交互增强

* **进度上报**：长任务分步 `report_progress`（参考 `d:\project\Key-Kid\MCP-README.md:341`）。

* **日志等级**：`debug/info/warning/error` 区分（参考 `d:\project\Key-Kid\MCP-README.md:665`）。

* **征询**：参数缺失或歧义时 `elicit()`（参考 `d:\project\Key-Kid\MCP-README.md:822`）。

* **采样**：必要时用采样辅助生成解释或提示文本（参考 `d:\project\Key-Kid\MCP-README.md:867`）。

## 安全与性能

* 不读取/写入用户敏感数据；不在日志中泄露密钥。

* 限制暴力枚举的搜索空间与时间；在超时前返回部分候选并提示继续。

* 大文本/二进制采用分段处理与流式进度回报。

## 测试与验证

* 内置 `samples://` 提供若干标准密文，作为工具回归样例。

* 使用 MCP Inspector 与 `uv run mcp dev` 交互测试（参考 `d:\project\Key-Kid\MCP-README.md:1086`）。

* 为每个工具准备最小可复现的输入与期望输出，验证结构化字段完整性。

## 迭代计划

* **v0.1（核心）**：编码检测/解码、Caesar/ROT/Vigenère/Affine/Rail Fence、XOR 单字节/重复密钥、资源与基本提示。

* **v0.2（扩展）**：Playfair/置换加强、哈希识别、现代密码解密工具、`elicit()` 流程完善、Streamable HTTP 部署。

* **v0.3（增强）**：更强的替换/置换启发式、更多词表与分页资源、OAuth 认证、图像/二进制相关编码支持、图标与元数据完善。

## 最小示例（片段）

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("CTF Crypto")  # 参考 FastMCP 用法

class BreakResult(BaseModel):
    algorithm: str
    plaintext: str
    key: str | None = None
    confidence: float = Field(ge=0, le=1)

@mcp.tool()
def rot_all(text: str, top_k: int = 3) -> list[BreakResult]:
    results = []
    for k in range(1, 26):
        pt = ''.join(
            chr((ord(c)-65-k)%26+65) if 'A'<=c<='Z' else \
            chr((ord(c)-97-k)%26+97) if 'a'<=c<='z' else c
            for c in text
        )
        score = english_score(pt)  # 简化打分
        results.append(BreakResult(algorithm=f"ROT{k}", plaintext=pt, key=str(k), confidence=score))
    return sorted(results, key=lambda x: x.confidence, reverse=True)[:top_k]

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

* 结构化输出由 Pydantic 自动校验与生成 schema（参考 `d:\project\Key-Kid\MCP-README.md:354`）。

## 下一步

* 我将基于上述规划创建工程骨架、首批工具与资源，并提供可运行的 `src/server.py`，同时给出若干 \`

