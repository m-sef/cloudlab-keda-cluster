#!/usr/bin/env bash

NODE_COUNT=$1

for i in $NODE_COUNT; do
    sudo ssh 10.10.1.$i "sudo /local/repository/scripts/disable_hyperthreading.sh && sudo /local/repository/scripts/disable_turboboost.sh && sudo /local/repository/scripts/set_all_cores_policy.sh performance"
done;

exit 0