# Basic Steps for Running LLMs on Local Machines
This guide uses some texts from the official Docker Desktop [docs](https://docs.docker.com/desktop/) and Ollama [docs](https://github.com/jmorganca/ollama/tree/main/docs).

## Install Docker
Docker Desktop is a one-click-install application for your Mac, Linux, or Windows environment that lets you to build, share, and run containerized applications and microservices. It provides a straightforward GUI (Graphical User Interface) that lets you manage your containers, applications, and images directly from your machine. You can use Docker Desktop either on its own or as a complementary tool to the CLI.
Before you install Docker for Desktop, please make sure you have a decent disk space for the models and configure the best internal drive as the location for Docker images. As we progress, LLM models will be pulled into the Ollama image. The size for a small model is around 5Gb while that of the biggest models can be more than 100Gb.
* Installation Guide for [WINDOWS](https://docs.docker.com/desktop/install/windows-install/).
* Installation Guide for [MAC](https://docs.docker.com/desktop/install/mac-install/).
* Installation Guide for [LINUX](https://docs.docker.com/desktop/install/linux-install/).

Make sure you allocate the best resource to Docker (i.e more system RAM), please follow the [Change Setting guide](https://docs.docker.com/desktop/settings/windows/) for Windows, Mac, and Linux.

Upon successful installation, you should be able to launch the Docker Desktop dashboard and it looks like this

![Docker Desktop Dashboard](https://github.com/Cybonto/OllaBench/assets/83996716/b1e853b3-43af-4a4a-81df-a68fd44602c3)

## Install Ollama
Ollama allows you to manage and run LLMs locally. The easiest way to install Ollama is to use the dashboard to search for the official Docker Sponsored Ollama. You look for the search bar (top middle of the dashboard), search for "ollama", and when the image is found, you click "pull".

More details on different ways to install Ollama and advanced configurations can be found at [Ollama on Docker Hub](https://hub.docker.com/r/ollama/ollama) page.

After installing Ollama, verify that Ollama is running by accessing the following link in your web browser: http://127.0.0.1:11434/. Note that the port number may differ based on your system configuration.

## About OpenSource Models
A full list of currently supported LLM models is in [here](https://ollama.ai/library). This project's model families of interests are:
### Llama2
Llama 2 is released by Meta Platforms, Inc. This model is trained on 2 trillion tokens, and by default supports a context length of 4096. Llama 2 Chat models are fine-tuned on over 1 million human annotations, and are made for chat.
### Mistral
Mistral 7B model is an Apache licensed 7.3B parameter model. It is available in both instruct (instruction following) and text completion.
### Orca2
Orca 2 is built by Microsoft research, and are a fine-tuned version of Meta's Llama 2 models. The model is designed to excel particularly in reasoning. 
### Falcon
A large language model built by the Technology Innovation Institute (TII) for use in summarization, text generation, and chat bots. The biggest Falcon model has 180b parameters.

## Pull the Models
A light-weight approach to interacting with Ollama is by using the integrated Docker Desktop command line interface. From the dashboard, you locate the running Ollama instance. Click on the three vertical dots in the right side of the instance row and choose "Open in terminal". More details can be found at [this blog post] (https://www.docker.com/blog/integrated-terminal-for-running-containers-extended-integration-with-containerd-and-more-in-docker-desktop-4-12/)

Once you are in the terminal, you can start pulling the models you want to use. For example:
```
Ollama pull llama2:7b
Ollama pull llama2:13b
Ollama pull llama2:70b
Ollama pull falcon:180b
Ollama pull orca2:13b
```
It will take a while to download a big model.

List models
```
ollama list
```

To remove a pulled model
```
ollama rm llama2:7b
```

## Run the Models
```
ollama run llama2:7b
```

For multiline input, wrap text with `"""`:
```
>>> """Hello,
... world!
... """

Pass in prompt as arguments
```
$ ollama run llama2 "Summarize this file: $(cat README.md)"
```

