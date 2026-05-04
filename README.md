# 🚀 LinkedIn Auto Job Applier AI

<p align="center">
  <b>AI-powered LinkedIn Easy Apply automation tool with smart filtering, anti-detection, and real-time dashboard</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" />
  <img src="https://img.shields.io/badge/Automation-AI-green" />
  <img src="https://img.shields.io/badge/Platform-LinkedIn-blue" />
  <img src="https://img.shields.io/badge/License-MIT-orange" />
</p>

---

## 🔥 Overview

**LinkedIn Auto Job Applier AI** is a powerful automation tool that helps you **search, filter, and apply to LinkedIn Easy Apply jobs automatically** using AI.

It mimics real human behavior, avoids bot detection, and intelligently answers job application questions using LLMs like **OpenAI** and **Google Gemini**.

---

## ✨ Key Features

### 🤖 Automated Easy Apply Engine

* Multi-step job application automation
* Handles all form elements:

  * Dropdowns
  * Radio buttons
  * Checkboxes
  * Text inputs

---

### 🧠 AI-Based Answer Generation

* Uses **OpenAI / Gemini APIs**
* Auto-generates answers for unknown questions
* Context-aware responses using your resume

---

### 🛡️ Anti-Bot Detection System

* Powered by `undetected-chromedriver`
* Human-like interaction simulation:

  * Typing delays
  * Mouse movements
  * Scroll randomness
* Persistent sessions (no repeated logins)

---

### 🎯 Smart Job Filtering

* Skip irrelevant jobs automatically:

  * Experience mismatch
  * Blacklisted keywords
  * Security clearance roles

---

### 🔄 UI Resilience Layer

* Handles LinkedIn UI changes
* Safe DOM interactions
* PyAutoGUI fallback for edge cases

---

### 📊 Real-Time Dashboard

* Built with Flask
* Track:

  * Applications
  * Success rate
  * Job stats

---

## 📸 Demo (Optional)

> Add screenshots or GIF here for better engagement

---

## ⚡ Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/linkedin-auto-job-applier-ai.git
cd linkedin-auto-job-applier-ai
```

### 2. Setup Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

### 3. Install Dependencies

```bash
pip install .
```

---

## ⚙️ Configuration Guide

Configure files inside `config/`:

| File           | Purpose                |
| -------------- | ---------------------- |
| `secrets.py`   | Credentials & API keys |
| `personals.py` | Personal details       |
| `search.py`    | Job filters & keywords |
| `questions.py` | Predefined answers     |
| `settings.py`  | Bot limits & delays    |

⚠️ Never commit `secrets.py`

---

## ▶️ Usage

### Run Bot

```bash
python main.py
```

### Run Dashboard

```bash
python web_server.py
```

Open: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🏗️ Project Structure

```
src/
├── browser/      # Automation & scraping
├── core/         # Main engine
├── ai/           # LLM integration
├── data/         # Storage layer
```

---

## 🚀 SEO Keywords (for discoverability)

LinkedIn automation bot, LinkedIn Easy Apply bot, AI job applier, job automation tool, OpenAI job bot, Gemini AI automation, Python job bot, LinkedIn scraper bot, auto apply jobs LinkedIn

---

## ⚠️ Disclaimer

This project is for **educational purposes only**.

* May violate LinkedIn Terms of Service
* Use at your own risk
* Avoid aggressive automation

---

## 🤝 Contributing

Contributions are welcome!

```bash
# Fork the repo
# Create your branch
git checkout -b feature/your-feature

# Commit changes
git commit -m "Add feature"

# Push
git push origin feature/your-feature
```

---

## ⭐ Support

If this project helps you:

* ⭐ Star the repo
* 🍴 Fork it
* 📢 Share it

---

## 👨‍💻 Author

**Ajinkya Kardile**

---

## 📜 License

MIT License
