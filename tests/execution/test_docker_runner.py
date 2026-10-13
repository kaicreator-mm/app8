"""Runner mechanics tests against a fake Docker client; no real daemon here.

The fake client is a real subprocess invoked through the same argv-head
contract as production (loader + reviewed artifact). It emulates
info/ps/rm/run so wall/output/cleanup enforcement is exercised for real.
Real-daemon qualification lives in scripts/qualify_real_runner.py only.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from app8.execution.docker_policy import ContainerRequest
from app8.execution.docker_runner import (
    RealDockerRunner,
    RunnerBlocked,
    RunnerConfig,
    RunnerKeyError,
    RunnerObservation,
    freeze_execution_plan,
    load_signing_key,
    policy_source_sha256,
)

IMAGE = "library/fake@sha256:" + "c" * 64
IMAGE_DIGEST = "c" * 64
POLICY = "a" * 64
KEY = b"runner-test-key-32-bytes-minimum-000"

FAKE_DOCKER = r'''
import os, sys, time

def _ids():
    f = os.environ.get("FAKE_DOCKER_PS", "")
    if f and os.path.exists(f):
        return [x for x in open(f, encoding="utf-8").read().splitlines() if x.strip()]
    return []

def _write(ids):
    f = os.environ.get("FAKE_DOCKER_PS", "")
    if f:
        with open(f, "w", encoding="utf-8", newline="\n") as out:
            out.write("\n".join(ids) + ("\n" if ids else ""))

argv = sys.argv[1:]
if argv[:1] == ["info"]:
    fmt = argv[argv.index("--format") + 1]
    sys.stdout.write(fmt.replace("{{.OSType}}", os.environ.get("FAKE_OSTYPE", "linux"))
                        .replace("{{.ServerVersion}}", os.environ.get("FAKE_SERVER", "29.0.0-test")) + "\n")
elif argv[:1] == ["ps"]:
    for cid in _ids():
        sys.stdout.write(cid + "\n")
elif argv[:1] == ["rm"]:
    ids = _ids()
    rc = 0
    for target in argv[1:]:
        if target == "-f":
            continue
        if target in ids:
            ids.remove(target)
            sys.stdout.write(target + "\n")
        else:
            sys.stderr.write("Error: No such container: " + target + "\n")
            rc = 1
    _write(ids)
    sys.exit(rc)
elif argv[:1] == ["run"]:
    cid = "fakecid0001"
    ids = _ids(); ids.append(cid); _write(ids)
    try:
        mode = os.environ.get("FAKE_RUN_MODE", "ok")
        if mode == "ok":
            sys.stdout.buffer.write(b"app8-ok\n"); sys.exit(0)
        if mode == "exit3":
            sys.stderr.buffer.write(b"boom\n"); sys.exit(3)
        if mode == "sleep":
            time.sleep(float(os.environ.get("FAKE_SLEEP_SECONDS", "120")))
        if mode == "flood":
            sys.stdout.buffer.write(b"A" * 1048576); sys.stdout.buffer.flush()
        if mode == "stderrflood":
            sys.stderr.buffer.write(b"E" * 1048576); sys.stderr.buffer.flush()
    finally:
        ids = _ids()
        if cid in ids:
            ids.remove(cid); _write(ids)
'''


class RunnerCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.fake = root / "fake_docker.py"
        self.fake.write_text(FAKE_DOCKER, encoding="utf-8", newline="\n")
        self.cli_sha = hashlib.sha256(self.fake.read_bytes()).hexdigest()
        self.ps_file = root / "containers.txt"
        self.ps_file.write_text("", encoding="utf-8")
        self.env = {"FAKE_DOCKER_PS": str(self.ps_file)}

    def config(self, **over):
        args = dict(runner_id="test-runner", policy_sha256=POLICY,
                    client_argv_head=(sys.executable, str(self.fake)),
                    environment_id="test-env",
                    allowlist=frozenset({(IMAGE, "/usr/local/bin/python")}),
                    kill_grace_seconds=0.3)
        args.update(over)
        return RunnerConfig(**args)

    def runner(self, **over):
        return RealDockerRunner(self.config(**over), signing_key=KEY)

    def req(self, command="/usr/local/bin/python", args=(), wall=10, cap=65536):
        return ContainerRequest(IMAGE, command, args, self.cli_sha, wall, cap)

    def ps_ids(self):
        return [x for x in self.ps_file.read_text().splitlines() if x.strip()]


class ConfigTests(RunnerCase):
    def test_relative_client_head_rejected(self):
        with self.assertRaises(RunnerBlocked):
            self.config(client_argv_head=("docker",))

    def test_policy_must_be_frozen_digest(self):
        with self.assertRaises(RunnerBlocked):
            self.config(policy_sha256="latest")

    def test_short_signing_key_rejected(self):
        with self.assertRaises(RunnerBlocked):
            RealDockerRunner(self.config(), signing_key=b"short")

    def test_allowlist_requires_absolute_commands(self):
        with self.assertRaises(RunnerBlocked):
            self.config(allowlist=frozenset({(IMAGE, "python")}))

    def test_policy_source_hash_is_real_digest(self):
        self.assertRegex(policy_source_sha256(), r"[0-9a-f]{64}\Z")


class KeyProvisioningTests(RunnerCase):
    def test_missing_key_path(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RunnerKeyError):
                load_signing_key()

    def test_short_key_rejected(self):
        path = Path(self.tmp.name) / "k.bin"
        path.write_bytes(b"too-short")
        with self.assertRaises(RunnerKeyError):
            load_signing_key(path)

    def test_hex_key_decoded(self):
        path = Path(self.tmp.name) / "k.hex"
        path.write_text("ab" * 32, encoding="utf-8")
        self.assertEqual(load_signing_key(path), bytes.fromhex("ab" * 32))

    def test_repo_internal_key_refused(self):
        path = Path(self.tmp.name) / "inner" / "k.bin"
        path.parent.mkdir()
        path.write_bytes(b"x" * 32)
        with mock.patch("app8.execution.docker_runner._REPO_ROOT", Path(self.tmp.name)):
            with self.assertRaises(RunnerKeyError):
                load_signing_key(path)


class ExecutionTests(RunnerCase):
    def test_normal_execution_real_hashes(self):
        with mock.patch.dict(os.environ, {**self.env, "FAKE_RUN_MODE": "ok"}):
            obs = self.runner().execute(self.req())
        self.assertEqual(obs.status, "EXECUTED")
        self.assertEqual(obs.exit_code, 0)
        self.assertEqual(obs.stdout, b"app8-ok\n")
        self.assertEqual(hashlib.sha256(obs.stdout).hexdigest(),
                         hashlib.sha256(b"app8-ok\n").hexdigest())
        self.assertTrue(obs.containers_reaped_verified)
        self.assertEqual(self.ps_ids(), [])
        self.assertEqual(obs.daemon_server_version, "29.0.0-test")

    def test_exit_code_propagated(self):
        with mock.patch.dict(os.environ, {**self.env, "FAKE_RUN_MODE": "exit3"}):
            obs = self.runner().execute(self.req())
        self.assertEqual(obs.exit_code, 3)
        self.assertEqual(obs.stderr, b"boom\n")

    def test_client_sha256_mismatch_blocks_before_spawn(self):
        with self.assertRaises(RunnerBlocked):
            self.runner().execute(ContainerRequest(IMAGE, "/usr/local/bin/python", (),
                                                   "0" * 64, 10, 65536))
        self.assertEqual(self.ps_ids(), [])

    def test_non_linux_daemon_blocked(self):
        env = {**self.env, "FAKE_OSTYPE": "windows"}
        with mock.patch.dict(os.environ, env):
            with self.assertRaises(RunnerBlocked):
                self.runner().execute(self.req())
        self.assertEqual(self.ps_ids(), [])

    def test_daemon_version_pin(self):
        env = {**self.env, "FAKE_RUN_MODE": "ok", "FAKE_SERVER": "29.7.2"}
        with mock.patch.dict(os.environ, env):
            with self.assertRaises(RunnerBlocked):
                self.runner(expected_server_version="29.1.3").execute(self.req())
            obs = self.runner(expected_server_version="29.7.2").execute(self.req())
        self.assertEqual(obs.daemon_server_version, "29.7.2")

    def test_unallowlisted_command_never_runs(self):
        with mock.patch.dict(os.environ, self.env):
            with self.assertRaises(RunnerBlocked):
                self.runner().execute(self.req(command="/bin/ls"))
        self.assertEqual(self.ps_ids(), [])

    def test_unallowlisted_image_never_runs(self):
        other = "library/other@sha256:" + "d" * 64
        with mock.patch.dict(os.environ, self.env):
            with self.assertRaises(RunnerBlocked):
                self.runner().execute(ContainerRequest(other, "/usr/local/bin/python", (),
                                                       self.cli_sha, 10, 65536))

    def test_shell_still_rejected_by_policy(self):
        with self.assertRaises(RunnerBlocked):
            self.runner().execute(self.req(command="/bin/sh"))

    def test_preexisting_container_ambiguity_blocks(self):
        self.ps_file.write_text("deadbeefcafe\n", encoding="utf-8")
        with mock.patch.dict(os.environ, self.env):
            with self.assertRaises(RunnerBlocked):
                self.runner().execute(self.req())
        self.assertEqual(self.ps_ids(), ["deadbeefcafe"])  # never reap unknowns

    def test_wall_limit_enforced_and_container_reaped(self):
        env = {**self.env, "FAKE_RUN_MODE": "sleep", "FAKE_SLEEP_SECONDS": "120"}
        with mock.patch.dict(os.environ, env):
            obs = self.runner().execute(self.req(wall=1))
        self.assertEqual(obs.status, "WALL_LIMIT_ENFORCED")
        self.assertIsInstance(obs.exit_code, int)
        self.assertLess(obs.wall_ms, 20000)
        self.assertTrue(obs.containers_reaped_verified)
        self.assertEqual(self.ps_ids(), [])

    def test_output_limit_enforced_streaming(self):
        env = {**self.env, "FAKE_RUN_MODE": "flood"}
        with mock.patch.dict(os.environ, env):
            obs = self.runner().execute(self.req(cap=65536))
        self.assertEqual(obs.status, "OUTPUT_LIMIT_ENFORCED")
        self.assertTrue(obs.stdout_truncated)
        self.assertEqual(len(obs.stdout), 65536)
        self.assertEqual(self.ps_ids(), [])

    def test_stderr_stream_capped(self):
        env = {**self.env, "FAKE_RUN_MODE": "stderrflood"}
        with mock.patch.dict(os.environ, env):
            obs = self.runner().execute(self.req(cap=65536))
        self.assertTrue(obs.stderr_truncated)
        self.assertLessEqual(len(obs.stderr), 65536)


class AdjudicationTests(unittest.TestCase):
    def obs(self, stdout=b"app8-ok\n", stderr=b"", code=0):
        return RunnerObservation("EXECUTED", code, stdout, stderr, False, False, 12,
                                 "a" * 64, "c" * 64, "b" * 64, "29.0.0-test", True)

    def test_all_assertion_forms(self):
        out_sha = hashlib.sha256(b"app8-ok\n").hexdigest()
        err_sha = hashlib.sha256(b"").hexdigest()
        verdict, codes = RealDockerRunner.adjudicate(
            ["exit_code==0", f"stdout_sha256=={out_sha}", f"stderr_sha256=={err_sha}",
             "stdout_contains:app8-ok"], self.obs())
        self.assertEqual(verdict, "SUPPORTED")
        self.assertIn("ASSERTIONS_PASSED", codes)

    def test_failed_assertion_refutes(self):
        verdict, codes = RealDockerRunner.adjudicate(["exit_code==0"], self.obs(code=3))
        self.assertEqual(verdict, "REFUTED")
        self.assertIn("ASSERTIONS_FAILED", codes)
        self.assertIn("FAILED:exit_code==0", codes)

    def test_unknown_form_blocked(self):
        with self.assertRaises(RunnerBlocked):
            RealDockerRunner.adjudicate(["please_trust_me"], self.obs())

    def test_enforcement_codes_recorded(self):
        obs = RunnerObservation("WALL_LIMIT_ENFORCED", 137, b"", b"", False, False, 12,
                                "a" * 64, "c" * 64, "b" * 64, "29.0.0-test", True)
        verdict, codes = RealDockerRunner.adjudicate(["exit_code==137"], obs)
        self.assertEqual(verdict, "SUPPORTED")
        self.assertIn("WALL_LIMIT_ENFORCED", codes)

    def test_freeze_plan_binds_budget(self):
        req = ContainerRequest(IMAGE, "/usr/local/bin/python", (), "b" * 64, 30, 65536)
        plan = freeze_execution_plan("binding:x", ["exit_code==0"], req)
        self.assertRegex(plan["plan_sha256"], r"[0-9a-f]{64}\Z")
        self.assertEqual(plan["budget"],
                         {"wall_seconds": 30, "max_output_bytes": 65536,
                          "network_allowed": False, "mutation_allowed": False})


if __name__ == "__main__":
    unittest.main()
