# Siora — Context-Aware AI Learning Companion

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](#)
[![Manifest](https://img.shields.io/badge/Chrome_MV3-Compliant-success.svg)](#)
[![Backend](https://img.shields.io/badge/FastAPI-Production_Ready-009688.svg)](#)
[![Database](https://img.shields.io/badge/PostgreSQL-ACID_Persisted-336791.svg)](#)

> **Siora is an intelligent, context-aware AI learning companion embedded directly into the browser workflow.**  
> It dynamically perceives the active learning resource—understanding playback progression, video context, and student dialogue in real time—delivering zero-friction conceptual grounding without requiring users to manually copy, paste, or explain their learning material.

---

## 🎯 Executive Overview

Modern online learners lose significant cognitive momentum switching between educational content (lectures, tutorials, technical documentation) and external AI chat interfaces. Standard chatbots operate with complete blindness to the user's active viewport, requiring repetitive manual prompting and context setting.

**Siora eliminates this friction entirely.** Built on a high-performance Chrome Manifest V3 architecture and an enterprise-grade backend infrastructure, Siora establishes an intelligent, non-intrusive side-panel workspace that operates synchronously alongside the student's active study sessions.

---

## 💎 Core Capabilities & Value Proposition

### 1. Zero-Friction Context Awareness
- **Real-Time Viewport Telemetry:** Dynamically synchronizes with the active media player, tracking precise temporal playback, canonical resource identification, and live user interactions.
- **Asymmetric Context Ingestion:** Eliminates token bloat and latency spikes by surgically isolating and extracting high-signal narrative windows relevant to the student’s exact moment of inquiry.

### 2. Isolated Per-Tab Side Panel Architecture
- **Tab-Scoped Lifecycle Management:** Unlike conventional extensions that bleed across windows or force intrusive popups, Siora isolates state, memory, and UI lifecycle strictly to the target educational tab.
- **Synchronous Port Management:** Leverages persistent runtime connection channels for seamless session toggling, zero-latency state recovery, and automatic background cleanup.

### 3. Stateful Multi-Turn Conversational Memory
- **Relational Persistence Layer:** Backed by an ACID-compliant PostgreSQL relational core, ensuring student interactions, conceptual inquiries, and AI pedagogical responses survive browser and session restarts.
- **Chronological Dialogue Assembly:** Resolves complex conversational coreferences and follow-up inquiries through clean, isolated conversational state tracking.

### 4. High-Availability Resilient Inference Pipeline
- **Hierarchical Fallback Routing:** Enterprise-grade routing gateway designed to survive upstream provider rate limits, regional outages, or latency spikes through automatic multi-tier fallback orchestration.
- **Strict Role Separation & Prompt Hygiene:** Implements rigorous data-contract boundaries to prevent synthetic pattern leakage and guarantee hallucination-free output structure.

### 5. Secure & Performant Client Experience
- **Client-Side Sanitization:** Complete multi-stage parsing pipeline rendering mathematically clean technical markdown while neutralizing XSS vulnerabilities via enterprise DOM sanitization standards.
- **Adaptive Visual System:** Fully integrated CSS variable design engine supporting high-contrast light and dark study environments.

---

## 🏛️ High-Level Technical Stack

| Domain | Technologies |
| :--- | :--- |
| **Client Interface** | Chrome Manifest V3, ES Modules, Custom Design Tokens, Vite Engine |
| **Document Processing** | Marked.js, DOMPurify, Web Components |
| **Core Services** | Python 3.11+, FastAPI (Asynchronous ASGI Engine), Pydantic v2 |
| **Persistence & ORM** | PostgreSQL, SQLAlchemy 2.0 (Thread-pooled session factory) |
| **Network & Transport** | HTTP/2, Asynchronous HTTPX Client, Chrome Port Messaging Protocol |
| **Inference Gateway** | Multi-Tier Orchestration / OpenAI-Compatible Routing Layer |

---

## 🔒 Security & Proprietary Notice

Siora is a proprietary software product. This repository contains the source code for the client-facing browser integration and foundational service interface. Proprietary algorithmic models, context orchestration pipelines, adaptive learning engines, and internal infrastructure designs are strictly reserved.

---

## ⚖️ License & Rights

© 2026 Siora. All rights reserved. Unauthorized reproduction, distribution, reverse engineering, or commercial exploitation of this software and its proprietary components is strictly prohibited.
