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
* [2024/02/07] [🚀 OllaGen1 is Launched!](https://github.com/Cybonto/OllaBench/tree/main/OllaGen1)

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)

## Overview
The grand challenge that most CEO's care about is maintaining the right level of cybersecurity at a minimum cost as companies are not able to reduce cybersecurity risks despite their increased cybersecurity investments [[1]](https://www.qbusiness.pl/uploads/Raporty/globalrisk2021.pdf). Fortunately, the problem can be explained via interdependent cybersecurity (IC) [[2]](https://www.nber.org/system/files/working_papers/w8871/w8871.pdf) as follows. First, optimizing cybersecurity investments in existing large interdependent systems is already a well-known non-convex difficult problem that is still yearning for new solutions. Second, smaller systems are growing in complexity and interdependence. Last, new low frequency, near simultaneous, macro-scale risks such as global pandemics, financial shocks, geopolitical conflicts have compound effects on cybersecurity.

Human factors account for half of the long-lasting challenges in IC as identified by Kianpour et al. [[3]](https://www.mdpi.com/2071-1050/13/24/13677), and Laszka et al. [[4]](http://real.mtak.hu/21924/1/Buttyan4.pdf). Unfortunately, human-centric research within the context of IC is under-explored while research on general IC has unrealistic assumptions about human factors. Fortunately, the dawn of Large Language Models (LLMs) promise a much efficient way to research and develop solutions to problems across domains. In cybersecurity, the Zero-trust principles require the evaluation, validation, and continuous monitoring and LLMs are no exception.

Therefore, OllaBench was born to help both researchers and application developers conveniently evaluate their LLM models within the context of cybersecurity compliance or non-compliance behaviors.

OllaBench benchmark scripts and leaderboard results will be published later in FEB after I submit my entry into nVidia's Generative AI Developer Challenge. For now, please check out its Dataset Generator and sample Datasets at the [OllaGen1](https://github.com/Cybonto/OllaBench/tree/main/OllaGen-1) subfolder.

## Installation
### Step 1 - Windows Linux Subsystem
If you are using Windows, you need to install WSL. The Windows Subsystem for Linux (WSL) is a compatibility layer introduced by Microsoft that enables users to run Linux binary executables natively on Windows 10 and Windows Server 2019 and later versions. WSL provides a Linux-compatible kernel interface developed by Microsoft, which can then run a Linux distribution on top of it. See [here](https://learn.microsoft.com/en-us/windows/wsl/install) for information on how to install it. In this set up, we use Debian linux. You can check verify linux was installed by executing
`wsl -l -v`
You enter WSL by executing the command "wsl" from windows command line window.

Please disregard if you are using a linux system.

### Step 2a - Nvidia Container Toolkit
The NVIDIA Container Toolkit is a powerful set of tools that allows users to build and run GPU-accelerated Docker containers. It leverages NVIDIA GPUs to enable the deployment of containers that require access to NVIDIA graphics processing units for computing tasks. This toolkit is particularly useful for applications in data science, machine learning, and deep learning, where GPU resources are critical for processing large datasets and performing complex computations efficiently. Instalation instructions are in [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

Please disregard if your computer does not have a GPU.

### Step 2b.option1 - nVidia TensorRT-LLM
TensorRT-LLM provides users with an easy-to-use Python API to define Large Language Models (LLMs) and build TensorRT engines that contain state-of-the-art optimizations to perform inference efficiently on NVIDIA GPUs.
- LlamaIndex [Tutorial](https://docs.llamaindex.ai/en/stable/examples/llm/nvidia_tensorrt.html) on Installing TensorRT-LLM
- TensorRT-LLM Github [page](https://github.com/NVIDIA/TensorRT-LLM/blob/main/README.md)

### Step 2b.option2 - Ollama
- Install Docker Desktop and Ollama with these [instructions](https://github.com/ollama/ollama).

### Step 3 - Run OllaGen-1
Please go to [OllaGen1](https://github.com/Cybonto/OllaBench/tree/main/OllaGen-1) subfolder and follow the instructions to generate the evaluation datasets.

### Step 4 - Execute the OllaBench python script
tba
