# Key-Kid

CTF 密码学 MCP Server，提供面向 agent 的多种密码算法识别、解码与破解工具，助力快速解决比赛题目。

## 特性
- 编码识别/解码：Base64/32/16/85、Hex、URL、Unicode Escape
- 经典密码破解：Caesar/ROT、Vigenère、Affine、Rail Fence、列式置换、Playfair（支持 key 提示）
- XOR 家族：单字节与重复密钥破解
- RC4 解密：支持缺参时交互征询密钥
- 结构化输出、可用于自动化 agent 流程

## 安装
- 安装 MCP Python SDK
  - `pip install "mcp[cli]"`

## 运行
- 开发调试：`uv run mcp dev src/server.py`
- 直接运行 HTTP：`python src/server.py`（默认 `streamable-http`）
- 安装到 Claude Desktop：`uv run mcp install src/server.py`

## 可用工具
- `tool_detect_encoding(text, top_k)`：编码候选与解码文本
- `tool_decode_common(text, limit)`：批量常见编码解码
- `tool_rot_all(text, top_k)`：遍历 ROT[1..25]
- `tool_caesar_break(ciphertext)`：Caesar 最优移位
- `tool_vigenere_break(ciphertext, max_key_len, top_k)`：密钥长度估计并破解
- `tool_affine_break(ciphertext, top_k)`：遍历参数并评分选优
- `tool_rail_fence_break(ciphertext, max_rails, top_k)`：枚举轨数
- `tool_transposition_break(ciphertext, max_key_len, top_k)`：小规模置换枚举
- `tool_playfair_break(ciphertext, key_hint)`：使用给定 key 解密
- `tool_xor_single_break(data, encoding, top_k)`：单字节 XOR 破解
- `tool_xor_repeating_break(data, encoding, min_key, max_key)`：重复密钥 XOR 破解
- `tool_rc4_decrypt(ciphertext, cipher_encoding, key?, key_encoding)`：RC4 解密（缺参时交互征询）
- `tool_factor_integer(n, prefer_yafu, timeout)`：整数因式分解，优先尝试本机 `yafu`，否则自动回退到内置算法
- `tool_hash_identify(text)`：依据长度/字符集识别常见哈希类型
- `tool_aes_decrypt(ciphertext, cipher_encoding, key?, key_encoding, iv?, iv_encoding, mode)`：AES 解密（ECB/CBC），依赖 `pycryptodome` 或 `cryptography`，缺参时交互征询
- `tool_des_decrypt(ciphertext, cipher_encoding, key?, key_encoding, iv?, iv_encoding, mode)`：DES 解密（ECB/CBC），依赖同上
- `tool_rot_all_wordlist(text, top_k, wordlist_name)`：结合词表与英文评分挑选更佳候选

## 样例资源/提示
- `samples://{id}`：如 `rot13_hello`、`xor_single_hex`
- `wordlist://{name}`：常用词表，如 `common` 与 `ctf`
- Prompt：`AnalyzeCiphertext` 引导调用顺序与策略

## 手动接入 JSON 示例（参考 MCP-README）

### Claude Desktop（手动配置）
将以下片段添加到 Claude Desktop 的配置文件中（示例结构）：

```json
{
  "mcpServers": {
    "CTF Crypto": {
      "command": "python",
      "args": [
        "d:/Key-Kid/src/server.py"
      ],
      "env": {
        "PYTHONPATH": "d:/Key-Kid"
      }
    }
  }
}
```


### Streamable HTTP 客户端配置
若以 HTTP 方式提供服务（参考 `d:\Key-Kid\MCP-README.md` 的 Streamable HTTP 章节），客户端可使用如下 JSON 指定服务器地址：

```json
{
  "server_url": "http://localhost:8000/mcp"
}
```

### Stdio 客户端参数（等价于代码中的配置）
对应 `StdioServerParameters` 的 JSON 等价示例：

```json
{
  "command": "uv",
  "args": ["run", "server", "fastmcp_quickstart", "stdio"],
  "env": {"UV_INDEX": ""}
}
```

## 自检
- `python scripts/selftest.py` 查看基础功能输出（包含因式分解示例）

## yafu 集成
- 若系统已安装 `yafu` 或 `yafu.exe` 并处于 `PATH`，`tool_factor_integer` 将自动调用以提升大整数分解效率
- 无 `yafu` 时自动回退到内置 Pollard Rho + Miller-Rabin + 试除组合

## 注意
- 大规模枚举任务已做限制；必要时请提供更多线索以缩小搜索空间
- RC4/AES 等现代密码需提供密钥等参数；AES 计划在后续版本引入
- AES/DES 工具需安装 `pycryptodome` 或 `cryptography`，否则返回空结果；请根据环境选择安装其一