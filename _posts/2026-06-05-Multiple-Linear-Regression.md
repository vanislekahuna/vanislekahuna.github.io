---
layout: post
title: "Putting DAGs to the Test: What Regression Reveals about Wildfire Drivers (Part 2)"
categories: [climate-ai]
---

This article puts the hypothesized causal DAG from Part 1 to the test by fitting 
various Multiple Linear Regression models to ~4,000 large BC wildfires (>100 hectares) and 
examining whether the atmospheric relationships we drew actually hold up in the data. 
Before the main analysis, we take a pedagogical detour through Bayesian Multiple 
Linear Regression using `PyMC` to demonstrate what happens when weakly informative 
priors meet a large dataset and why that finding justifies switching to simpler 
Frequentist methods for the rest of the analysis. The honest result: Our final model 
explains roughly 11% of variance in fire size, which sounds underwhelming until you 
consider what that 11% actually represents. Two of our hypothesized mediators don't 
survive contact with the data, and our revised DAG is far better for it.

**Topics covered:**
- Bayesian Multiple Linear Regression with `PyMC` along with other Bayesian techniques like prior specification, prior predictive simulation, and posterior estimation
- Forest plots and posterior predictive plots for Bayesian model evaluation
- Correlation matrix analysis for detecting multicollinearity among atmospheric predictors
- Pooled vs. zone-stratified regression and why separating BC fire zones nearly doubles model performance (R² = 0.067 → 0.117)
- Standardized coefficient heatmaps for comparing predictor effects across geographic zones
- Using multiple lines of evidence (correlation, coefficient instability, R² comparison) to identify redundant mediators without formal VIF testing

<!-- more -->


<iframe 
  src="https://nbviewer.org/github/vanislekahuna/vanislekahuna.github.io/blob/master/notebooks/%5BPart_2%5DPutting_DAGs_to_the_Test_What_Regression_reveals_about_Wildfire_Drivers.ipynb" 
  width="100%" 
  height="1200px" 
  frameborder="0"
    style="border: 1px solid var(--border-color); border-radius: 4px;">
  <!-- style="border: 1px solid #ccc; border-radius: 4px;"> -->
</iframe>

---

Click the Colab badge below to run the notebook interactively:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vanislekahuna/vanislekahuna.github.io/blob/master/notebooks/%5BPart_2%5DPutting_DAGs_to_the_Test_What_Regression_reveals_about_Wildfire_Drivers.ipynb)