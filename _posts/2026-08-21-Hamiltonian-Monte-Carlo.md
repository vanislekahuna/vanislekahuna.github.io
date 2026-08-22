---
layout: post
title: "Reverse-Engineering Hamiltonian Monte Carlo: The MCMC Engine Behind Modern Bayesian Inference"
categories: [climate-ai]
---

Every time a Bayesian model gets fit in PyMC, the Hamiltonian Monte Carlo algorithm (HMC) is quietly doing the work behind the scenes of simulating a physical particle moving across a probability landscape to generate a posterior distribution, all without ever needing to compute that distribution directly. This article takes that machine apart. Building on our earlier article covering the foundational Markov Chain Monte Carlo (MCMC) and it's original variant - the Metropolis-Hastings algorithm, we trace the specific limitations that made HMC necessary then reconstruct it piece by piece. Our tour of HMC starts with the negative log-posterior function that defines the landscape, the gradient function that acts as gravity pulling the particle toward high-probability regions, before concluding with the leapfrog integration settings that govern how far the particle travels before a sample gets recorded. Along the way, we confront the U-turn problem that plagues poorly-tuned HMC and see how the No-U-Turn Sampler (NUTS) solves it automatically. Rather than applying this innovation on toy problems, we do the opposite by utilizing them in a complex Hierarchical Multi-Level Bayesian Regression model designed to estimate wildfire size across British Columbia's Fire Centre zones to demonstrate how the same skeleton powering a two-parameter demonstration scales, largely unchanged, to a model with dozens of parameters. By the end of it, we'll find that the black box behind `pymc.sample()` is a black box to us no longer.

**Topics Covered**

- A quick review of the Metropolis-Hastings algorithm and where it hits a scaling wall;
- The physical intuition behind Hamiltonian Monte Carlo and how it leverages gradient information to turn a blind random walk into a directed exploration of the posterior;
- How to construct a negative log-posterior function ("the landscape") for models of arbitrary complexity, from a simple two-parameter model to a full Hierarchical Bayesian Regression;
- How to compute the gradient of that function ("the gravity") and why it's the key ingredient that makes HMC efficient;
- The leapfrog steps and step size which are the two settings controlling how far Hamiltonian particle travels before a sample is recorded;
- The U-turn problem and how the No-U-Turn Sampler (NUTS) solves it adaptively;
- Assembling all five components into a complete, working `Hamiltonian_Monte_Carlo()` sampler built from scratch;
- Diagnosing sampler health using trace plots;
- A real-world application where it's used to sample a complex Hierarchical Bayesian Regression model of wildfire size across BC's Fire Centre zones.

<!-- more -->


<iframe 
  src="https://nbviewer.org/github/vanislekahuna/wps-labs/blob/main/Bayesian_Wildfire_Stats_Lab/Reverse_Engineering_Hamiltonian_Monte_Carlo.ipynb" 
  width="100%" 
  height="1200px" 
  frameborder="0"
    style="border: 1px solid var(--border-color); border-radius: 4px;">
  <!-- style="border: 1px solid #ccc; border-radius: 4px;"> -->
</iframe>

---

Click the Colab badge below to run the notebook interactively:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vanislekahuna/wps-labs/blob/main/Bayesian_Wildfire_Stats_Lab/Reverse_Engineering_Hamiltonian_Monte_Carlo.ipynb)