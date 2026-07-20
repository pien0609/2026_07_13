"""checker.py 核心模組基本測試。"""

import sys
from pathlib import Path

# 確保能 import 同層的 checker
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checker import validate_timeout, validate_url


# ── validate_url ─────────────────────────────────────────────


class TestValidateUrl:
    def test_empty(self):
        assert validate_url("") == "請輸入網址"

    def test_none_like(self):
        assert validate_url("   ") == "請輸入網址"

    def test_no_scheme(self):
        assert validate_url("example.com") is not None

    def test_ftp_scheme(self):
        assert "http" in (validate_url("ftp://example.com") or "")

    def test_valid_https(self):
        assert validate_url("https://example.com") is None

    def test_valid_http(self):
        assert validate_url("http://example.com") is None

    def test_valid_with_path(self):
        assert validate_url("https://example.com/path?q=1") is None

    def test_missing_netloc(self):
        assert validate_url("https://") is not None


# ── validate_timeout ─────────────────────────────────────────


class TestValidateTimeout:
    def test_valid(self):
        val, err = validate_timeout("30")
        assert val == 30
        assert err is None

    def test_not_a_number(self):
        val, err = validate_timeout("abc")
        assert val is None
        assert "整數" in err

    def test_zero(self):
        val, err = validate_timeout("0")
        assert val is None
        assert "小於" in err

    def test_negative(self):
        val, err = validate_timeout("-5")
        assert val is None

    def test_too_large(self):
        val, err = validate_timeout("999")
        assert val is None
        assert "超過" in err

    def test_boundary_ok(self):
        val, err = validate_timeout("1")
        assert val == 1
        assert err is None

    def test_boundary_max(self):
        val, err = validate_timeout("300")
        assert val == 300
        assert err is None
