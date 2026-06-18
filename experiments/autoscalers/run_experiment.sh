#!/usr/bin/env bash
# Author(s): Han Dong (hdong@hamilton.edu)
#            Seth Moore (slmoore@hamilton.edu)

# --- CONFIGURATION (Hardcoded for simplicity) ---

# Helper function to run Vegeta load
run_rate()
{
  local rate=$1
  local duration=$2
  local log_file=$3
  echo "GET ${TARGET_URL}:8080/?burn=30" | \
      vegeta attack -rate="${rate}/s" -duration="${duration}" | \
      vegeta encode -to=csv -output="${log_file}"
}

run_experiments()
{
    NAME=$1
    YAML=$2
    RUNS=$3

    kubectl apply -f $YAML
    
    sleep 60

    TARGET_URL="http://$(kubectl get svc webserver-service -n webserver -o jsonpath='{.spec.clusterIP}')"

    # --- MAIN LOOP FOR RERUNS ---
    for run_id in $(seq 1 ${RUNS}); do
        echo "=========================================="
        echo " STARTING EXPERIMENT RUN: ${run_id} @ ${TARGET_URL}"
        echo "=========================================="
        
        # 1. Create a clean folder for this specific run's results
        FOLDER_NAME="results/${NAME}/experiment_run_${run_id}"
        mkdir -p "${FOLDER_NAME}"

        # 2. Start HPA monitoring in the background and log to watch.log
        echo "NAME   REFERENCE        TARGETS        MINPODS   MAXPODS   REPLICAS   AGE" > "${FOLDER_NAME}/replicas.log"
        
        # This loop runs silently in the background ($! grabs its process ID)
        while true; do
            kubectl get hpa -n webserver | tail -n 1 >> "${FOLDER_NAME}/replicas.log" 2>/dev/null
            sleep 1
        done &
        WATCHER_PID=$!

        # 3. Execute the Traffic Ramp
        echo "--- Baseline: 10 req/s (1 minute) ---"
        run_rate 10 "1m" "${FOLDER_NAME}/vegeta1.log"

        echo "--- Spike: 60 req/s (3 minutes) ---"
        run_rate 60 "3m" "${FOLDER_NAME}/vegeta2.log"

        echo "--- Cool down: 10 req/s (1 minute) ---"
        run_rate 10 "1m" "${FOLDER_NAME}/vegeta3.log"

        # 4. Ramp finished. Hold and watch for an extra 5 minutes
        echo "--- Traffic ramp finished. Monitoring HPA for an extra 5 minutes... ---"
        sleep 5m

        # 5. Stop the background HPA watcher
        kill ${WATCHER_PID}
        
        echo "RUN ${run_id} COMPLETE! Output saved to folder: ${FOLDER_NAME}"
        echo "------------------------------------------"
    done

    echo "ALL RUNS COMPLETED SUCCESSFULLY."

    kubectl delete -f $YAML
}

run_experiments fixed_replica_count yaml/webserver_fixed_replica_count.yaml 5
run_experiments default_hpa yaml/webserver_default_hpa.yaml 5
run_experiments tuned_hpa yaml/webserver_tuned_hpa.yaml 5
run_experiments keda_cpu yaml/webserver_keda_cpu_scaler.yaml 5
run_experiments keda_prometheus yaml/webserver_keda_prometheus.yaml 5

exit 0
