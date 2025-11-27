---
layout: post
title: "Playing With Fire and Priors: Learning the Limits of Bayesian Linear Regression with PyMC"
categories: [climate-ai]
---

This notebook demonstrates the complete workflow for building a Bayesian Simple Linear Regression model using `PyMC` to predict wildfire size from wind speed data. We formalize the model using statistical notation, implement prior predictive simulations to validate assumptions, and generate posterior distributions through Markov Chain Monte Carlo (MCMC) sampling. The analysis reveals that wind speed alone is a weak (really terrible) predictor of fire size but provides valuable lessons about model diagnostics including what happens when we violate assumptions of linearity and heteroscedasticity in real-world data.

**Topics covered:**
- Statistical model notation for Bayesian Linear Regression (priors, likelihood, parameters)
- Log transformations to handle right-skewed distributions
- Prior predictive simulation to validate parameter choices
- `PyMC` implementation with Normal and HalfNormal distributions
- MCMC sampling to generate posterior distributions
- Model evaluation through trace plots and regression line uncertainty
- Diagnosing assumption violations (homoscedasticity, linearity, heteroscedasticity)

<!-- more -->


<iframe 
  src="https://nbviewer.org/github/vanislekahuna/vanislekahuna.github.io/blob/test/notebooks/Bayesian_Simple_Linear_Regression_PyMC.ipynb" 
  width="100%" 
  height="1200px" 
  frameborder="0"
    style="border: 1px solid var(--border-color); border-radius: 4px;">
  <!-- style="border: 1px solid #ccc; border-radius: 4px;"> -->
</iframe>

---

Click the Colab badge below to run the notebook interactively:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vanislekahuna/vanislekahuna.github.io/blob/test/notebooks/Bayesian_Simple_Linear_Regression_PyMC.ipynb)