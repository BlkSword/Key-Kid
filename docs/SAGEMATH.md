# SageMath Tools for Key-Kid

## Overview

Key-Kid includes advanced cryptography tools powered by [SageMath](https://www.sagemath.org/), a free open-source mathematics software system based on Python. These tools handle complex number theory problems common in CTF cryptography challenges.

## Installing SageMath

### Windows

1. Download the installer from https://www.sagemath.org/download.html
2. Run the installer (requires ~5GB disk space)
3. Add SageMath to your PATH:
   - Default location: `C:\Program Files\SageMath 9.x\rosa\bin`
   - Add to System Environment Variables

Verify installation:
```bash
sage --version
```

### Linux (Debian/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install sagemath
```

### macOS

```bash
brew install sage
```

Or download the .dmg installer from the website.

## Available Tools

### 1. Discrete Logarithm (`tool_discrete_log`)

Solves the discrete logarithm problem: find x where `base^x ≡ g (mod p)`.

**Use cases:**
- Diffie-Hellman cryptanalysis
- ElGamal decryption
- DLP-based CTF challenges

**Example:**
```python
# Solve: 2^x ≡ 5 (mod 101)
tool_discrete_log(g="5", p="101", base="2")
# Returns: {"found": true, "x": "10"}
```

**Methods:**
- `auto`: SageMath chooses best algorithm
- `bsgs`: Baby-step giant-step (medium problems)
- `ph`: Pohlig-Hellman (smooth order)
- `rho`: Pollard's rho (large problems)

### 2. Elliptic Curve Factorization (`tool_elliptic_curve_factor`)

Factors integers using Lenstra's Elliptic Curve Method (ECM).

**Use cases:**
- Finding medium-sized factors (20-60 digits)
- RSA modulus factorization
- Numbers where Pollard's rho is too slow

**Example:**
```python
# Find factor of n using ECM
tool_elliptic_curve_factor(n="1234567890123456789")
# Returns: {"found": true, "factor": "1234567", "remaining": "999999..."}
```

### 3. Chinese Remainder Theorem (`tool_chinese_remainder`)

Solves systems of simultaneous linear congruences.

**Use cases:**
- RSA broadcast attacks
- Side-channel cryptanalysis
- Reconstructing secrets from shares

**Example:**
```python
# Solve: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)
tool_chinese_remainder(congruences=[("2", "3"), ("3", "5"), ("2", "7")])
# Returns: {"found": true, "x": "23", "modulus": "105"}
```

### 4. Linear Congruence Systems (`tool_linear_congruence`)

Solves equations of the form `a*x ≡ b (mod n)`.

**Use cases:**
- Affine cipher analysis
- Modular inverse finding
- Linear equation solving over finite fields

**Example:**
```python
# Solve: 3*x ≡ 2 (mod 7)
tool_linear_congruence(coefficients=["3"], remainders=["2"], moduli=["7"])
# Returns: {"found": true, "x": "3", "modulus": "7"}
```

### 5. Elliptic Curve Point Addition (`tool_elliptic_curve_point_add`)

Performs point addition on elliptic curves over prime fields.

**Use cases:**
- ECC cryptanalysis
- ECDH parameter recovery
- ECDSA challenges

**Example:**
```python
# Add points on y² = x³ + 2x + 2 (mod 17)
tool_elliptic_curve_point_add(
    curve_params=("2", "2", "17"),
    p1=("5", "1"),
    p2=("5", "1")
)
# Returns: {"found": true, "x": "...", "y": "..."}
```

### 6. Coppersmith's Method (`tool_coppersmith_attack`)

Finds small roots of modular polynomials.

**Use cases:**
- RSA low-exponent attacks
- Boneh-Durfee
- Broadcast attacks
- Coppersmith's short pad attacks

**Example:**
```python
# Find small roots of polynomial modulo n
tool_coppersmith_attack(
    n="15",
    e="3",
    polynomial="x^3 + 4*x^2 + x",
    beta=0.5
)
```

### 7. Quadratic Residues (`tool_quadratic_residue`)

Finds square roots modulo prime: `x² ≡ a (mod p)`.

**Use cases:**
- Rabin cryptosystem decryption
- Quadratic residue problems
- Legendre symbol computation

**Example:**
```python
# Find x where x² ≡ 4 (mod 7)
tool_quadratic_residue(a="4", p="7")
# Returns: {"found": true, "roots": ["2", "5"]}
```

## Usage in Key-Kid MCP Server

### Via Claude Desktop

Once SageMath is installed, the tools are automatically available in MCP sessions:

```
User: Solve 2^x ≡ 14 (mod 101)
Assistant: [calls tool_discrete_log]
         Found: x = 10
```

### Checking Availability

```bash
# Verify SageMath is available
python -c "from src.tools.sagemath import HAS_SAGEMATH; print(HAS_SAGEMATH)"

# Via MCP tool
tool_sagemath_check()
```

## Performance Considerations

### Discrete Logarithms

- **Small (p < 2^20)**: Baby-step giant-step, < 1 second
- **Medium (p < 2^40)**: Pollard's rho, < 30 seconds
- **Large (p > 2^40)**: May take minutes or hours
- **Special cases**: Pohlig-Hellman when p-1 has small factors

### Elliptic Curve Factorization

- **Small factors (< 20 digits)**: Very fast, < 1 second
- **Medium factors (20-40 digits)**: ECM effective, < 2 minutes
- **Large factors (> 40 digits)**: May require multiple attempts or different methods

### Timeouts

All tools support a `timeout` parameter (default 30-120 seconds). Adjust based on your problem size:

```python
# Allow more time for hard problems
tool_discrete_log(g="5", p="0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E08", timeout=300)
```

## Troubleshooting

### SageMath Not Found

**Error:** "SageMath not installed"

**Solution:**
1. Verify installation: `sage --version`
2. Add to PATH if not found
3. Restart your MCP server/IDE

### Timeout Issues

**Problem:** SageMath takes too long

**Solutions:**
1. Increase `timeout` parameter
2. Try different `method` (e.g., "bsgs" vs "auto")
3. Check if problem size is reasonable for your hardware

### Memory Issues

**Problem:** SageMath runs out of memory

**Solutions:**
1. Reduce problem size (if applicable)
2. Use more targeted methods instead of generic algorithms
3. Increase system swap or use machine with more RAM

## Integration with Other Tools

SageMath tools complement existing Key-Kid functionality:

- **RSA**: Use `tool_factor_integer` first, then `tool_elliptic_curve_factor` for hard composites
- **DLP**: `tool_discrete_log` for DH/ElGamal, unlike `tool_xor` for XOR problems
- **Side-channel**: Combine `tool_chinese_remainder` with timing analysis results

## Example CTF Workflow

```python
# Challenge: Decrypt ECC message
# Given: Curve y² = x³ + 7 (mod 1009), point P = (..., ...)
# Goal: Find private key k such that Q = k*P

# Step 1: Check SageMath availability
tool_sagemath_check()

# Step 2: If we know approximate range, use discrete log approach
# (Implementation depends on specific challenge)

# Step 3: Use point operations to verify
tool_elliptic_curve_point_add(curve_params=("0", "7", "1009"), ...)
```

## Further Reading

- [SageMath Documentation](https://doc.sagemath.org/)
- [Handbook of Applied Cryptography](https://www.schneier.com/blog/archives/2005/03/cryptography.html)
- [CTF Crypto Wiki](https://ctf-wiki.org/crypto)

## Contributing

To add new SageMath tools:

1. Implement function in `src/tools/sagemath.py`
2. Add MCP wrapper in `src/server.py`
3. Write tests in `tests/test_tools/test_sagemath.py`
4. Update this documentation

Ensure graceful degradation when SageMath is not installed.
