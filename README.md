# Educage 🧠🐭  
**Behavioral Experiments for Mice**

---

## Overview

**Educage** is a complete software-and-hardware solution for running behavioral experiments with mice — designed with tired PhD students in mind.

Whether you're training mice in auditory discrimination tasks or running custom paradigms, Educage helps streamline the process and make data collection and analysis easier and more robust.

> Plug in your mice. Press run. Go make coffee.

---

## Features ✨

- 🧠 **User-friendly GUI** for setting up and running experiments  
- 🐭 **Compatible with standard behavioral cages** (e.g., with sound delivery, water reward, and sensors)  
- 📊 **Automated data collection** in txt format  
- 📈 **Built-in plotting** of behavioral metrics like d-prime and score distributions  
- 🧪 **Easily customizable** for different paradigms  
- 🔌 **Hardware integration** (e.g., Raspberrypi, TDT system)  

---

## Demo 🎥

> **Short video / GIF of the Educage in action goes here**

📷 Add a short GIF or link to a YouTube video that shows:
- A mouse interacting with the cage
- The software interface during an experiment  
- Real-time feedback or results display  

**Example**:  
![Educage in action](images/demo.gif)  
_or_  
[![Watch Demo Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

---

## Screenshots 🖼️

> Show how the GUI looks and how results are presented

- Experiment setup window  
  ![Setup Screenshot](images/setup_screenshot.png)

- Live data visualization  
  ![Graph Screenshot](images/graph_screenshot.png)

---

## Installation ⚙️

### Requirements
- Python 3.6–3.12  
- Tkinter  
- Pandas, Plotly, NumPy  
- TDT drivers (if using hardware)

### Installation

git clone https://github.com/YOUR_USERNAME/educage.git
cd educage
pip install -r requirements.txt
python main.py

---

### How to Use 🖱️

1. Launch the GUI: python main.py
2. Enter experiment parameters (e.g., Mouse ID, session type, number of trials).  
3. Start the session and monitor progress via the built-in graphs.  
4. Data is saved automatically to the `/data` folder in CSV format.  
5. Use the built-in visualizations to explore:
   - 🟦 Score distributions (bar chart)  
   - 📈 d-prime over time (line plot with sliding window of 20 trials)

---

### Contributing 🤝

We welcome contributions of all kinds:

- 🐛 Found a bug? Open an issue  
- 🌟 Got an idea? Start a discussion or pull request  
- 💬 Have questions? We'd love to hear from you  

> Please follow our [contribution guidelines](CONTRIBUTING.md) *(coming soon)*.

---

### License 📄

This project is licensed under the **MIT License**.  
See the [`LICENSE`](LICENSE) file for full details.

---

### Acknowledgements 🙏

- Developed at **[Your Lab Name]**, **[University Name]**
- Thanks to:
  - All the mice who participated in testing 🐭  
  - [Your PI or colleagues you want to mention]  
  - The open-source community ❤️  

---

> *Educage is a work in progress. Feedback, forks, and ideas are always welcome!*
