#🚀 H.A.W.K

#Hybrid Adaptive Waypoint Knowledge for Multi-Domain UAV Navigation

🔗 GitHub Repository:
https://github.com/abhi301203/HAWK


---

📌 Overview

H.A.W.K (Hybrid Adaptive Waypoint Knowledge) is an intelligent UAV navigation system designed to perform autonomous exploration, understand human instructions, and continuously learn from its environment.

Unlike traditional drone systems that rely on fixed paths or manual control, this project focuses on building a system that can operate independently in unknown environments. It combines computer vision, natural language understanding, navigation strategies, and adaptive learning into a single framework.

The system is developed and tested using Microsoft AirSim, allowing realistic simulation of UAV behavior before real-world deployment.


---

🎯 Objectives

Enable UAV control using natural language instructions

Perform autonomous exploration in unknown environments

Build and reuse knowledge from previous runs

Adapt to multiple environments (domains)

Combine perception, memory, and decision-making



---

🧠 Key Features

🔹 Vision-Language Navigation (VLN)

Accepts commands like:

"go to car"

"go near tree"


Uses NLP + perception + memory to execute tasks



---

🔹 Autonomous Exploration

Grid-based and frontier-based exploration

Covers unknown areas efficiently

Collects data during movement



---

🔹 Object Detection

Uses YOLOv8 for real-time detection

Detects objects such as:

cars

people

trees




---

🔹 Domain Adaptation

Identifies environment type (city, blocks, etc.)

Uses feature extraction and similarity matching

Reuses previously learned knowledge



---

🔹 Self Dataset Generation

Automatically collects:

images

logs

metadata


Organizes them into structured datasets



---

🔹 Memory System

Stores:

object locations

past instructions

navigation paths


Improves decision-making over time



---

🏗️ Project Structure

HAWK/
│
├── hawk_system/
├── phase2/
├── phase3/
├── core/
├── datasets/
├── tools/
├── models/
│
├── config.json
├── hawk_train.py


---

⚙️ How the System Works

1. Initialization

Connects to AirSim

Loads models and system modules



---

2. Environment Detection

Captures images

Extracts features using ResNet

Matches with known domains



---

3. Mode Selection

Input	Mode

No instruction	Exploration
Instruction given	Navigation



---

4. Exploration Mode

Moves using grid and frontier logic

Captures images in multiple directions

Stores environmental data



---

5. Navigation Mode (VLN)

1. Parse instruction


2. Check memory


3. Use perception (YOLO)


4. If not found → explore




---

6. Data Collection

Images

Visit maps

Collision logs

Run logs



---

7. Learning Pipeline

Data is processed automatically

Domain adaptation is performed

System improves for future runs



---

🧪 Technologies Used

Python

PyTorch

OpenCV

YOLOv8

ResNet18

SpaCy

Microsoft AirSim



---

📦 Installation

1. Clone the Repository

git clone https://github.com/abhi301203/HAWK.git
cd HAWK


---

2. Install Dependencies

pip install -r requirements.txt


---

3. Install AirSim

Follow official setup:
https://github.com/microsoft/AirSim


---

4. Download YOLOv8 Weights

https://github.com/ultralytics/ultralytics

Place the file (yolov8n.pt) in the project root.


---

▶️ Running the Project

py -3.9 -m hawk_system.main


---

🧭 Usage

Exploration Mode

Press ENTER without typing anything.


---

Navigation Mode

Example commands:

go to car
go to tree
go to person


---

📊 Example Output

Domain detected (e.g., city)

Exploration starts

Images captured

Dataset pipeline triggered

Learning completed



---

🔮 Future Improvements

Real-world drone deployment

Multi-drone coordination

Better instruction understanding

Reinforcement learning integration

SLAM-based mapping



---

🤝 Contributing

Feel free to fork the repository and submit pull requests.


---

👨‍💻 Authors

Abhinav Samala
Tharun Nalamasu
Rishikesh Tingirikar
Sasiram Anupoju


---

⭐ Final Note

This project is built to explore how autonomous systems can learn, adapt, and make decisions in real-time environments. It combines multiple AI concepts into a single working system and can be extended further for real-world applications.
