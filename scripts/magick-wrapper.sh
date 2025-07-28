#!/bin/bash
# Wrapper script to simulate ImageMagick v7 `magick convert` command required by Snakemake

# If the first argument is 'convert', remove it
if [ "$1" = "convert" ]; then
    shift
fi

# Call the 'convert' command with the remaining arguments
/usr/bin/convert "$@"
