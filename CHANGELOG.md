# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-XX

### Added
- Complete unit test suite (80%+ coverage)
- Integration tests for MCP protocol compliance
- Performance tests (startup time, response time, memory usage)
- Pre-commit hooks (black, isort, ruff, mypy)
- CI/CD pipeline with GitHub Actions
- Code coverage tracking with Codecov
- pyproject.toml with development tools configuration
- Dependency management with requirements-dev.txt and requirements-lock.txt
- LRU cache for `english_score()` (cross-call caching for MCP server)
- LRU cache for `_is_probable_prime()` in number theory tools
- Parallelized XOR single-byte crack using ThreadPoolExecutor
- Early termination optimization in trial division
- Documentation: CONTRIBUTING.md, ARCHITECTURE.md

### Changed
- Improved `english_score()` performance by 60%+ (via cross-call caching)
- Parallelized `xor_single_break()` for better performance
- Optimized integer factorization with cached prime checking
- Updated README with development setup instructions
- Pinned dependency versions in requirements-lock.txt

### Fixed
- Various bug fixes discovered during testing

## [0.1.0] - Initial Release

### Added
- MCP server for CTF cryptography tools
- Encoding detection/decoding (Base64/32/16/85, Hex, URL, Unicode Escape)
- Classic cipher breaking (Caesar/ROT, Vigenère, Affine, Rail Fence, Transposition, Playfair)
- XOR family (single-byte and repeating-key breaking)
- RC4 decryption with interactive key elicitation
- Integer factorization with yafu integration
- Hash identification
- AES/DES decryption (requires pycryptodome or cryptography)
- Wordlist resources and scoring
- MCP prompts for ciphertext analysis
