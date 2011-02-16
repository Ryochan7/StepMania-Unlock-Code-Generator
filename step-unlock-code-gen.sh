#!/bin/sh

cd $(dirname $0)
exec python stepmania-unlock-code-generator.py "$@"

