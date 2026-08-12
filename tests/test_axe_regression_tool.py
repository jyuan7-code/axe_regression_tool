import json
import sys
import tempfile
import unittest
from pathlib import Path

from axe_regression_tool import main


class AxeRegressionToolTests(unittest.TestCase):
    def test_writes_and_reuses_baselines_for_gsf_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tests_dir = root / "tests"
            baselines_dir = root / "baselines"
            report_path = root / "report.json"
            nested_test = tests_dir / "render" / "triangle.gsf"
            nested_test.parent.mkdir(parents=True)
            nested_test.write_text("triangle\n", encoding="utf-8")

            runner = (
                f'{sys.executable} -c "from pathlib import Path; import sys; '
                'sys.stdout.write(Path(sys.argv[1]).read_text().upper())" {gsf}'
            )

            exit_code = main(
                [
                    "--test-root",
                    str(tests_dir),
                    "--baseline-dir",
                    str(baselines_dir),
                    "--runner",
                    runner,
                    "--report-json",
                    str(report_path),
                    "--write-baseline",
                ]
            )

            self.assertEqual(exit_code, 0)
            baseline_path = baselines_dir / "render" / "triangle.json"
            self.assertTrue(baseline_path.exists())
            payload = json.loads(baseline_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["stdout"], "TRIANGLE\n")

            exit_code = main(
                [
                    "--test-root",
                    str(tests_dir),
                    "--baseline-dir",
                    str(baselines_dir),
                    "--runner",
                    runner,
                    "--report-json",
                    str(report_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report[0]["status"], "pass")

    def test_reports_regressions_when_output_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tests_dir = root / "tests"
            baselines_dir = root / "baselines"
            report_path = root / "report.json"
            test_file = tests_dir / "scene.gsf"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("baseline\n", encoding="utf-8")

            stable_runner = (
                f'{sys.executable} -c "from pathlib import Path; import sys; '
                'sys.stdout.write(Path(sys.argv[1]).read_text())" {gsf}'
            )
            regression_runner = (
                f'{sys.executable} -c "from pathlib import Path; import sys; '
                'sys.stdout.write(Path(sys.argv[1]).read_text().replace(\'baseline\', \'changed\'))" {gsf}'
            )

            self.assertEqual(
                main(
                    [
                        "--test-root",
                        str(tests_dir),
                        "--baseline-dir",
                        str(baselines_dir),
                        "--runner",
                        stable_runner,
                        "--write-baseline",
                    ]
                ),
                0,
            )

            exit_code = main(
                [
                    "--test-root",
                    str(tests_dir),
                    "--baseline-dir",
                    str(baselines_dir),
                    "--runner",
                    regression_runner,
                    "--report-json",
                    str(report_path),
                ]
            )

            self.assertEqual(exit_code, 1)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report[0]["status"], "regression")
            self.assertEqual(report[0]["differences"], ["stdout"])


if __name__ == "__main__":
    unittest.main()
