# Contributing to Key-Kid

感谢你对 Key-Kid 项目的关注！我们欢迎任何形式的贡献。

## 开发环境设置

### 前置要求
- Python 3.12+
- Git

### 安装步骤

1. Fork 并克隆仓库：
```bash
git clone https://github.com/yourusername/key-kid.git
cd key-kid
```

2. 安装开发依赖：
```bash
pip install -e ".[dev]"
```

3. 安装 pre-commit 钩子：
```bash
pre-commit install
```

## 代码风格指南

### Python 代码规范
- 遵循 PEP 8
- 使用 `black` 进行代码格式化（line-length: 100）
- 使用 `isort` 对导入进行排序
- 使用 `ruff` 进行 linting
- 使用 `mypy` 进行类型检查（逐步添加类型注解）

### 命名约定
- 函数和变量：`snake_case`
- 类：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- 私有函数：`_leading_underscore`

### 文档字符串
所有公共函数和类应有文档字符串：
```python
def function_name(param1: str, param2: int) -> str:
    """简短描述。

    详细说明（可选）。

    Args:
        param1: 参数1的说明
        param2: 参数2的说明

    Returns:
        返回值的说明
    """
    pass
```

## Pull Request 流程

1. 创建新分支：
```bash
git checkout -b feature/your-feature-name
```

2. 进行更改并提交：
```bash
git add .
git commit -m "feat: 添加某功能"
```

3. 推送到你的 fork：
```bash
git push origin feature/your-feature-name
```

4. 在 GitHub 上创建 Pull Request

### Commit 消息格式
使用 Conventional Commits 格式：
- `feat:` 新功能
- `fix:` Bug 修复
- `refactor:` 代码重构
- `docs:` 文档更新
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加 RSA 模数分解工具
fix: 修复 Vigenère 破解的边界情况
docs: 更新 README 安装说明
```

## 测试指南

### 编写测试
- 测试文件放在 `tests/` 目录下
- 使用 `pytest` 框架
- 测试覆盖率目标：≥80%

```python
# tests/test_tools/test_rot.py
def test_rot_all_basic():
    """Test basic ROT decryption."""
    results = rot_all("Uryyb Jbeyq", top_k=1)
    assert len(results) == 1
    assert "hello" in results[0].plaintext.lower()
```

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_tools/test_rot.py

# 显示详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 性能考虑

### 缓存策略
- 使用 `@lru_cache` 装饰器缓存频繁调用的函数
- `english_score()` 使用跨调用缓存（MCP 服务器常驻特性）
- `_is_probable_prime()` 使用 LRU 缓存

### 并行化
- 单字节 XOR 破解使用 `ThreadPoolExecutor` 并行化
- 最大工作线程数：`min(256, cpu_count * 4)`

## 报告 Bug

请通过 [GitHub Issues](https://github.com/yourusername/key-kid/issues) 报告 bug，包含：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息（OS、Python 版本）

## 许可

通过贡献代码，你同意你的贡献将使用与项目相同的许可证发布。
