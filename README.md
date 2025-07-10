# Performance and Interference Analysis on BeagleBone AI-64

**Authors:**
- [Vincenzo Luigi Bruno](https://github.com/vlb20)
- [Salvatore Cangiano](https://github.com/Salvr28)

<img src="https://github.com/user-attachments/assets/a8b23c94-1a56-4539-86d6-5e93ec562d64" alt="Icon BB" width="300"/>

--- 

This study quantifies the performance interference between AI workloads and system-level tasks on the BeagleBone AI-64 platform.

Specific Aims:

1. **To evaluate AI resilience under system stress**: We measure the `Inference Time` of standard neural network models while placing the CPU, memory, and I/O subsystems under controlled stress with `stress-ng`.
2. **To measure AI's impact on real-time performance**: We quantify the effect of a sustained AI workload on task predictability by measuring the `Maximum Scheduling Latency` of a high-priority `cyclictest` task running concurrently with the AI accelerators.

---

## Table of Contents
1. [Board & System Specification](#board--system-specification)
2. [Board Setup](#board-setup)
3. [How to run the "Impact of stressor on AI workload" experiment](#how-to-run-the-impact-of-stressor-on-ai-workload-experiment)
4. [How to run the "Impact of AI workload on Real-Time Task" experiment](#how-to-run-the-impact-of-ai-workload-on-real-time-task-experiment)
5. [Data Analysis](#data-analysis)

---

## Repository Structure
This repository is organized into directories for data analysis and experiment execution. 

```
.
├── data_results_and_analysis/       # Pyhon scripts for data analysis and log files from Beaglebone
│   ├── cyclic_test_isolated_data/     # log files from cyclictest runs in the isolated CPU scenario
│   ├── cyclic_test_not_isolated_data/ # non-isolated scenario
│   ├── stress_on_ai_data/             # log files from AI inference experiments under stress-ng 
│   ├── box_plotter.py                 # Python class utility used for generating boxplots
│   └── main_plot.py                   # Main analysis script: parse all data and generate plots
├── experiments_scripts/            # Configuration and automation experiment scripts for BB-AI-64 
│   ├── rtsia_config.yaml              # YAML configuration file for the TI Edge AI application
│   ├── run_ex.sh                      # Script for automating the "stressor on AI workload" exp.
│   ├── run_test_isolated.sh           # Script for automating the cyclictest experiment
│   └── run_test_not_isolated.sh
├── README.md
└── requirements.txt                # Python dependencies required to run the analysis scripts
```

- **`rtisia_config.yaml`**: destination on BeagleBone `/opt/edge_ai_apps/configs/`
- **`run_ex.sh`**: destination on BeagleBone `/home/debian/rtsia/`
- **`run_test_isolated.sh`** & **`run_test_not_isolated.sh`**: destination on BeagleBone `/home/debian/rtsia/cyclictest/`

---

## Board & System Specification
- **Platform**: BeagleBone AI-64
- **CPU**: Dual-core 64-bit Arm Cortex-A72
- **AI Accelerators**: C71x DSP and Matrix Multiplication Accelerator (MMA)
- **Memory**: 4GB LPDDR4 RAM, 16GB eMMC Flash
- **Operating System**: `BBAI64 11.8 2023-10-07 10GB eMMC TI EDGEAI Xfce Flasher`
- **Kernel**: Linux 5.10.168-ti-arm64-r111

<img src="https://github.com/user-attachments/assets/7a263ec9-469c-4634-b5c6-3e0ddfb6b360" alt="Icon BB-AI-64" width="300"/>

---

## Board Setup

**Step 1: Flash the board image**

The board was flashed with the official `BBAI64 11.8 2023-10-07 10GB eMMC TI EDGEAI Xfce Flasher` image to ensure a clean and stable starting point.

**Step 2: Install dependencies and stress tools**

```bash
sudo apt update
sudo apt install -y rt-tests stress-ng
```

**Step 3: Prepare AI Models**

The AI models used in this experiment are provided by the pre-installed TI Edge AI SDK. The models were downloaded using the included script.
1. Navigate to the main SDK directory:
  ```bash
  cd /opt/edge_ai_apps
  ```
2. Run the downloader script to select and install the required models from the TI Model Zoo:
  ```bash
  ./download_models.sh
  ```
The downloaded models will be placed in the `/opt/model_zoo/` directory.

**Step 4: Models used**

The following table lists the models used for the experiments and their respective paths on the system.

| Model Name | System Path |
| :--- | :--- |
| MobileNet v1 | `/opt/model_zoo/TFL-CL-0000-mobileNetV1-mlperf` |
| MobileNet v2 | `/opt/model_zoo/ONR-CL-6070-mobileNetV2` |
| SSD MobileNet v1 | `/opt/model_zoo/TFL-OD-2000-ssd-mobV1-coco-mlperf-300x300` |
| SSD MobileNet v2 | `/opt/model_zoo/TFL-OD-2010-ssd-mobV2-coco-mlperf-300x300` |

---

## How to run the "Impact of stressor on AI workload" experiment

**Step 1: Prepare the test image set**

The tests use a fixed set of input images to ensure consistency. The images provided by the SDK in `/opt/edge_ai_apps/data/images/` were used. The original set of 30 images was replicated to create a larger dataset of 90 images for each run.

**Step 2: Prepare the demo configuration file**

A single YAML configuration file, `rtsia_config.yaml`, located in `/opt/edge_ai_apps/configs/`, is used to control the demo application. This file defines the input image sequence and the output settings. To test a specific model, the `model_path` key within the `flows` section of this file must be manually updated to point to one of the models listed in the table above.

**Step 3: Execute the automated test script**

The test execution is partially automated using the `run_experiment.sh` script (included in this repository). This script launches the AI workload for 30 repetitions to gather statistically relevant data.

1. **For baseline ("no-stress") tests**:
   From your home directory (`/home/debian`), run the script with the path to the YAML config and the desired results directory.
  ```bash
  # Example for running MobileNetV1 without stress
  sudo ./run_experiment.sh /opt/edge_ai_apps/configs/rtsia_config.yaml ~/results/mobilenetV1/no_stress
  ```

2. **For tests with stressors**:
   This requires two terminals connected to the BeagleBone.
   - **Terminal 1**: Launch the desired stressor command (e.g., stress-ng --cpu 4).
   - **Terminal 2**: Immediately after, launch the automation script as shown above.
   This process must be repeated for each of the seven stressors (`cpu`, `vm`, `memcpy`, `interrupt`, `open`, `fork`, `udp`).

---

## How to run the "Impact of AI workload on Real-Time Task" experiment

This experiment quantifies the impact of a sustained AI workload on the maximum scheduling latency of a high-priority, real-time task using `cyclictest`. The experiment is conducted in two scenarios: 
- on a standard, non-isolated system,
- and on a system with a dedicated, isolated CPU core for the real-time task.

### Scenario A: Non-Isolated Environment
In this scenario, `cyclictest` and all other system tasks share the CPU cores without any specific affinity.

**Step 1: Baseline measurement (No AI Workload)**

First, measure the baseline real-time performance of the system without any AI workload.

1. Navigate to the test scripts directory (e.g., `~/rtisia/cyclictest`)
2. Run the `run_test_not_isolated.sh` script, which executes `cyclictest` for 30 iterations and saves the maximum latency from each run.

```bash
# This script runs: sudo cyclictest --mlockall --priority=90 --duration=30
sudo ./run_test_not_isolated.sh baseline_not_isolated.txt
```

**Step 2: Measurement with AI Workload**

Next, measure the latency while an AI model is actively running. This requires two terminals.

1. **Terminal 1 (AI Workload):**

   - Ensure the `rtsia_config.yaml` file is configured for the desired AI model.
   - Launch the AI workload from the `home/debian` directory.
     ```bash
      # Example for running MobileNetV1 workload
      sudo ./run_experiment.sh /opt/edge_ai_apps/configs/rtsia_config.yaml ~/results/mobilenetV1/cyclictest_not_isolated
     ```

2. **Terminal 2 (Real-Time test):**

   - Immediately after starting the AI workload, launch the `cyclictest` script as before.
   - Save the results to a file named after the AI model being tested.

3. Repeat this process for each AI model.

### Scenario B: Isolated CPU Environment

In this scenario, Core 1 is isolated from the general kernel scheduler to exclusively run the `cyclictest` task, minimizing interference from other processes.

**Step 1: Configure core isolation**

1. **Modify kernel boot arguments**: Edit the U-Boot configuration file to add kernel boot parameters for isolation.
   ```bash
   sudo nano /boot/firmware/extlinux/extlinux.conf
   ```

   Find the line beginning with `append` whithin the label `BeagleBone AI-64 eMMC (default)` and add `isolcpus=1 rcu_nocbs=1` to the end of it. The result should look similar to this:
   ```bash
   append ... quiet isolcpus=1 rcu_nocbs=1
   ```

   > **Note on `nohz_full`**: The `nohz_full=1` parameter is omitted as the default kernel is not compiled with `CONFIG_NO_HZ_FULL=y`, rendering the parameter ineffective. This can be verified with `grep CONFIG_NO_HZ_FULL /boot/config-$(uname -r).`.

   > **Note on Interrupt Affinity**: Complete core isolation requires migrating device interrupts. An analysis via `cat /proc/interrupts` shows that the only interrupt remaining on the isolated Core 1 is IRQ 11 (`arch_time`). This is a per-CPU timer essential for the core's internal scheduling and cannot be migrated. The kernel intentionally locks its affinity to ensure system stability.

2. **Reboot the board**: Apply the changes by rebooting the system.
   ```bash
   sudo reboot
   ```

**Step 2: Baseline measurement (Isolated core)**

After rebooting, repeat the baseline measurement, this time pinning `cyclictest` to the isolated Core 1 using `taskset`.

```bash
# This script runs: sudo taskset -c 1 cyclictest --mlockall --priority=90 --duration=30
sudo ./run_test_isolated.sh baseline_isolated.txt
```

**Step 3: Measurement with AI Workload (Isolated core)**

Finally, repeat the interference test from Scenario A, but use the isolated test script.
  
---

## Data Analysis
After all experiments are complete, the `~/results` directory on the BeagleBone will contain all the raw log files.
1. Transfer the `results` directory back to your PC using `scp`.
2. The `analysis/` folder in this repository contains Python scripts to automatically parse all log files, consolidate the data, and generate the final boxplots for the report.

> It is recommended to use the file `requirements.txt` to set up a virtual environment on your host PC before running `main_plot.py`.
