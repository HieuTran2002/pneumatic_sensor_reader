#!/bin/bash

if ! $(which v4l2-ctl) > /dev/null
then
    echo "Install v4l-utils, pls."
    exit 1
fi

# Get a list of video devices
video_devices=(/dev/video*)

# Initialize an array to store valid video devices
valid_devices=()

# Iterate through each video device
for device_path in "${video_devices[@]}"; do
    # Check the number of supported video formats for video capture
    num_formats=$(v4l2-ctl --device "$device_path" --all | grep -i 'format video capture' | wc -l)

    # If only one format is supported, consider it valid
    if [ "$num_formats" -eq 1 ]; then
        valid_devices+=("$device_path")
    fi
done

# Print the valid video devices
if [ "${#valid_devices[@]}" -ne 0 ]; then
    for valid_device in "${valid_devices[@]}"; do
        echo "$valid_device"
    done
fi
