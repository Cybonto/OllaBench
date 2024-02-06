
<div align="center">

OllaGen1
===========================
<h4> OllaBench Generator 1 - Generating Cognitive Behavioral QA for Cybersecurity</h4>

[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)]()
[![python](https://img.shields.io/badge/python-3.10-green)]()
[![Static Badge](https://img.shields.io/badge/release-0.1-green?style=flat&color=green)]()
[![license](https://img.shields.io/badge/license-Apache%202-blue)](./LICENSE)

---
<div align="left">

## Latest News
* [2024/02/07] [🚀 OllaGen1 is Launched!](https://github.com/Cybonto/OllaBench/tree/main/OllaGen1)

## Table of Contents

- [OllaGen1 Overview](#ollagen1-overview)
- [Installation](#installation)
- [Methodology](#methodology)
- [Troubleshooting](#troubleshooting)
- [Release notes](#release-notes)
  - [Change Log](#change-log)
  - [Known Issues](#known-issues)
  - [Report Issues](#report-issues)
 
## OllaGen1 Overview
The grand challenge that most CEO's care about is maintaining the right level of cybersecurity at a minimum cost as companies are not able to reduce cybersecurity risks despite their increased cybersecurity investments [[1]](https://www.qbusiness.pl/uploads/Raporty/globalrisk2021.pdf). Fortunately, the problem can be explained via interdependent cybersecurity (IC) [[2]](https://www.nber.org/system/files/working_papers/w8871/w8871.pdf) as follows. First, optimizing cybersecurity investments in existing large interdependent systems is already a well-known non-convex difficult problem that is still yearning for new solutions. Second, smaller systems are growing in complexity and interdependence. Last, new low frequency, near simultaneous, macro-scale risks such as global pandemics, financial shocks, geopolitical conflicts have compound effects on cybersecurity.

Human factors account for half of the long-lasting challenges in IC as identified by Kianpour et al. [[3]](https://www.mdpi.com/2071-1050/13/24/13677), and Laszka et al. [[4]](http://real.mtak.hu/21924/1/Buttyan4.pdf). Unfortunately, human-centric research within the context of IC is under-explored while research on general IC has unrealistic assumptions about human factors. Fortunately, the dawn of Large Language Models (LLMs) promise a much efficient way to research and develop solutions to problems across domains. In cybersecurity, the Zero-trust principles require the evaluation, validation, and continuous monitoring and LLMs are no exception.

Therefore, OllaGen1 was born to help both researchers and application developers conveniently evaluate their LLM models within the context of cybersecurity compliance or non-compliance behaviors. For immediate evaluation, there are three QA data (sub)sets of "True or False", "Which Cognitive Path", and "Who is who", all of which will be described in further details. For more flexibility, OllaGen1 dataset generator is included and allows for generation of new realistic grounded QA entries, guaranteeing robust LLM evaluation.

## Installation
The datasets are in .csv format with data fields of ID (question id), Context (describing the cognitive behavior details relating to the context of cybersecurity compliance or non-compliance), Question, and Answer (the correct reference). To import CSV files into a Python script, a few key components are generally required. First, you need to use the csv module that comes built into Python, which provides functionality to both read from and write to CSV files. To read a CSV file, you typically start by opening the file using the open() function with the appropriate file path and mode ('r' for reading). Then, you can use csv.reader() to create a reader object that allows you to iterate over the rows of the CSV file. You will then need to give the LLM model the Context and the Question as a prompt. After the model returns its answer, you compare that answer with the correct reference to decide whether the model's response is correct. A grader script will be provided for your convenience.

If you want to generate new (never before seen) questions you first need to make sure the following main libraries are installed in your python environment.
- datetime, random
- itertools
- copy
- pandas
- matplotlib
- csv
- json
- networkx

The codes were tested in Python 3.12 but it should run in older Python environments. The next step is modify the params.json to your specifications.
- node_path: the path to the list of Cybonto Gen1 knowledge nodes
- edge_path: the path to the list of Cybonto Gen1 knowledge edges
- dict_path: the path to the list of Cybonto Gen1 prompt templates. Please do not change the content of this file.
- QA_TF_questions: the maximum number of True/False questions to be generated
- QA_TF_coglength: the length of the cognitive behavioral path to be used in generating the context. 4 is the recommended number.
- QA_TF_outpath: the location where the generated questions will be saved
- QA_WCP_questions: the maximum number of "Which Cognitive Path" questions to be generated
- QA_WCP_coglength: the length of the cognitive behavioral path to be used in generating the context. 4 is the recommended number.
- QA_WCP_outpath: the location where the generated questions will be saved
- QA_WHO_questions: the maximum number of "Who is who" questions to be generated
- QA_WHO_outpath: the location where the generated questions will be saved

Finally, you run the OllaGen1.py to generate the dataset.
  
## Methodology
Scientific methods were used to ensure grounded and realistic generation of the dataset. 

First, 108 psychology constructs and thousands of related paths based on 20 time-tested psychology theories were packaged as Cybonto—a novel ontology. This work was peer-reviewed and published at [https://xmed.jmir.org/2022/2/e33502/](https://xmed.jmir.org/2022/2/e33502/).
![The Cybonto Cognitive Behavioral Network](https://github.com/Cybonto/OllaBench/assets/83996716/d42124ad-4682-4074-b7e5-b2c0c09721d9)

Then, certain nodes and edges that fit the context of cybersecurity compliance and non-compliance were selected.
![The Cybonto-Gen1 Knowledge Graph](https://github.com/Cybonto/OllaBench/assets/83996716/b5a10ddf-1b97-4f48-8a8e-018bb1368ff0)

The edges were double checked by citations of empirical peer-reviewed [evidences](./references). Based on this knowledge graph and specified parameters, cognitive behavioral paths are created. For each cognitve behavioral path, a prompt will be constructed based on a library of manually designed and verified prompt templates. The final prompt will be used with ChatGPT or any of LLM models to generate the Context. The Answer (the correct reference) values are derived from the cogniive behavioral paths and the engineering of the context. Please refer to the generate datasets for specific examples.

## Troubleshooting
Codes were verfied to be running properly. If you run into issues, please first make sure that you have all dependencies installed. If you use online LLMs to generate new datasets, please make sure you have the API key(s) imported properly into your environment. Some online LLM providers will terminate/thorttle the LLM API performance by the "request per minute" rate which can cause the script to crash or run slower than expected. 

## Release notes

  * Version 0.1 is the initial version with some parts being under-developed.

### Known Issues

  * LLMs may not return responses in the expected format although the reponses may be correct. Please feel free to modify the question template as needed. However, due to the flexible nature of LLM responses, there is always a chance a response is not in the expected format.
  * Some LLMs may provide wrong answers to the same question if you as them the same questions repeatedly. It could be a programmed "trick" from the LLM maker meaning if you ask a question the first time (and the LLM provided you with a correct answer) and you ask the same question again, the LLM may think that you did not like the first answer and will try to pick a different answer.

### Report Issues

You can use GitHub issues to report issues and I will fix the issues that are on my end and may try to use prompt engineering to fix issues that are on the LLMs' end.
