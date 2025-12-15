---
layout: post
title: "How to Augment Wildfire Datasets with Historical Weather Data using Python and Google Earth Engine"
categories: [climate-ai]
---

This notebook demonstrates how to augment wildfire datasets with historical weather data using Python and Google Earth Engine's ERA5 dataset. Here we transform basic fire records (coordinates and timestamps) into enriched datasets containing comprehensive environmental context including temperature, wind patterns, humidity, and soil conditions which are all critical information for fire risk modeling and analysis. The workflow includes automatic retry logic for handling API timeouts and incremental batch saving to prevent data loss during long processing runs.

**Topics covered:**
- Authenticating and querying Google Earth Engine API
- Extracting historical weather data from ERA5 satellite imagery
- Batch processing large wildfire datasets with error resilience
- Converting wind components to speed and cardinal directions
- Handling multiple data formats (CSV, Excel, JSON, SQLite)

<!-- more -->


<iframe 
  src="https://nbviewer.org/github/vanislekahuna/wps-labs/blob/main/data/historical_bc_wildfires/Earth_Engine_Augment_Wildfire_Datasets.ipynb" 
  width="100%" 
  height="1200px" 
  frameborder="0"
    style="border: 1px solid var(--border-color); border-radius: 4px;">
  <!-- style="border: 1px solid #ccc; border-radius: 4px;"> -->
</iframe>

---

*Note: This notebook is maintained in the [`wps-labs` repository](https://github.com/vanislekahuna/wps-labs).*

Click the Colab badge below to run the notebook interactively:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vanislekahuna/wps-labs/blob/main/data/historical_bc_wildfires/Earth_Engine_Augment_Wildfire_Datasets.ipynb)