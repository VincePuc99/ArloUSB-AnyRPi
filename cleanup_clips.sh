#!/bin/bash
CLIP_STORE=/share/arlo
#RETENTION_DURATION=${1:-14}
RETENTION_DURATION=14

find "$CLIP_STORE" -maxdepth 5 -type f -mtime +"$RETENTION_DURATION" -print | xargs -r rm
find "$CLI_STORE"/arlo/metadata/ -type d -empty -delete