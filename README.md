# Performance and Interference Analysis on BeagleBone AI-64

**Authors:**
- [Vincenzo Luigi Bruno](https://github.com/vlb20)
- [Salvatore Cangiano](https://github.com/Salvr28)

The primary objective of this study is to provide a quantitative characterization of the performance interference between AI workloads and system-level tasks on the BeagleBone AI-64 platform.

To investigate this, the research is guided by two specific aims:
1. To evaluate the resilience of the AI inference process against various types of system-wide resource contention. This is achieved by measuring the **Inference Time** of several standard neural network models while the system is subjected to controlled stress on its CPU, memory, and I/O subsystems with `stress-ng`.
2. To quantify the reciprocal impact of a sustained AI workload on the predictability of a high-priority, real-time task. This is achieved by measuring the **Maximum Scheduling Latency** of a `cyclictest` task running on the main CPU while the AI accelerators are concurrently active.

---

### Indice
1. [Board & System Specification](#board--system-specification)
2. [Board Setup](#board-setup)
3. [How to run the experiments](#how-to-run-the-experiments)
4. [Data Analysis](#data-analysis)

---

### Board & System Specification
- **Platform**: BeagleBone AI-64
- **CPU**: Dual-core 64-bit Arm Cortex-A72
- **AI Accelerators**: C71x DSP and Matrix Multiplication Accelerator (MMA)
- **Memory**: 4GB LPDDR4 RAM, 16GB eMMC Flash
- **Operating System**: `BBAI64 11.8 2023-10-07 10GB eMMC TI EDGEAI Xfce Flasher`
- **Kernel**: Linux 5.10.168-ti-arm64-r111

---

### Board Setup

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

### How to run the experiments

**Step 1: Prepare the test image set**

The tests use a fixed set of input images to ensure consistency. The images provided by the SDK in `/opt/edge_ai_apps/data/images/` were used. The original set of 30 images was replicated to create a larger dataset of 90 images for each run.

**Step 2: Prepare the demo configuration file**

A single YAML configuration file, `rtsia_config.yaml`, located in `/opt/edge_ai_apps/configs/`, is used to control the demo application. This file defines the input image sequence and the output settings. To test a specific model, the `model_path` key within the `flows` section of this file must be manually updated to point to one of the models listed in the table above.

**Step 3: Execute the automated test script**

The test execution is partially automated using the `run_experiment.sh` script (included in this repository). This script launches the AI workload for 30 repetitions to gather statistically relevant data.

1. **For baseline ("no-stress") tests**:
   From your home directory (/home/debian), run the script with the path to the YAML config and the desired results directory.
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

### Data Analysis
After all experiments are complete, the `~/results` directory on the BeagleBone will contain all the raw log files.
1. Transfer the `results` directory back to your PC using `scp`.
2. The `analysis/` folder in this repository contains Python scripts to automatically parse all log files, consolidate the data, and generate the final boxplots for the report.
