#!/bin/bash

echo "Running script in an infinite loop."
echo "(automatically restarting on failure)"
echo

while :
do
    python main.py
    sleep 1
done
