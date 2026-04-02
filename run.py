"""Unified CLI entry point."""

import argparse
import logging
import sys


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="DiachronicVec CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("preprocess", help="Preprocess corpus texts")
    sub.add_parser("train", help="Train Word2Vec models")
    sub.add_parser("align", help="Align models via Procrustes")
    sub.add_parser("pipeline", help="Run preprocess -> train -> align")
    sub.add_parser("serve", help="Start FastAPI server")

    args = parser.parse_args()

    if args.command == "preprocess":
        from diachronic.preprocess import preprocess_all
        preprocess_all()
    elif args.command == "train":
        from diachronic.train import train_all
        train_all()
    elif args.command == "align":
        from diachronic.align import align_all
        align_all()
    elif args.command == "pipeline":
        from diachronic.preprocess import preprocess_all
        from diachronic.train import train_all
        from diachronic.align import align_all
        preprocess_all()
        train_all()
        align_all()
    elif args.command == "serve":
        import uvicorn
        uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
