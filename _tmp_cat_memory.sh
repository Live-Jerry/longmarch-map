#!/bin/bash
cd /opt/longmarch-dev
for f in memory/*.md; do
    echo "=== $f ==="
    head -100 "$f"
    echo
done
