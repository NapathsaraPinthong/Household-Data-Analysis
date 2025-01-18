
# Household Data Analysis using Graph Techniques

The project focuses on handling heterogeneous, high-dimensional datasets from the Ministry of Social Development and Human Security (MSDHS) of Thailand, employing graph embeddings and machine learning to uncover patterns in socioeconomic fragility.

The system transforms raw household data into graph representations, applies the 'metapath2vec' algorithm for node embeddings, and uses clustering and classification techniques to provide actionable insights.


## Tech Stack

- **Library:** StellarGraph, Plotly
- **Machine Learning:** SVC, K-Means, t-SNE 
- **Language:** Python, JavaScript, HTML, CSS
- **Database:** MongoDB 


## Dataset

The dataset is a simulated version of the real MSDHS data, containing:

- **Nodes:** 174,232 entities (households, members, income levels, etc.)
- **Edges:** Relationships such as - household-to-member and household-to-income.
- **Attributes:** Socioeconomic data including income, family problems, and health issues.
- **Fragility Levels:** Categorized into five levels (-1 to 3) based on income and dependencies.

**Example of raw data in MongoDB**
- Household Collection
```
{
  "_id": 0000000000,
  "latitude": 00.00000,
  "longitude": 000.00000,
  "hh_type": {
    "code": "HHT3",
    "desc": "Extended Household"
  },
  "hh_code": "0000000000",
  "province_code": "00",
  "house_type": {
    "code": "HT1",
    "desc": "Land has its own ownership"
  },
  "house_solid": 0,
}
```
- Member Collection
```
{
  "_id": 0000000000
  "hh_id": 0000000000,
    "age": 60
  "is_hh_head": 1,
  "province_code": "00",
  "edu_level": {
    "code": "EL2",
    "desc": "Primary education"
  },
  "marital_status": "Married",
  "sex": "Male",
  "SUM_DEBT": 100000,
  "SUM_INCOME": 100000,
  "occup_status": 1,
  "disability": null,
  "have_pwd_card": null,
  "is_disabled": 0,
  "prob_family": [
    {
      "code": "PBFA21",
      "desc": "Poor family"
    }
  ],
  "prob_health": null,
}
```
## Web Application

- Hosted at: [Household Data Analysis using Graph Techniques](https://cn2-household-analysis.netlify.app/)
- **Features**
    - **Clustering Visualization:** Compare results from K-Means, GMM, and BIRCH clustering methods.
    - **Attribute-Based Filtering:** Highlight households by attributes like income, age, or health for focused analysis.  
    - **Dynamic Interaction:** Explore cluster densities with interactive Plotly plots.
    - **Comparative Analysis:** Evaluate clusters against MSDHS-defined fragility levels



## Documentation

- [Final Research Report](https://drive.google.com/file/d/1LaI3R6-rGjsTZMX89TdeQkMl9QqmfLGv/view?usp=sharing)


## Authors

- [@Napathsara Pinthong](https://github.com/NapathsaraPinthong)
- [@Pavida Malitong](https://github.com/pavidamalitong)
- [@Panipak Wongbubpha](https://github.com/pawong88)

