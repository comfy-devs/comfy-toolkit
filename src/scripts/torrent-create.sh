#!/bin/bash
# Creates a torrent for a series
# Arguments: 1 (source folder), 2 (destination .torrent file), 3 (torrent name), 4 (torrent comment)

cd ../create-torrent
yarn process "$1" "$2" "$3" "$4"
cd ../scripts
