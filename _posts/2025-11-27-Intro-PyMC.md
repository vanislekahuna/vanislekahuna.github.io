---
layout: post
title: "An Intro to PyMC and the Language for Describing Statistical Models"
categories: [climate-ai]
---

This notebook introduces the language of statistical model notation used to describe Bayesian models, demonstrating how mathematical notation translates directly into executable `PyMC` code. Using a real-world example of Vancouver Island Coastal Wolves (a recently discovered subspecies known for displaying distinguished behaviour from other wolf populations such the ability to swim great distances or the significant prevelance of marine organisms in their diet), we build a Bayesian model to estimate gender ratios from limited sample data to emphasize how posterior distributions reveal the full range of plausible outcomes rather than single point estimates.

**Topics covered:**
- Statistical model notation fundamentals (stochastic relationships, parameters vs data)
- Translating model notation into `PyMC` syntax (`pm.Uniform`, `pm.Binomial`, `pm.sample`)
- Understanding posterior distributions as ranked plausibilities
- Visualizing uncertainty with `ArviZ` trace plots and HDI intervals
- Prior predictive simulations with binomial and uniform distributions

<!-- more -->


<iframe 
  src="https://nbviewer.org/github/vanislekahuna/vanislekahuna.github.io/blob/test/notebooks/Vancouver_Island_Coastal_Wolves.ipynb" 
  width="100%" 
  height="1200px" 
  frameborder="0"
    style="border: 1px solid var(--border-color); border-radius: 4px;">
  <!-- style="border: 1px solid #ccc; border-radius: 4px;"> -->
</iframe>

---

Click the Colab badge below to run the notebook interactively:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vanislekahuna/vanislekahuna.github.io/blob/test/notebooks/Vancouver_Island_Coastal_Wolves.ipynb)