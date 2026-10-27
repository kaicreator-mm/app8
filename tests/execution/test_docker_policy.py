"""Pure policy tests: NO Docker subprocess or OS containment PASS is implied."""
from dataclasses import replace
import unittest

from app8.execution.docker_policy import ContainerRequest, SandboxPolicyError, prepare_docker_sandbox

IMAGE = "registry.example/allowed-runtime@sha256:" + "a" * 64
CLI = "b" * 64


def base():
    return ContainerRequest(IMAGE, "/usr/bin/ffmpeg", ("-version",), CLI)


class DockerPolicyTests(unittest.TestCase):
    def test_fixed_restrictive_options(self):
        planned = prepare_docker_sandbox(base())
        self.assertEqual(planned.status, "NOT_RUN")
        self.assertFalse(planned.host_isolation_verified)
        self.assertEqual(planned.image_sha256, "a" * 64)
        for expected in ("--pull=never", "--network=none", "--read-only", "--cap-drop=ALL",
                         "--security-opt=no-new-privileges=true", "--ipc=none", "--no-healthcheck"):
            self.assertIn(expected, planned.argv)
        self.assertNotIn("--privileged", planned.argv)
        self.assertFalse(any(x.startswith("--volume") or x == "--mount" for x in planned.argv))
        self.assertEqual(planned.argv[-3:], (IMAGE, "/usr/bin/ffmpeg", "-version"))

    def test_full_local_image_id_accepted_without_registry(self):
        local = "sha256:" + "a" * 64
        planned = prepare_docker_sandbox(replace(base(), image_ref=local))
        self.assertEqual(planned.image_sha256, "a" * 64)
        self.assertEqual(planned.argv[-3:], (local, "/usr/bin/ffmpeg", "-version"))
        self.assertIn("--pull=never", planned.argv)
        self.assertIn("--network=none", planned.argv)
        self.assertFalse(planned.host_isolation_verified)

    def test_local_image_id_must_be_full_lowercase_digest(self):
        for image in ("sha256:abc", "sha256:" + "A" * 64,
                      "sha256:" + "a" * 63, "sha256:" + "a" * 65,
                      "local:latest", "sha256:../../etc/passwd"):
            with self.subTest(image=image), self.assertRaises(SandboxPolicyError):
                prepare_docker_sandbox(replace(base(), image_ref=image))

    def test_tag_only_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), image_ref="registry.example/runtime:latest"))

    def test_registry_without_path_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), image_ref="runtime@sha256:" + "a" * 64))

    def test_uppercase_digest_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), image_ref=IMAGE.upper()))

    def test_docker_cli_identity_required(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), docker_cli_sha256=""))

    def test_shell_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), command="/bin/sh"))

    def test_relative_command_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), command="ffmpeg"))

    def test_dotdot_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), command="/usr/../bin/sh"))

    def test_no_newline_command(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), command="/bin/ffmpeg\n--privileged"))

    def test_arg_docker_flag_never_becomes_runtime_flag(self):
        planned = prepare_docker_sandbox(replace(base(), args=("--privileged", "--mount", "x")))
        index = planned.argv.index(IMAGE)
        self.assertLess(planned.argv.index("--network=none"), index)
        self.assertEqual(planned.argv[index + 2:], ("--privileged", "--mount", "x"))

    def test_bool_budget_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), wall_seconds=True))

    def test_excess_memory_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), memory_mib=4096))

    def test_excess_output_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), max_output_bytes=2_000_000))

    def test_excess_processes_rejected(self):
        with self.assertRaises(SandboxPolicyError):
            prepare_docker_sandbox(replace(base(), pids_limit=1000))

    def test_input_never_executes(self):
        planned = prepare_docker_sandbox(base())
        self.assertEqual(planned.status, "NOT_RUN")
        self.assertEqual(planned.wall_seconds_runner_must_enforce, 30)
        self.assertEqual(planned.max_output_bytes_runner_must_enforce, 65536)

    def test_hash_changes_with_args(self):
        a = prepare_docker_sandbox(base())
        b = prepare_docker_sandbox(replace(base(), args=("-codecs",)))
        self.assertNotEqual(a.request_sha256, b.request_sha256)


if __name__ == "__main__":
    unittest.main()
