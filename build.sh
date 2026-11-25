#!/bin/sh
set -eu
cd "$(dirname "$0")/source"
for helper in outline normalize boolean; do
  swiftc "$helper.swift" -o "$helper"
done
python3 build.py
