from __future__ import annotations

import argparse
import os

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Scalable image upload API runner")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=3001, help="Port to bind")
    parser.add_argument("--instance", default=None, help="Optional instance name override")
    args = parser.parse_args()

    if args.instance:
        os.environ["INSTANCE_ID"] = args.instance

    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
