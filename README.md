# 💼 Salary Negotiation Simulator

> **Practice the conversation before the real conversation.**

<div align="center">

### 🚀 Live Demo

**https://salary-negotiation-simulator-nhdmgsuwnuxwjz2wt7sqys.streamlit.app/**

<br>

### 💻 Source Code

**https://github.com/Satyam0010/salary-negotiation-simulator**

</div>

---

## 📌 Project Overview

The **Salary Negotiation Simulator** is an AI-powered, interactive negotiation training platform built with **Streamlit, Python, and Google's Gemini API**.

The application simulates a realistic salary negotiation between a candidate and a strict HR manager. Instead of acting as a generic chatbot, Gemini is configured as a specialized HR negotiation engine that evaluates the candidate's arguments, challenges weak reasoning, considers evidence, and dynamically adjusts the simulated salary offer.

The simulator supports both:

- ⌨️ **Text-based negotiation**
- 🎙️ **Voice-based negotiation using microphone input**

The system maintains the complete negotiation context using Streamlit session state, allowing the conversation to continue across Streamlit reruns without losing the candidate's profile, negotiation history, current offer, or round information.

---

# 🎯 Problem Statement

Salary negotiation is an important professional skill, but students and early-career professionals often have limited opportunities to practice realistic negotiations before an actual interview or job offer.

Traditional preparation methods generally involve:

- Reading negotiation guides
- Watching interview videos
- Practicing with friends
- Memorizing negotiation strategies

These methods do not provide an interactive environment where the user can repeatedly negotiate against a challenging and adaptive HR manager.

### The Salary Negotiation Simulator solves this problem by providing:

> **A controlled AI-powered environment where users can practice salary negotiations, receive realistic HR responses, and improve their negotiation strategy before facing a real employer.**

The official capstone problem statement specifies a voice-driven salary negotiation simulator in which the AI plays the role of a strict HR manager while the user practices negotiating a **₹96,400 salary**.

---

# 🚀 Key Features

## 1. 👤 Candidate Profile

Users can configure their negotiation profile before starting the simulation.

The profile includes:

- Candidate name
- Job role
- Years of experience
- Current / previous salary
- Minimum acceptable salary
- Target salary
- Key skills
- Major achievements
- Negotiation evidence

The target salary is based on the capstone problem statement:

> **₹96,400 per month**

---

## 2. 🧠 AI-Powered HR Manager

Gemini acts as a specialized HR manager rather than a generic conversational assistant.

The AI receives dynamic negotiation context including:

- Candidate profile
- Current salary
- Target salary
- Minimum acceptable salary
- Current HR offer
- Current negotiation round
- Candidate's skills
- Candidate's achievements
- Negotiation evidence
- Previous conversation
- Latest candidate response
- Negotiation difficulty
- Negotiation style

This allows the HR manager to respond according to the actual conversation.

---

## 3. 💬 Interactive Text Negotiation

Users can negotiate directly through a text input.

Example:

```text
Candidate:
"I am targeting ₹96,400 because my technical experience,
project work, and ability to contribute immediately justify
the compensation."

HR Manager:
"I understand your target. However, I need stronger
evidence of measurable impact before moving further."