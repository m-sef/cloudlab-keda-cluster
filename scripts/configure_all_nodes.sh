#!/usr/bin/env bash

NODE_COUNT=$1

for ((i=1; i<=NODE_COUNT; i++)); do
    NODE=10.10.1.$i

    if ip -4 addr show | grep -q "inet ${NODE}/"; then
        continue
    fi

    ssh -o StrictHostKeyChecking=no $NODE "sudo /local/repository/scripts/disable_hyperthreading.sh"
    ssh -o StrictHostKeyChecking=no $NODE "sudo /local/repository/scripts/disable_turboboost.sh"
    ssh -o StrictHostKeyChecking=no $NODE "sudo /local/repository/scripts/set_all_cores_policy.sh performance"
done

exit 0