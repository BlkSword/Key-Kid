# Key-Kid

[![CI](https://github.com/yourusername/key-kid/workflows/CI/badge.svg)](https://github.com/yourusername/key-kid/actions)
[![codecov](https://codecov.io/gh/yourusername/key-kid/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/key-kid)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

CTF 密码学 MCP Server，提供面向 agent 的多种密码算法识别、解码与破解工具，助力快速解决比赛题目。

## 特性
- 编码识别/解码：Base64/32/16/85、Hex、URL、Unicode Escape
- 经典密码破解：Caesar/ROT、Vigenère、Affine、Rail Fence、列式置换、Playfair（支持 key 提示）
- XOR 家族：单字节与重复密钥破解
- RC4 解密：支持缺参时交互征询密钥
- **SageMath 高级工具**：离散对数、椭圆曲线、格基约化、中国剩余定理（需安装 SageMath）
- 结构化输出、可用于自动化 agent 流程
- **80%+ 测试覆盖率**
- **性能优化**：跨调用缓存、并行化枚举攻击

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

## 开发

### 环境设置
```bash
# 克隆仓库
git clone https://github.com/yourusername/key-kid.git
cd key-kid

# 安装开发依赖
pip install -e ".[dev]"

# 安装 pre-commit 钩子
pre-commit install
```

### 运行测试
```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

### 代码质量检查
```bash
# Lint
ruff check src/

# 类型检查
mypy src/ --ignore-missing-imports

# 格式化
black src/ tests/
isort src/ tests/

# 运行所有检查
pre-commit run --all-files
```

### 贡献
欢迎贡献！请查看 [CONTRTRIBUTING.md](docs/CONTRIBUTING.md) 了解详情。

## yafu 集成
- 若系统已安装 `yafu` 或 `yafu.exe` 并处于 `PATH`，`tool_factor_integer` 将自动调用以提升大整数分解效率
- 无 `yafu` 时自动回退到内置 Pollard Rho + Miller-Rabin + 试除组合

## 注意
- 大规模枚举任务已做限制；必要时请提供更多线索以缩小搜索空间
- RC4/AES 等现代密码需提供密钥等参数；AES 计划在后续版本引入
- AES/DES 工具需安装 `pycryptodome` 或 `cryptography`，否则返回空结果；请根据环境选择安装其一

## SageMath 集成

Key-Kid 包含基于 SageMath 的高级密码学工具，用于解决复杂的数论问题：

### 安装 SageMath

**Windows**: 从 https://www.sagemath.org/ 下载安装程序
**Linux**: `sudo apt-get install sagemath`
**macOS**: `brew install sage`

### 可用工具

- `tool_discrete_log(g, p, base, method)` - 离散对数求解（DLP）
- `tool_elliptic_curve_factor(n, a, b)` - 椭圆曲线因式分解（ECM）
- `tool_chinese_remainder(congruences)` - 中国剩余定理（CRT）
- `tool_linear_congruence(coefficients, remainders, moduli)` - 线性同余方程组
- `tool_elliptic_curve_point_add(curve, p, p1, p2)` - 椭圆曲线点加法
- `tool_coppersmith_attack(n, e, polynomial, beta)` - Coppersmith 方法
- `tool_quadratic_residue(a, p)` - 模平方根求解
- `tool_sagemath_check()` - 检查 SageMath 可用性

详细文档请参考 [SAGEMATH.md](docs/SAGEMATH.md)

### 使用示例

```python
# 离散对数：求解 2^x ≡ 5 (mod 101)
tool_discrete_log(g="5", p="101", base="2")
# 返回: {"found": True, "x": "10"}

# 中国剩余定理：x ≡ 2 (mod 3), x ≡ 3 (mod 5)
tool_chinese_remainder(congruences=[("2", "3"), ("3", "5")])
# 返回: {"found": True, "x": "23", "modulus": "15"}
```