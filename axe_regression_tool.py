from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass
class Baseline:
    returncode: int
    stdout: str
    stderr: str


@dataclass
class TestResult:
    name: str
    gsf: str
    baseline: str
    status: str
    returncode: int
    differences: list[str]


def normalize_output(value: str) -> str:
    return value.replace("\r\n", "\n")


def discover_gsf_files(test_root: Path) -> list[Path]:
    return sorted(path for path in test_root.rglob("*.gsf") if path.is_file())


def baseline_path_for(gsf_path: Path, test_root: Path, baseline_dir: Path) -> Path:
    return baseline_dir / gsf_path.relative_to(test_root).with_suffix(".json")


def build_command(command_template: str, gsf_path: Path) -> list[str]:
    return [part.replace("{gsf}", str(gsf_path)) for part in shlex.split(command_template)]


def run_test(command_template: str, gsf_path: Path, cwd: Path | None = None) -> Baseline:
    completed = subprocess.run(
        build_command(command_template, gsf_path),
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return Baseline(
        returncode=completed.returncode,
        stdout=normalize_output(completed.stdout),
        stderr=normalize_output(completed.stderr),
    )


def save_baseline(path: Path, baseline: Baseline) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(baseline), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_baseline(path: Path) -> Baseline:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return Baseline(**payload)


def compare_baseline(expected: Baseline, actual: Baseline) -> list[str]:
    differences: list[str] = []
    if expected.returncode != actual.returncode:
        differences.append("returncode")
    if expected.stdout != actual.stdout:
        differences.append("stdout")
    if expected.stderr != actual.stderr:
        differences.append("stderr")
    return differences


def process_tests(
    test_root: Path,
    baseline_dir: Path,
    command_template: str,
    write_baseline: bool,
    cwd: Path | None = None,
) -> tuple[list[TestResult], int]:
    results: list[TestResult] = []
    gsf_files = discover_gsf_files(test_root)
    if not gsf_files:
        return results, 2

    has_failures = False
    for gsf_path in gsf_files:
        baseline_path = baseline_path_for(gsf_path, test_root, baseline_dir)
        actual = run_test(command_template, gsf_path, cwd=cwd)

        if write_baseline:
            save_baseline(baseline_path, actual)
            results.append(
                TestResult(
                    name=str(gsf_path.relative_to(test_root)),
                    gsf=str(gsf_path),
                    baseline=str(baseline_path),
                    status="baseline-updated",
                    returncode=actual.returncode,
                    differences=[],
                )
            )
            continue

        if not baseline_path.exists():
            has_failures = True
            results.append(
                TestResult(
                    name=str(gsf_path.relative_to(test_root)),
                    gsf=str(gsf_path),
                    baseline=str(baseline_path),
                    status="missing-baseline",
                    returncode=actual.returncode,
                    differences=["baseline"],
                )
            )
            continue

        differences = compare_baseline(load_baseline(baseline_path), actual)
        status = "pass" if not differences else "regression"
        if differences:
            has_failures = True
        results.append(
            TestResult(
                name=str(gsf_path.relative_to(test_root)),
                gsf=str(gsf_path),
                baseline=str(baseline_path),
                status=status,
                returncode=actual.returncode,
                differences=differences,
            )
        )

    return results, 1 if has_failures else 0


def write_report(results: Iterable[TestResult], report_path: Path | None) -> None:
    if not report_path:
        return
    payload = [asdict(result) for result in results]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Regression tool for fulsim GSF tests.")
    parser.add_argument("--test-root", required=True, help="Directory that contains .gsf tests.")
    parser.add_argument("--baseline-dir", required=True, help="Directory that stores baseline JSON files.")
    parser.add_argument(
        "--runner",
        required=True,
        help="Command template used to execute each test. Use {gsf} as the placeholder for the test path.",
    )
    parser.add_argument("--cwd", help="Optional working directory for test execution.")
    parser.add_argument("--report-json", help="Optional JSON report output path.")
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write current execution output as the baseline instead of comparing against an existing baseline.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    test_root = Path(args.test_root).resolve()
    baseline_dir = Path(args.baseline_dir).resolve()
    cwd = Path(args.cwd).resolve() if args.cwd else None

    results, exit_code = process_tests(
        test_root=test_root,
        baseline_dir=baseline_dir,
        command_template=args.runner,
        write_baseline=args.write_baseline,
        cwd=cwd,
    )
    write_report(results, Path(args.report_json).resolve() if args.report_json else None)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
