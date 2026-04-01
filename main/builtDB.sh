#!/usr/bin/env bash
# For parameters see .env

set -euo pipefail

# Load environment variables
set -a
source config.env
set +a

CURRENT_DIR="$(pwd)"
export CURRENT_DIR

SRC="$SOURCE_DIR"
DST="$OUT_DIRECTORY/inputs"

# Helper functions
copy_file() {
    local src="$1"
    local dst="$2"

    if [ -f "$src" ]; then
        cp "$src" "$dst"
    else
        echo "Warning: Missing file $src"
    fi
}

copy_dir() {
    local src_dir="$1"
    local dst_dir="$2"

    mkdir -p "$dst_dir"

    if [ -d "$src_dir" ]; then
        cp "$src_dir"/* "$dst_dir/" 2>/dev/null || true
    else
        echo "Warning: Missing directory $src_dir"
    fi
}

# =========================
# Manual databases handling
# =========================
if [ "$MANUAL_DATABASES" = "true" ]; then
    echo "Processing manual databases..."

    ## Bat Eco-Interactions
    copy_file "$SRC/$BATECO_FILE" "$DST/$BATECO_FILE"

    ## BV-BRC
    mkdir -p "$DST/$BVBRC_DIR"
    copy_dir "$SRC/$BVBRC_DIR" "$DST/$BVBRC_DIR"

    ## DIP
    copy_dir "$SRC/$DIP_DIR" "$DST/$DIP_DIR"

    ## GMPD
    copy_dir "$SRC/$GMPD_DIR" "$DST/$GMPD_DIR"

    ## EID2
    copy_dir "$SRC/$EID2_FILE" "$DST/$EID2_FILE"

    ## Single-file datasets
    copy_file "$SRC/$PHILM2WEB_FILE" "$DST/$PHILM2WEB_FILE"
    copy_file "$SRC/$PHISTO_FILE"    "$DST/$PHISTO_FILE"
    copy_file "$SRC/$FGSCDB_FILE"    "$DST/$FGSCDB_FILE"
fi

# =========================
# Run pipeline
# =========================

if [ "$DOWNLOAD" = "true" ]; then
    echo ">>> Started Step 1: Downloading databases <<<"
    bash ../utils/downloadDB.sh
fi

if [ "$PROCESS" = "true" ]; then
    echo ">>> Started Step 2: Processing databases <<<"
    mkdir -p "$OUT_DIRECTORY/outputs"
    python ../utils/processDB.py
fi

if [ "$AGGREGATE" = "true" ]; then  
    echo ">>> Started Step 3: Aggregating databases <<<"
    python ../utils/aggregateDB.py
fi 

# =========================
# Cleanup
# =========================
if [ "$DELETE" = "true" ]; then
    echo ">>> Cleaning temporary files <<<"
    rm -r "$OUT_DIRECTORY/outputs"
fi