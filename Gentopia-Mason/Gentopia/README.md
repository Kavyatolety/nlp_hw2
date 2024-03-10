# Gentopia 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/gentopia)](https://pypi.org/project/gentopia/)
[![Read the Docs](https://img.shields.io/readthedocs/gentopia)](https://gentopia.readthedocs.io/en/latest/index.html)
[![Static Badge](https://img.shields.io/badge/GentPool-blue)](https://github.com/Gentopia-AI/GentPool)
[![Static Badge](https://img.shields.io/badge/backlog-pink)](https://github.com/orgs/Gentopia-AI/projects/1)
[![Open Issues](https://img.shields.io/github/issues-raw/Gentopia-AI/Gentopia)](https://github.com/Gentopia-AI/Gentopia/issues)
[![Dependency Status](https://img.shields.io/librariesio/github/Gentopia-AI/Gentopia)](https://libraries.io/github/Gentopia-AI/Gentopia)

[![Twitter Follow](https://img.shields.io/twitter/follow/GentopiaAI)](https://twitter.com/GentopiaAI)
[![](https://dcbadge.vercel.app/api/server/ASPP9MY9QK?compact=true&style=flat)](https://discord.gg/ASPP9MY9QK)
[![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/views/UC9QCjcsHJVKjKZ2Zmrq83vA)](https://www.youtube.com/channel/UC9QCjcsHJVKjKZ2Zmrq83vA)
[![GitHub star chart](https://img.shields.io/github/stars/Gentopia-AI/Gentopia?style=social)](https://star-history.com/Gentopia-AI/Gentopia)




Gentopia is a lightweight and extensible framework for LLM-driven [Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) and [ALM](https://arxiv.org/abs/2302.07842)  research. It provides essential components to build, test and evaluate agents. At its core, Gentopia aims to assemble an agent with a single config, thus minimizing your effort in building, tuning, and sharing agents. 

<img width="1140" alt="image" src="https://github.com/Gentopia-AI/Gentopia/assets/65674752/8cb8ec87-6e50-44d5-aedc-c4994e9a8aa2">


Gentopia maintains an agent platform [GentPool](https://github.com/Gentopia-AI/GentPool) to share specialized agents, where your agent *interacts* with other agents by cloning, hierarchical plug-in, or sharing environment. We provide a unique agent [benchmark](https://gentopia.readthedocs.io/en/latest/gentpool.html#agent-evaluation) for holistic evaluation. 

## Motivation 🧠
Agent practitioners start to realize the difficulty in tuning a "well-rounded" agent with tons of tools or instructions in a single layer.
Recent studies like [TinyStories](https://arxiv.org/abs/2301.12726), [Specializing Reasoning](https://arxiv.org/abs/2301.12726), [Let's Verify SbS](https://arxiv.org/abs/2305.20050), [ReWOO](https://arxiv.org/abs/2305.18323), etc. also point us towards an intuitive yet undervalued direction 👉 

```
An LLM is more capable if you create a context/distribution shift specialized to some target tasks.
```
Sadly, there is no silver bullet for agent specialization. For example, you can 
- Simply add `Let's think step by step.` in your **prompt** for more accurate Math QA.
- Give a **few-shot** exemplar in your prompt to guide a better reasoning trajectory for novel plotting.
- Supervise **fine-tuning** (SFT) your 70B `llama2` like [this](https://arxiv.org/abs/2305.20050) to match reasoning of 175B GPT-3.5.
- Tune your agent **paradigm** like this [demo](https://www.youtube.com/watch?v=diJ4IDaT4Z4) to easily half the execution time for Seach & Summarize.
- And more ...

Isn't it beautiful if one shares his effort in specialized intelligence, allowing others to reproduce, build on, or interact with it? 🤗 This belief inspires us to build Gentopia, 
**designed for agent *specialization, sharing, and interaction,* to stackingly achieve collective growth towards greater intelligence.**.

## Core Features 💡

- ⚙️ Config-driven agent assembling and chat.
- 🚀 Large amount of prebuilt agent types, LLM clients, tools, memory systems, and more.
- 🪶 Lightweight and highly extensible implementation of essential components.
- 🧪 Aligning with state-of-the-art AI research.
- 🤝 Enabling multi-agent interactions.
- 🦁 Unique platform of agent zoo and eval benchmark.

## Quick Start 🍏
```
conda create --name gentenv python=3.10
conda activate gentenv
pip install gentopia
```
or if you want to build with open LLMs locally 👉 `pip install gentopia[huggingface]`

First time to Gentopia? Grab a coffee ☕ and 

Take ~ 8 mins to check out the following demo tutorials [![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/views/UC9QCjcsHJVKjKZ2Zmrq83vA)](https://www.youtube.com/channel/UC9QCjcsHJVKjKZ2Zmrq83vA) 

<div style="display: flex; justify-content: space-around;">
  
<a href="https://www.youtube.com/watch?v=7dZ3ZvsI7sw" target="_blank">
  <img src="https://img.youtube.com/vi/7dZ3ZvsI7sw/hqdefault.jpg" alt="Video 1" style="width:32%;">
</a>

<a href="https://www.youtube.com/watch?v=XTsv9pk6AOA" target="_blank">
  <img src="https://img.youtube.com/vi/XTsv9pk6AOA/hqdefault.jpg" alt="Video 2" style="width:32%;">
</a>

<a href="https://www.youtube.com/watch?v=diJ4IDaT4Z4" target="_blank">
  <img src="https://img.youtube.com/vi/diJ4IDaT4Z4/hqdefault.jpg" alt="Video 3" style="width:32%;">
</a>

</div>

Or check out the [Quick Start](https://gentopia.readthedocs.io/en/latest/quick_start.html) Doc.

## Documentation 📖
See [here](https://gentopia.readthedocs.io/en/latest/index.html) for full documentation.

🌟 Highlight Topics 🌟 
- [🤖 Agent Templates](https://gentopia.readthedocs.io/en/latest/quick_start.html#vanilla-agent)
- [⛰️ Hierarchical Agents](https://gentopia.readthedocs.io/en/latest/agent_components.html#agent-as-plugin)
- [🥇 Unique Agent Benchmark](https://gentopia.readthedocs.io/en/latest/gentpool.html#agent-evaluation)
- [🦙 Open LLM Supports](https://gentopia.readthedocs.io/en/latest/agent_components.html#huggingface-open-llms)
- [🧠 High-Performance Memory](https://gentopia.readthedocs.io/en/latest/agent_components.html#long-short-term-memory)


## News 👷

**[Oct 7]** The companion paper was accepted by #EMNLP 23. See you in Singapore! 🦙🌎

**[Aug 6]** We've submitted our work as a paper for EMNLP 2023. Special thanks to the research [team](https://gentopia-ai.github.io/Gentopia-AI-Homepage/#about) and professors from NCSU, GMU, and CMU for collaboration :)

## Join us! 🌎

Participate in this Utopia of superintelligence and help it grows! As a fully open-source project, we develop under public advice, ideas, and supervision. Meanwhile, here are ways you may contribute to Gentopia.

- 🐛 Post an [issue](https://github.com/Gentopia-AI/Gentopia/issues) requesting necessary bug fixes, additional features, or roadmap suggestions. (Check closed ones first)
- 🎯 Our dev team meets weekly to groom [backlog](https://github.com/orgs/Gentopia-AI/projects/1) into tickets. While we work on them, you can pick up others and create a [Pull Request](https://github.com/Gentopia-AI/Gentopia/pulls) to request a merge. We always welcome new members in this way.
- 🤝 Share your specialized agent to [GentPool](https://github.com/Gentopia-AI/GentPool)! Create an Agent PR ([example]()) to merge your well-tuned agent into the pool. This allows others to use or build upon your agent. 
- ⭐ Help us spread! Give us a star, follow us on [Twitter](https://twitter.com/GentopiaAI), join our [Discord](https://discord.gg/ASPP9MY9QK), and share with your friends!


