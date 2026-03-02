# Customer Churn Prediction: An End-to-End ML Solution

Retaining customers is more cost-effective than acquiring new ones. This project provides a robust machine learning framework designed to identify customers at high risk of leaving, allowing businesses to intervene proactively with targeted retention strategies. By analyzing historical behavioral patterns, we move from reactive response to predictive action.

## Problem Definition

In many service-based industries, customer churn is a silent profit killer. Identifying which customers are likely to leave is inherently difficult due to the complex interplay of service quality, billing issues, and behavioral cues. Furthermore, the dataset for such problems is almost always heavily skewed, as most customers (thankfully) do not churn. This class imbalance often leads to models that are "accurate" on paper—by simply predicting no one will leave—but fail to identify the critical minority that actually does.

## Solution

To solve this, I developed an end-to-end predictive pipeline that prioritizes real-world utility over vanity metrics. The solution features:

1.  **Iterative Model Development**: Using XGBoost for its superior performance on tabular data and ability to capture non-linear relationships.
2.  **Addressing Data Skew**: Integrating SMOTE (Synthetic Minority Over-sampling Technique) during the training phase to balance the representation of churners and non-churners.
3.  **Real-Time Serving**: A Flask-based REST API that brings the model's predictions into live production environments.
4.  **Operational Dashboard**: "ChurnSight," a Streamlit interface that empowers non-technical stakeholders to use the model's insights.

## Project Vision

The core objective was to build a deployment-ready system that translates complex data into actionable business intelligence. This involved everything from raw data cleaning and statistical balancing to architecting a scalable API and an intuitive decision-support dashboard.

## Key Outcomes

Through iterative development and rigorous testing, this project achieved the following technical milestones:

*   Predictive Accuracy: Achieved a robust ~78% cross-validated accuracy. It is important to note that this metric was maintained while solving a severe class imbalance; the model doesn't just predict the majority class but identifies churning customers with high recall thanks to specialized SMOTE preprocessing.
*   Class Imbalance Resolution: Addressed target skew using SMOTE, processing over 7,000 records to ensure the minority "Churn" class was correctly weighted and identified.
*   Scalable Architecture: Built a RESTful Flask API capable of serving real-time predictions with precise probability scores.
*   Hyperparameter Optimization: Validated the model through extensive grid-search (570+ fits), ensuring the best possible log-loss performance.

## Live Deployment Support

The ChurnSight dashboard is deployed and accessible for real-time interaction. You can explore the model's predictions and test various customer profiles directly via the following link:

[Access ChurnSight Dashboard](LINK)

## The ChurnSight Dashboard

To bridge the gap between data science and decision-making, I developed ChurnSight—a Streamlit-based interface. It allows users to:
*   Input customer profiles directly into a modern, responsive UI.
*   Receive instant churn risk assessments and retention probabilities.
*   Visualize the confidence of the model's decision through dynamic risk bars.

## Technical Architecture

The system is built on a modern Python stack focused on performance and reliability:
*   Engineering: pandas, numpy, and scikit-learn for robust data pipelines.
*   Modeling: XGBoost for high-performance gradient boosting and imbalanced-learn for SMOTE.
*   Service: Flask for the prediction backend.
*   Interface: Streamlit for the frontend dashboard.

## Getting Started

Follow these steps to set up the environment and run the system locally.

### Prerequisites
*   Python 3.8 or higher

### Installation
1. Clone the repository and navigate to the project directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the System Locally
1. Start the Flask Prediction API:
   ```bash
   python main.py
   ```
   The server will initialize and load the trained model and encoders from the exports directory.

2. Launch the ChurnSight Dashboard:
   ```bash
   streamlit run app.py
   ```
   The dashboard will open in your default browser, typically at http://localhost:8501.

## API Usage

The Flask server exposes two primary endpoints for integration with other services:

*   GET /health: Returns the current status of the server and confirms if the model is loaded.
*   POST /predict: Accepts customer data in JSON format and returns churn predictions and probabilities.

Example Request:
```json
{
    "gender": "Male", 
    "SeniorCitizen": 0, 
    "Partner": "No", 
    "Dependents": "Yes", 
    "tenure": 12, 
    "MonthlyCharges": 65.0, 
    "TotalCharges": 780.0,
    "Contract": "Month-to-month",
    "InternetService": "Fiber optic"
}
```

## Conclusion

This project demonstrates how data science can be operationalized to solve critical business challenges. By combining sophisticated machine learning with practical deployment tools, it provides a template for building intelligent, data-driven applications that deliver measurable value.
