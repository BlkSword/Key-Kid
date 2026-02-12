# Key-Kid 架构文档

## 项目结构

```
key-kid/
├── src/
│   ├── server.py           # MCP 服务器入口
│   ├── tools/             # 密码学工具模块
│   │   ├── models.py      # 数据模型 (Pydantic)
│   │   ├── rot.py         # ROT/ Caesar 工具
│   │   ├── xor.py         # XOR 破解工具
│   │   ├── classic.py     # 经典密码 (Vigenère, Affine, etc.)
│   │   ├── decode.py      # 编码检测与解码
│   │   ├── number.py      # 数论工具 (因式分解)
│   │   ├── hash.py       # 哈希识别
│   │   ├── block.py      # 块密码 (AES, DES)
│   │   ├── rc4.py        # RC4 流密码
│   │   └── score.py      # 词表评分
│   ├── utils/             # 工具函数
│   │   └── scoring.py    # 英文评分系统 (带缓存)
│   ├── resources/         # MCP 资源
│   │   ├── samples.py    # 样本资源
│   │   └── wordlist.py  # 词表资源
│   └── prompts/          # MCP 提示模板
│       └── analyze.py    # 密码分析提示
├── tests/                # 测试套件
│   ├── conftest.py       # pytest 配置
│   ├── fixtures/         # 测试数据
│   ├── test_utils/       # 工具函数测试
│   ├── test_tools/       # 工具模块测试
│   └── test_integration/ # 集成测试
├── scripts/             # 实用脚本
│   └── selftest.py     # 自检脚本
├── docs/               # 文档
├── pyproject.toml      # 项目配置
└── requirements.txt    # 依赖清单
```

## 模块依赖关系

```
server.py (MCP 入口)
    ├── tools/
    │   ├── models.py (BreakResult, DetectionCandidate, FactorResult)
    │   ├── rot.py ─────────────────────────┐
    │   ├── xor.py ───────────────────────┐│
    │   ├── classic.py ───────────────────┐││
    │   ├── decode.py ──────────────────┐│││
    │   ├── number.py ─────────────────┐││││
    │   ├── hash.py                 ││││││
    │   ├── block.py ───────────────┐││││││
    │   ├── rc4.py ───────────────┐│││││││
    │   └── score.py ────────────┐││││││││
    └── utils/
        └── scoring.py ───────────┘││││││││
                                   ││││││││
                                   └┴┴┴┴┴┴┴┘
                            (english_score,
                             ioc, hamming)
```

## 数据流

### 1. MCP 工具调用流程
```
Claude/Agent
    │
    ├─> MCP Client
    │     │
    │     └─> server.py (FastMCP)
    │           │
    │           ├─> tools/*.py (业务逻辑)
    │           │     │
    │           │     └─> utils/scoring.py (评分)
    │           │
    │           └─> resources/*.py (MCP 资源)
    │
    └─> BreakResult/DetectionCandidate (结构化输出)
```

### 2. 评分系统流程
```
plaintext
    │
    ├─> FLAG_PATTERN 检查 ──> flag{...} ──> score = 10.0
    │
    ├─> printable_count 检查 ──> < 70% ──> score = 0.0
    │
    ├─> LETTER_FREQ 评分 ──> normalized_letter
    │
    └─> BIGRAM_FREQ 评分 ──> bigram_score
          │
          └─> total = 0.7 * letter + 0.3 * bigram
```

## 性能优化

### 跨调用缓存 (MCP 特定)
- **english_score()**: `@lru_cache(maxsize=2048)`
  - 由于 MCP 服务器是常驻进程，缓存在多次工具调用之间共享
  - 典型场景：同一密文的多个 ROT 候选评分

- **_is_probable_prime()**: `@lru_cache(maxsize=256)`
  - 因式分解时避免重复质数检查

### 并行化
- **xor_single_break()**: `ThreadPoolExecutor`
  - 256 个密钥并行尝试
  - 工作线程：`min(256, cpu_count * 4)`

### 快速启动
- 延迟导入非关键模块（如块密码库）
- 按需加载重型依赖

## MCP 协议实现

### 工具 (Tools)
所有工具通过 `@mcp.tool()` 装饰器注册：
```python
@mcp.tool()
def tool_rot_all(text: str, top_k: int = 3) -> list[BreakResult]:
    """工具描述（用于 AI 生成调用）"""
    return rot_all(text, top_k)
```

### 资源 (Resources)
- `samples://...` - 测试样本
- `wordlist://...` - 词表 (common, ctf)

### 提示 (Prompts)
- `AnalyzeCiphertext` - 密码分析工作流模板

## 扩展指南

### 添加新工具
1. 在 `src/tools/` 创建新文件
2. 实现工具函数
3. 在 `server.py` 中注册：
```python
@mcp.tool()
def tool_new_tool(param: str) -> BreakResult:
    """工具描述"""
    from src.tools.new_tool import new_tool
    return new_tool(param)
```

### 添加新评分方法
1. 在 `utils/scoring.py` 添加函数
2. 使用 `@lru_cache` 装饰器
3. 在工具中导入使用

## 安全考虑

- 所有用户输入通过 Pydantic 验证
- 外部命令调用（yafu）有超时限制
- 解码错误使用 `errors="ignore"` 处理
- 不缓存用户敏感数据

## 测试策略

- **单元测试**: 测试单个函数
- **集成测试**: 测试 MCP 协议合规性
- **性能测试**: 测试响应时间、内存占用、并发
- **覆盖率目标**: ≥80%
