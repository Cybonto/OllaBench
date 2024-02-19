<div align="center">

![image](https://github.com/Cybonto/OllaBench/assets/83996716/ea27ca1c-aad4-4d1e-8e42-73d071a02538)

<h4> Evaluating LLMs' Cognitive Behavioral Reasoning for Cybersecurity</h4>

[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)]()
[![python](https://img.shields.io/badge/python-3.10-green)]()
[![Static Badge](https://img.shields.io/badge/release-0.1-green?style=flat&color=green)]()
[![license](https://img.shields.io/badge/license-Apache%202-blue)](./LICENSE)

---
<div align="left">

## Latest News
* [2024/02/19] Created DEV folder to support further development

## Table of Contents
- [Overview](#overview)
- [Tested System Settings](#tested-system-settings)
- [Development Agenda](#development-agenda)

## Overview
Fellow developers. In this folder, you will find Jupyter notebooks to help with your custom development needs. The first cell allows you to export the production-ready codes to a .py file. All non-production codes should be in cells tagged with `dev_only` and these cells will not be exported to the .py file. Unit test can be done within the jupyter notebooks using DocTest library. I wanted OllaBench to be as light and as easy to use as possible. However, please feel free to clone, extend, and integrate to bigger systems per your needs. Happy Coding!


![OllaBench-Flows](https://github.com/Cybonto/OllaBench/assets/83996716/e001451d-9978-4de1-b35c-7eaad3602f22)


## Tested System Settings
The following tested system settings show successful operation for running OllaGen1 dataset generator and OllaBench.
- Primary Generative AI model: Llama2
- Python version: 3.10
- Windows version: 11
- GPU: nvidia geforce RTX 3080 Ti
- Minimum RAM: [your normal ram use]+[the size of your intended model]
- Disk space: [your normal disk use]+[minimum software requirements]+[the size of your intended model]
- Minimum software requirements: nvidia CUDA 12 (nvidia CUDA toolkit), 
- Additional system requirements:

## Development Agenda
Here is my tentative milestones in temporal order.
- Release a white paper detailing the scientific rigor behind OllaBench
- Release version 0.2 of OllaGen with at least 5 more new question types
- Release version 0.2 of OllaBench with upgraded and more rigorous benchmark mechanism
- Release OllaBench Leaderboard and related dataset
- Release version 0.1 of OllaGen-RAG
