---
layout: post
title: "Rethinking Predictors: Why Causal Reasoning Matters in Data Science (Part 1)"
categories: [climate-ai]
---

This article makes the case for causal inference as a framework for thinking more 
deliberately about the models we build and the predictors we choose. Using multiple 
linear regression as our primary analytical lens, we introduce the core ideas behind 
causal reasoning, such as the data generating processes, mediators, confounding variables, and 
spurious correlations, and apply them to a real dataset of large BC wildfires (>100 
hectares). The analysis culminates in a hypothesized causal DAG mapping the atmospheric 
conditions we believe drive wildfire size, which we'll formally test with regression 
in Part 2. Spoiler: not every arrow in our DAG will survive contact with the data, 
and that's precisely the point.

**Topics covered:**
- Data generating processes (DGPs) and why thinking about them changes how you model
- Why adding more predictors can make your model less useful, not more
- Mediators and how including them can obscure the relationships you're actually trying to estimate
- Multicollinearity and why it makes individual coefficient estimates unreliable
- Confounding variables and spurious correlations exposed through multiple linear regression
- One-hot encoding of categorical variables (fire cause: lightning, person, unknown)
- Directed Acyclic Graphs (DAGs): construction, interpretation, and causal pathway tracing
- Connecting DAG structure to prior specification in Bayesian models

<!-- more -->


<iframe 
  src="https://nbviewer.org/github/vanislekahuna/vanislekahuna.github.io/blob/master/notebooks/%5BPart_1%5DRethinking_Predictors_Why_Causal_Reasoning_Matters_in_Data_Science.ipynb" 
  width="100%" 
  height="1200px" 
  frameborder="0"
    style="border: 1px solid var(--border-color); border-radius: 4px;">
  <!-- style="border: 1px solid #ccc; border-radius: 4px;"> -->
</iframe>

---

Click the Colab badge below to run the notebook interactively:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vanislekahuna/wps-labs/blob/main/Bayesian_Wildfire_Stats_Lab/%5BPart_1%5DRethinking_Predictors_Why_Causal_Reasoning_Matters_in_Data_Science.ipynb)