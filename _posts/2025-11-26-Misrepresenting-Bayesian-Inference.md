---
layout: post
title: "Why Most Introductory Examples of Bayesian Statistics Misrepresent It"
categories: [climate-ai]
---

This notebook introduces the basic idea behind Bayes' Theorem and highlights some key differences between Bayesian Statistics and the widely taught traditional branch of statistics, commonly known as Frequentist Statistics. Furthermore we challenge the traditional medical testing example used in countless textbooks to introduce Bayesian Inference, arguing that using fixed constants (also known as point estimates) misrepresents the true nature of Bayesian Statistics. Rather than inputting single values in Bayes' Theorem, we utilize a more faithful Bayesian approach by considering probability distributions of possible outcomes, thus revealing how disease prevalence uncertainty affects diagnostic accuracy.

**Topics covered:**
- Bayes' Theorem fundamentals (priors, likelihood, posteriors)
- Contrasting Bayesian vs Frequentist interpretations of probability
- Critique of point estimates in introductory Bayesian examples
- Generating probability distributions for priors using `NumPy`
- Visualizing the relationship between prior and posterior distributions

<!-- more -->


<iframe 
  src="https://nbviewer.org/github/vanislekahuna/vanislekahuna.github.io/blob/test/notebooks/Misrepresenting-Bayesian-Inference.ipynb" 
  width="100%" 
  height="1200px" 
  frameborder="0"
    style="border: 1px solid var(--border-color); border-radius: 4px;">
  <!-- style="border: 1px solid #ccc; border-radius: 4px;"> -->
</iframe>

---

Click the Colab badge below to run the notebook interactively:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vanislekahuna/vanislekahuna.github.io/blob/test/notebooks/Misrepresenting-Bayesian-Inference.ipynb)