#!/usr/bin/env python3
import os
import re
import matplotlib.pyplot as plt

results_dir = os.path.join(os.path.dirname(__file__), "results")

data = []
for entry in os.listdir(results_dir):
    parts = entry.split("_")
    if len(parts) != 2:
        continue
    update_frac, target_qps = parts
    leader_log = os.path.join(results_dir, entry, "leader.log")
    if not os.path.exists(leader_log):
        continue

    p99_read = p99_update = actual_qps = None
    with open(leader_log) as f:
        for line in f:
            if line.startswith("read"):
                p99_read = float(line.split()[8])
            elif line.startswith("update"):
                p99_update = float(line.split()[8])
            elif line.startswith("Total QPS"):
                m = re.search(r"Total QPS = ([\d.]+)", line)
                if m:
                    actual_qps = float(m.group(1))

    if p99_read is not None and p99_update is not None:
        data.append((int(target_qps), actual_qps, p99_read, p99_update))

data.sort(key=lambda x: x[0])
target_qps_vals = [d[0] for d in data]
p99_read_vals = [d[2] for d in data]
p99_update_vals = [d[3] for d in data]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(target_qps_vals, p99_read_vals, marker="o", label="P99 Read latency")
ax.plot(target_qps_vals, p99_update_vals, marker="s", label="P99 Update latency")

ax.set_xlabel("Target QPS")
ax.set_ylabel("P99 Latency (µs)")
ax.set_title("Memcached P99 Latency vs QPS (update fraction = 0.25)")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xticks(target_qps_vals)
ax.set_xticklabels(target_qps_vals, rotation=45)

out = os.path.join(os.path.dirname(__file__), "p99_latency.png")
plt.tight_layout()
plt.savefig(out, dpi=150)
print(f"Saved to {out}")

for d in data:
    print(f"QPS {d[0]:5d} (actual {d[1]:7.1f}): read P99={d[2]:.1f}µs  update P99={d[3]:.1f}µs")
