# ConnectGrabber

An automated, headless tool designed to log into **Adobe Connect** live sessions, bypass interactive prompt obstacles, and record both video and audio directly into high-quality `.mp4` containers using Docker, Selenium, and FFmpeg.

---

## Features

* **Headless Visual Environment:** Runs a virtual frame buffer via `Xvfb` (1920x1080 resolution), eliminating the need for a physical desktop environment.
* **Audio Interception:** Spawns a background `PulseAudio` server to accurately trap and stitch internal session audio directly into the recording.
* **Smart Interaction Simulation:** Uses hardware-level OS commands (`xdotool`) to clear initial media-engagement blocks often triggered by modern web browsers.
* **Multi-Class Concurrent Orchestration:** Fully containerized with Docker Compose to let you record multiple live rooms simultaneously without cross-talk or visual overlap.

---

## Prerequisites

Before starting, ensure you have the following installed on your host system:
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

---

## Directory Structure

Ensure your project files are arranged as follows:
```text
.
├── docker-compose.yml
├── Dockerfile
├── recorder.py
└── videos/            # Your recordings will be stored here
```

## Configuration & Usage
### 1. Configure the Environment
Open the docker-compose.yml file. You need to provide your exact session URLs and account credentials for each service configuration.

```yaml
version: '3.8'

services:
  class_one:
    build: .
    volumes:
      - ./videos:/output
    environment:
      - CLASS_URL=https://your-institution.adobeconnect.com/room-abc/
      - USERNAME=your_username
      - PASSWORD=your_password
      - RECORD_DURATION=3060 # Recording duration in seconds
      - OUTPUT_FILE=/output/class_one_session.mp4

  class_two:
    build: .
    volumes:
      - ./videos:/output
    environment:
      - CLASS_URL=https://your-institution.adobeconnect.com/room-xyz/
      - USERNAME=your_username
      - PASSWORD=your_password
      - RECORD_DURATION=3600
      - OUTPUT_FILE=/output/class_two_session.mp4
```

### 2. Scaling Out (Adding More Classes)

You can easily scale this to record 3, 4, or more classes concurrently. To add another automated runner, simply append a new block structure inside your docker-compose.yml:

```yaml
class_three:
    build: .
    volumes:
      - ./videos:/output
    environment:
      - CLASS_URL=https://your-institution.adobeconnect.com/room-123/
      - USERNAME=your_username
      - PASSWORD=your_password
      - RECORD_DURATION=5400
      - OUTPUT_FILE=/output/class_three_session.mp4
```

### 3. Execution Commands
Build and start all recording instances:

`docker compose up --build`

Run in detached mode (background):

`docker compose up --build -d`

Stop all recording instances:

`docker compose down`

## Environmental Variable Reference

| Variable Name     | Description                                                          | Default Value           |
| ----------------- | -------------------------------------------------------------------- | ----------------------- |
| `CLASS_URL`       | The landing URL of your online Adobe Connect classroom.              | Required                |
| `USERNAME`        | Login identifier for the room portal.                                | Required                |
| `PASSWORD`        | Security password for the room portal.                               | Required                |
| `RECORD_DURATION` | Length of time (in seconds) FFmpeg should pull data before stopping. | `3600`                  |
| `OUTPUT_FILE`     | Internal container path and filename for the `.mp4` video.           | `/output/recording.mp4` |


## Troubleshooting & Under-the-Hood Mechanics
Note:
- Hardware Click Coordinates: The script utilizes xdotool mousemove 960 580 click 1 to target the exact geometric middle of a standard 1080p viewport. This interacts with Adobe's "Join Audio" or introductory media block overlay. If your platform's prompt positioning deviates wildly, adjust the coordinate parameters inside recorder.py.

- Error Capturing: If elements fail to load due to high connection latency, the app saves a snapshot internally to /tmp/error.png right before exit termination sequences trigger.
