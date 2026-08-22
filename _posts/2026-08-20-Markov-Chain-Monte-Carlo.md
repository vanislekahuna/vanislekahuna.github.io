---
layout: post
title: "Explaining Markov Chain Monte Carlo using Wildfire Forensics"
categories: [climate-ai]
---

A wildfire has burned overnight in a remote stretch of forest, and Prof. Markov has been called in to find out where it started. He has a burn map divided into a 5-by-5 grid (25 total cells), some historical records on lightning strikes and logging roads, and a single die with eight sides. That's it. No coordinates, no shortcuts, no way to survey the entire area all at once. However, what he does have is a procedure: At every cell, ask whether the next one over is more or less likely than where he's standing, and let that comparison do the rest after running for a hundred thousand iterations. By the end, the places he visited most often *are* the answers to his original question of where the fire started, down to a full probability distribution rather than a single guess.

That rule is the Metropolis algorithm, the oldest and simplest member of the Markov Chain Monte Carlo (MCMC) family, and it's the same one quietly running underneath a huge share of modern Bayesian computing. This article follows Prof. Markov's investigation step by step, using it as the scaffolding to build a working Metropolis sampler from scratch, watch it converge on a true posterior, and understand exactly what "sampling a distribution" means in practice. We'll also cover where this elegant 1953 algorithm starts to strain, and what a Canadian statistician named W.K. Hastings did to solve it seventeen years later.

**Topics Covered**

- Prof. Markov's wildfire investigation: Prior risk, burn-pattern likelihood, and the posterior he actually needs;
- Why computing that posterior directly is practically impossible, even on such a small grid;
- The three rules of the Metropolis algorithm illustrated by the die roll, the acceptance ratio, and the accept/reject decision;
- A full Python implementation of the sampler, run and visualized across the burnt grid;
- Reading a convergence plot and why the accumulated record of visited cells *is* the posterior;
- Where Metropolis breaks down: Concentration of measure, autocorrelation, and its symmetric proposal assumption;
- W.K. Hastings' 1970 generalization to asymmetric proposals and how a single loaded die illustrates exactly why it matters.

<!-- more -->


<iframe 
  src="https://nbviewer.org/github/vanislekahuna/wps-labs/blob/main/Bayesian_Wildfire_Stats_Lab/Explaining_Markov_Chain_Monte_Carlo.ipynb" 
  width="100%" 
  height="1200px" 
  frameborder="0"
    style="border: 1px solid var(--border-color); border-radius: 4px;">
  <!-- style="border: 1px solid #ccc; border-radius: 4px;"> -->
</iframe>

---

Click the Colab badge below to run the notebook interactively:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vanislekahuna/wps-labs/blob/main/Bayesian_Wildfire_Stats_Lab/Explaining_Markov_Chain_Monte_Carlo.ipynb)