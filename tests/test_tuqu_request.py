import argparse
import contextlib
import importlib.util
import io
import json
import os
import pathlib
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tuqu-photo-api" / "scripts" / "tuqu_request.py"


def build_legacy_env_name(*parts):
    return "_".join(("TUQU",) + parts)


def load_module():
    spec = importlib.util.spec_from_file_location("tuqu_request", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


class TuquRequestEnvTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_prepare_body_rejects_legacy_user_key_env_var(self):
        with mock.patch.dict(
            os.environ,
            {build_legacy_env_name("USER", "KEY"): "legacy-key"},
            clear=True,
        ):
            with self.assertRaisesRegex(ValueError, "TUQU_USER_SERVICE_KEY"):
                self.module.prepare_body("user-key", {})

    def test_prepare_body_uses_unified_env_var_for_user_key(self):
        with mock.patch.dict(
            os.environ,
            {"TUQU_USER_SERVICE_KEY": "shared-key"},
            clear=True,
        ):
            body = self.module.prepare_body("user-key", {})

        self.assertEqual(body["userKey"], "shared-key")

    def test_main_uses_unified_env_var_for_api_key_header(self):
        request_capture = {}

        def fake_urlopen(request, timeout):
            request_capture["X-api-key"] = request.get_header("X-api-key")
            return FakeResponse(json.dumps({"ok": True}).encode("utf-8"))

        args = argparse.Namespace(
            method="GET",
            path="/api/characters",
            base_url=None,
            query=[],
            json=None,
            body_file=None,
            auth_mode="auto",
            timeout=5,
        )

        with mock.patch.dict(
            os.environ,
            {"TUQU_USER_SERVICE_KEY": "shared-key"},
            clear=True,
        ):
            with mock.patch.object(self.module, "parse_args", return_value=args):
                with mock.patch.object(self.module.urllib.request, "urlopen", side_effect=fake_urlopen):
                    with contextlib.redirect_stdout(io.StringIO()):
                        exit_code = self.module.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(request_capture["X-api-key"], "shared-key")

    def test_main_rejects_legacy_api_key_env_var(self):
        request_called = False

        def fake_urlopen(request, timeout):
            nonlocal request_called
            request_called = True
            return FakeResponse(json.dumps({"ok": True}).encode("utf-8"))

        args = argparse.Namespace(
            method="GET",
            path="/api/characters",
            base_url=None,
            query=[],
            json=None,
            body_file=None,
            auth_mode="auto",
            timeout=5,
        )

        with mock.patch.dict(
            os.environ,
            {build_legacy_env_name("API", "KEY"): "legacy-key"},
            clear=True,
        ):
            with mock.patch.object(self.module, "parse_args", return_value=args):
                with mock.patch.object(self.module.urllib.request, "urlopen", side_effect=fake_urlopen):
                    with contextlib.redirect_stderr(io.StringIO()) as stderr:
                        with contextlib.redirect_stdout(io.StringIO()):
                            exit_code = self.module.main()

        self.assertEqual(exit_code, 1)
        self.assertFalse(request_called)
        self.assertIn("TUQU_USER_SERVICE_KEY", stderr.getvalue())

    def test_main_uses_unified_env_var_for_service_key_header(self):
        request_capture = {}

        def fake_urlopen(request, timeout):
            request_capture["Authorization"] = request.get_header("Authorization")
            return FakeResponse(json.dumps({"ok": True}).encode("utf-8"))

        args = argparse.Namespace(
            method="GET",
            path="/api/v1/recharge/plans",
            base_url=None,
            query=[],
            json=None,
            body_file=None,
            auth_mode="auto",
            timeout=5,
        )

        with mock.patch.dict(
            os.environ,
            {"TUQU_USER_SERVICE_KEY": "shared-key"},
            clear=True,
        ):
            with mock.patch.object(self.module, "parse_args", return_value=args):
                with mock.patch.object(self.module.urllib.request, "urlopen", side_effect=fake_urlopen):
                    with contextlib.redirect_stdout(io.StringIO()):
                        exit_code = self.module.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(request_capture["Authorization"], "Bearer shared-key")

    def test_main_rejects_legacy_service_key_env_var(self):
        request_called = False

        def fake_urlopen(request, timeout):
            nonlocal request_called
            request_called = True
            return FakeResponse(json.dumps({"ok": True}).encode("utf-8"))

        args = argparse.Namespace(
            method="GET",
            path="/api/v1/recharge/plans",
            base_url=None,
            query=[],
            json=None,
            body_file=None,
            auth_mode="auto",
            timeout=5,
        )

        with mock.patch.dict(
            os.environ,
            {build_legacy_env_name("SERVICE", "KEY"): "legacy-key"},
            clear=True,
        ):
            with mock.patch.object(self.module, "parse_args", return_value=args):
                with mock.patch.object(self.module.urllib.request, "urlopen", side_effect=fake_urlopen):
                    with contextlib.redirect_stderr(io.StringIO()) as stderr:
                        with contextlib.redirect_stdout(io.StringIO()):
                            exit_code = self.module.main()

        self.assertEqual(exit_code, 1)
        self.assertFalse(request_called)
        self.assertIn("TUQU_USER_SERVICE_KEY", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
