"""Performance demonstration - cache effectiveness."""
import os
import sys
import time

sys.path.insert(0, os.path.abspath("."))

from src.utils.scoring import english_score


def demo_cache_effectiveness():
    """演示 english_score 缓存的效果"""
    print("=== 缓存性能演示 ===\n")

    # 清空缓存
    english_score.cache_clear()

    # 测试文本
    test_texts = [
        "Hello World",
        "The quick brown fox jumps over the lazy dog",
        "flag{test_flag_here}",
        "Uryyb Jbeyq",  # ROT13
        "Lxfopvefrnhr",  # Vigenère
    ] * 100  # 重复 100 次模拟多轮破解

    # 第一次运行（缓存未命中）
    print("第一次运行（冷启动）:")
    start = time.time()
    for text in test_texts:
        english_score(text)
    cold_time = time.time() - start
    print(f"  时间: {cold_time:.3f} 秒")

    cache_info = english_score.cache_info()
    print(f"  缓存信息: {cache_info}")
    print()

    # 第二次运行（缓存命中）
    print("第二次运行（热启动）:")
    start = time.time()
    for text in test_texts:
        english_score(text)
    hot_time = time.time() - start
    print(f"  时间: {hot_time:.3f} 秒")

    cache_info = english_score.cache_info()
    print(f"  缓存信息: {cache_info}")
    print()

    # 计算加速比
    speedup = cold_time / hot_time
    print(f"加速比: {speedup:.1f}x")
    print(f"缓存命中率: {cache_info.hits / (cache_info.hits + cache_info.misses) * 100:.1f}%")
    print()


def demo_flag_detection():
    """演示 flag 模式检测"""
    print("=== Flag 模式检测演示 ===\n")

    test_cases = [
        ("普通英文", "Hello World"),
        ("Flag 模式", "flag{test_flag}"),
        ("CTF 模式", "ctf{some_flag}"),
        ("Key 模式", "key{secret_key}"),
        ("Secret 模式", "secret{my_secret}"),
        ("无 Flag", "just some random text"),
    ]

    print("评分结果:")
    for name, text in test_cases:
        score = english_score(text)
        print(f"  {name:15}: {score:5.2f} - {text}")


def main():
    demo_cache_effectiveness()
    demo_flag_detection()


if __name__ == "__main__":
    main()
