"""Verify exported evidence and CSVs without the original project database. Python standard library only."""
import argparse
import json
import os
from pathlib import Path

from app import PayPal, Problem, load_env, verify_evidence


def read_text(path, limit):
    with path.open("rb") as file:
        raw = file.read(limit + 1)
    if len(raw) > limit:
        raise Problem("Evidence supports 1 MB; each UTF-8 CSV supports 300 KB.")
    return raw.decode("utf-8-sig")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--source", type=Path, help="Original CSV for source-comparison agreements")
    parser.add_argument("--paypal", action="store_true", help="Read-only authenticated sandbox lookup; never creates orders or captures")
    args = parser.parse_args()
    try:
        paypal = None
        if args.paypal:
            load_env()
            if not all(os.getenv(key) for key in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET")):
                raise Problem("Configure sandbox app credentials locally for PayPal lookup.")
            paypal = PayPal(os.environ["PAYPAL_CLIENT_ID"], os.environ["PAYPAL_CLIENT_SECRET"])
        result = verify_evidence(json.loads(read_text(args.evidence, 1_000_000)), read_text(args.delivery, 300_000), read_text(args.source, 300_000) if args.source else None, paypal)
        print(json.dumps(result, indent=2))
        return 0
    except (Problem, OSError, UnicodeError, ValueError, RecursionError) as exc:
        message = str(exc) if isinstance(exc, Problem) else "Files could not be read as a valid UTF-8 evidence export and CSVs."
        print(json.dumps({"local_checks_passed": False, "payment_verified": False, "error": message}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
