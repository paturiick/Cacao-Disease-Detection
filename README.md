# 🚁 LUPAD: Cacao Disease Detection & Drone Telemetry 

![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D)
![Nuxt.js](https://img.shields.io/badge/Nuxt.js-002E3B?style=for-the-badge&logo=nuxt.js&logoColor=00DC82)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

**LUPAD** is an advanced Agri-Tech web application designed to orchestrate autonomous drone flights, monitor real-time telemetry, and perform automated disease detection on cacao pods. It bridges telecommunications infrastructure with agricultural management to provide pilots and farmers with actionable, data-driven insights.

## 📖 About the Study
This project explores the integration of drone flight automation with real-time computer vision to identify healthy vs. diseased cacao pods. By utilizing a robust full-stack architecture, the system safely transmits flight coordinates, streams live telemetry via Server-Sent Events (SSE), and aggregates detection analytics into a centralized database. 

It was developed with a focus on scalable network infrastructure, reliable data transmission, and highly responsive user interfaces.

---

## ✨ Core Features

### 🗺️ Autonomous Mission Planner
* **Interactive Flight Queue:** Drag-and-drop interface to build flight paths using precise commands (Takeoff, Land, RC Override, Hover, and XYZ vector navigation).
* **Preset Management:** Save, duplicate, and load flight configurations locally and sync them to the backend.
* **Safety Protocols:** Hardcoded constraints prevent invalid coordinates (e.g., limiting manual distance inputs to a maximum of 300cm) to ensure drone safety.

### 📡 Live Telemetry & Monitoring
* **Real-Time Data:** Streams battery life, GPS status, altitude, and drone speed directly to the dashboard.
* **RC Flight Control:** Manual override panel for emergency landings and live Roll/Pitch/Throttle/Yaw adjustments.
* **Camera Integration:** `[mon]` command toggles downward-facing camera detection during active flight routes.

### 📊 Detection Analytics
* **Lifetime Scan Records:** Tracks the total volume of scanned cacao pods across all missions.
* **Health Categorization:** Automatically categorizes pods into **Healthy** and **Diseased** metrics.
* **Data Visualization:** Utilizes Chart.js with custom gradients to visualize detection trends over time.

### 🧑‍✈️ Pilot Profile & Security
* **Identity Management:** Secure pilot authentication and account management.
* **Performance Tracking:** Individual dashboard showcasing the pilot's specific contributions to the agricultural surveys.

---

## 🛠️ Technology Stack

* **Frontend:** Vue.js 3 / Nuxt.js, Tailwind CSS (Glassmorphic UI Design), Chart.js
* **Backend:** Python, Django REST Framework
* **Database:** PostgreSQL (Containerized)
* **Environment & Tools:** Windows Subsystem for Linux (WSL), Docker, Git
