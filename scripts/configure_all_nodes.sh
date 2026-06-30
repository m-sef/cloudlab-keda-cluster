#!/usr/bin/env bash

NODE_COUNT=$1

for ((i=1; i<=NODE_COUNT; i++)); do
    ssh 10.10.1.$i "sudo /local/repository/scripts/disable_hyperthreading.sh"
    ssh 10.10.1.$i "sudo /local/repository/scripts/disable_turboboost.sh"
    ssh 10.10.1.$i "sudo /local/repository/scripts/set_all_cores_policy.sh performance"
done

exit 0