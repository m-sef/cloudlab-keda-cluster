#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
NODE_COUNT=$1

if ! "$SCRIPT_DIR/is_master.sh"; then
    exit 1
fi

for ((i=1; i<=NODE_COUNT; i++)); do
    NODE=10.10.1.$i

    ssh -o StrictHostKeyChecking=no $NODE "sudo /local/repository/scripts/disable_hyperthreading.sh"
    ssh -o StrictHostKeyChecking=no $NODE "sudo /local/repository/scripts/disable_turboboost.sh"
    ssh -o StrictHostKeyChecking=no $NODE "sudo /local/repository/scripts/set_all_cores_policy.sh performance"
done

exit 0