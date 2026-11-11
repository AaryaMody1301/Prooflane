"""Reproduce the Python-only judge flow in an isolated clone; no provider access."""
import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clone", type=Path)
    args = parser.parse_args()
    clone = args.clone.resolve()
    assert not (clone / ".env").exists(), "Use a clone without local credentials."
    assert not (clone / "prooflane.sqlite3").exists(), "Use a fresh clone without saved projects."
    env = {k: v for k, v in os.environ.items() if not (k.startswith(("GEMINI_", "PAYPAL_", "PROOFLANE_")) or k in {"AI_MODE", "PAYMENT_MODE", "PORT"})}
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env["PORT"] = str(port)  # Avoid disturbing the real sandbox app on documented port 8787.
    base = f"http://127.0.0.1:{port}"
    report = {"python": sys.version.split()[0], "platform": sys.platform, "clone_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=clone, text=True).strip(), "env_file_present": False, "initial_database_present": False, "package_installs": 0, "provider_calls": 0, "port_override_for_isolation": port, "steps": {}}

    def request(path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = Request(base + path, data=data, headers={"Content-Type": "application/json", "X-Prooflane-Request": "1"})
        with urlopen(req, timeout=10) as response:
            return json.load(response)

    def start():
        process = subprocess.Popen([sys.executable, "app.py"], cwd=clone, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("Clean server did not start: " + process.stderr.read().decode())
            try:
                config = request("/api/config")
                assert config["ai_mode"] == "sample" and config["payment_mode"] == "simulation"
                return process, config
            except (URLError, ConnectionError):
                time.sleep(0.1)
        process.terminate()
        raise RuntimeError("Clean server did not become ready.")

    def stop(process):
        process.terminate()
        process.communicate(timeout=10)

    source = (clone / "examples/source.csv").read_text()
    process, config = start()
    try:
        p = request("/api/projects", {"brief": config["source_brief"], "price": "1.00"})
        assert len(p["plan"]["checks"]) == 7
        path = "/api/projects/" + p["id"]
        request(path + "/agree", {"source_csv": source})
        for name, failures in (("substituted", 2), ("changed-value", 1)):
            p = request(path + "/verify", {"source_csv": source, "csv": (clone / f"examples/{name}.csv").read_text()})
            assert p["status"] == "BLOCKED"
            assert sum(not c["passed"] for c in p["verification"]["checks"]) == failures
            report["steps"][name] = "blocked"
        before = request(path)
        try:
            request(path + "/verify", {"source_csv": source, "csv": "bad,header\nshort\n"})
            raise AssertionError("Malformed upload was accepted")
        except HTTPError as error:
            assert error.code == 400
        assert request(path) == before
        report["steps"]["invalid_upload_preserves_state"] = True
        proposal = request(path + "/repair", {"source_csv": source, "csv": (clone / "examples/changed-value.csv").read_text()})
        corrected = proposal["csv"]
        p = request(path + "/verify", {"source_csv": source, "csv": corrected})
        assert p["status"] == "VERIFIED"
        request(path + "/approve", {})
        p = request(path + "/order", {})
        p = request(path + "/capture", {"order_id": p["order"]["id"]})
        assert p["status"] == "PAID" and p["receipt"]["mode"] == "simulation"
        assert request(path + "/capture", {"order_id": p["order"]["id"]}) == p
        evidence = request(path + "/evidence")
        report["steps"]["seven_checks_correction_approval_simulation_export"] = True
        with tempfile.TemporaryDirectory(prefix="independent-verifier-") as temp:
            independent = Path(temp)
            for name in ("app.py", "verify_receipt.py"):
                shutil.copyfile(clone / name, independent / name)
            (independent / "receipt.json").write_text(json.dumps(evidence), encoding="utf-8")
            (independent / "delivery.csv").write_text(corrected, encoding="utf-8", newline="")
            (independent / "source.csv").write_text(source, encoding="utf-8", newline="")
            command = [sys.executable, "verify_receipt.py", "receipt.json", "delivery.csv", "--source", "source.csv"]
            result = subprocess.run(command, cwd=independent, env=env, capture_output=True, text=True)
            assert result.returncode == 0, result.stdout + result.stderr
            report["independent_verifier"] = json.loads(result.stdout)
            for attack in ("delivery", "source", "amount", "manifest"):
                changed = json.loads(json.dumps(evidence))
                (independent / "delivery.csv").write_text(corrected, encoding="utf-8")
                (independent / "source.csv").write_text(source, encoding="utf-8")
                if attack in {"delivery", "source"}:
                    (independent / f"{attack}.csv").write_text((clone / "examples/changed-value.csv").read_text(), encoding="utf-8")
                elif attack == "amount":
                    changed["project"]["cents"] += 1
                else:
                    changed["project"]["manifest"]["brief"] += " tampered"
                (independent / "receipt.json").write_text(json.dumps(changed), encoding="utf-8")
                result = subprocess.run(command, cwd=independent, env=env, capture_output=True, text=True)
                assert result.returncode == 1 and not json.loads(result.stdout)["local_checks_passed"]
                report["steps"]["reject_changed_" + attack] = True
            (independent / "receipt.json").write_text(json.dumps(evidence), encoding="utf-8")
            result = subprocess.run(command + ["--paypal"], cwd=independent, env=env, capture_output=True, text=True)
            assert result.returncode == 1 and "credentials" in result.stdout
            assert not (independent / "prooflane.sqlite3").exists()
            report["steps"]["missing_provider_credentials_fail_honestly_no_database"] = True
    finally:
        stop(process)
    process, _ = start()
    try:
        assert request(path) == p
        report["steps"]["persisted_receipt_after_actual_server_restart"] = True
    finally:
        stop(process)
    report["passed"] = True
    output = Path(__file__).parent / "CLEAN_INSTALL_2026-11-11.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
