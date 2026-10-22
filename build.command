#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/launcher"
./gradlew --no-daemon testReleaseUnitTest lintRelease assembleRelease --console=plain
