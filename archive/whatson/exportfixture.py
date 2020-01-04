#!/usr/bin/env python


import yaml
import argparse
import webbrowser
import tempfile
from typing import Dict, Any
import base64
import gzip


def fixture_to_html(fixture: Dict[Any, Any]) -> str:
    response = fixture["interactions"][0]["response"]
    body = response["body"]["string"]
    if "gzip" in response["headers"]["Content-Encoding"]:
        body = gzip.decompress(body)

    return body.decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-o", "--output", required=False)
    args = parser.parse_args()

    with open(args.filename) as infile:
        parsed = yaml.safe_load(infile)

    text = fixture_to_html(parsed)

    if args.output is not None:
        with open(args.output, "w") as outfile:
            outfile.write(text)

    else:
        with tempfile.NamedTemporaryFile(
            suffix=".html", mode="w", delete=False
        ) as outfile:
            outfile.write(text)

            outfile.seek(0)

            webbrowser.open("file:///{}".format(outfile.name))


if __name__ == "__main__":
    main()
