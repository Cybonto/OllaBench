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
- [Quick Start](#quick-start)
- [Installation](#installation)

## Overview
The grand challenge that most CEO's care about is maintaining the right level of cybersecurity at a minimum cost as companies are not able to reduce cybersecurity risks despite their increased cybersecurity investments [[1]](https://www.qbusiness.pl/uploads/Raporty/globalrisk2021.pdf). Fortunately, the problem can be explained via interdependent cybersecurity (IC) [[2]](https://www.nber.org/system/files/working_papers/w8871/w8871.pdf) as follows. First, optimizing cybersecurity investments in existing large interdependent systems is already a well-known non-convex difficult problem that is still yearning for new solutions. Second, smaller systems are growing in complexity and interdependence. Last, new low frequency, near simultaneous, macro-scale risks such as global pandemics, financial shocks, geopolitical conflicts have compound effects on cybersecurity.

Human factors account for half of the long-lasting challenges in IC as identified by Kianpour et al. [[3]](https://www.mdpi.com/2071-1050/13/24/13677), and Laszka et al. [[4]](http://real.mtak.hu/21924/1/Buttyan4.pdf). Unfortunately, human-centric research within the context of IC is under-explored while research on general IC has unrealistic assumptions about human factors. Fortunately, the dawn of Large Language Models (LLMs) promise a much efficient way to research and develop solutions to problems across domains. In cybersecurity, the Zero-trust principles require the evaluation, validation, and continuous monitoring and LLMs are no exception.

Therefore, OllaBench was born to help both researchers and application developers conveniently evaluate their LLM models within the context of cybersecurity compliance or non-compliance behaviors.


> [!IMPORTANT]
> Dataset Generator and test Datasets at the [OllaGen1](https://github.com/Cybonto/OllaBench/tree/main/OllaGen-1) subfolder.
> You need to have either a local LLM stack (nvidia TensorRT-LLM with Llama_Index in my case) or OpenAI api key for generating new OllaBench datasets. Please note that OpenAI throttle Requests per Minutes which may cause significant delays depending on how big will your desired datasets be.
> When OllaBench white paper is published (later in FEB), OllaBench benchmark scripts and leaderboard results will be made available.


![OllaBench-Flows](https://github.com/Cybonto/OllaBench/assets/83996716/e001451d-9978-4de1-b35c-7eaad3602f22)


## Quick Start
### Evaluate with your own codes
You can grab the [evaluation datasets](https://github.com/Cybonto/OllaBench/tree/main/OllaGen-1) to run with your own evaluation codes. Note that the datasets (csv files) are for zero-shot evaluation. It is recommended that you modify the OllaBench Generator 1 (OllaGen1) params.json with your desired specs and run the OllaGen1.py to generate for yourself fresh, UNSEEN datasets that match your custom needs. Check OllaGen-1 README for more details.
### Use OllaBench
OllaBench will evaluate your models within Ollama model zoo using OllaGen1 default datasets. You can quickly spin up Ollama with Docker desktop/compose and download LLMs to Ollama. Please check the below [Installation](#installation) section for more details.
### Tested System Settings
The following tested system settings show successful operation for running OllaGen1 dataset generator and OllaBench.
- Primary Generative AI model: Llama2
- Python version: 3.10
- Windows version: 11
- GPU: nvidia geforce RTX 3080 Ti
- Minimum RAM: [your normal ram use]+[the size of your intended model]
- Disk space: [your normal disk use]+[minimum software requirements]+[the size of your intended model]
- Minimum software requirements: nvidia CUDA 12 (nvidia CUDA toolkit), 
- Additional system requirements:
### Quick Install of Key Components
This quick install is for a single Windows PC use case (without Docker) and for when you need to use OllaGen1 to generate your own datasets. I assume you have nvidia GPU installed.\
- Go to [TensorRT-LLM for Windows](https://github.com/NVIDIA/TensorRT-LLM/blob/main/windows/README.md) and follow the Quick Start section to install TensorRT-LLM and the prerequisites.
- If you plan to use OllaGen1 with local LLM, go to [Llama_Index for TensorRT-LLM](https://docs.llamaindex.ai/en/stable/examples/llm/nvidia_tensorrt.html) and follow instrucitons to install Llama_Index, and prepare models for TensorRT-LLM
- If you plan to use OllaGen1 with OpenAI, please follow OpenAI's intruction to add the api key into your system environment. You will also need to change the llm_framework param in OllaGen1 params.json to "openai".

### Commands to check for key software requirements
**Python**
`python -V`
**nvidia CUDA 12**
`nvcc -V`
**Microsoft MPI***
`mpiexec -hellp`

## Installation
The following instructions are mainly for the Docker use case.
### Windows Linux Subsystem
If you are using Windows, you need to install WSL. The Windows Subsystem for Linux (WSL) is a compatibility layer introduced by Microsoft that enables users to run Linux binary executables natively on Windows 10 and Windows Server 2019 and later versions. WSL provides a Linux-compatible kernel interface developed by Microsoft, which can then run a Linux distribution on top of it. See [here](https://learn.microsoft.com/en-us/windows/wsl/install) for information on how to install it. In this set up, we use Debian linux. You can check verify linux was installed by executing
`wsl -l -v`
You enter WSL by executing the command "wsl" from windows command line window.

Please disregard if you are using a linux system.

### Nvidia Container Toolkit
The NVIDIA Container Toolkit is a powerful set of tools that allows users to build and run GPU-accelerated Docker containers. It leverages NVIDIA GPUs to enable the deployment of containers that require access to NVIDIA graphics processing units for computing tasks. This toolkit is particularly useful for applications in data science, machine learning, and deep learning, where GPU resources are critical for processing large datasets and performing complex computations efficiently. Instalation instructions are in [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

Please disregard if your computer does not have a GPU.

### nVidia TensorRT-LLM
TensorRT-LLM provides users with an easy-to-use Python API to define Large Language Models (LLMs) and build TensorRT engines that contain state-of-the-art optimizations to perform inference efficiently on NVIDIA GPUs.
- LlamaIndex [Tutorial](https://docs.llamaindex.ai/en/stable/examples/llm/nvidia_tensorrt.html) on Installing TensorRT-LLM
- TensorRT-LLM Github [page](https://github.com/NVIDIA/TensorRT-LLM/blob/main/README.md)

### Ollama
- Install Docker Desktop and Ollama with these [instructions](https://github.com/ollama/ollama).

### Run OllaGen-1
Please go to [OllaGen1](https://github.com/Cybonto/OllaBench/tree/main/OllaGen-1) subfolder and follow the instructions to generate the evaluation datasets.

### Execute the OllaBench python script
tba
