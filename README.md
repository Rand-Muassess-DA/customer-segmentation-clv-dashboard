# Customer Segmentation & CLV Dashboard

An end-to-end customer analytics project built using Python, Power BI, DAX, and real online retail transaction data.

## Project Objective

This project analyzes customer purchasing behavior, segments customers using RFM analysis, estimates customer value, and creates a drillthrough dashboard to support customer retention decisions.

The goal is to identify:

* High-value customers
* At-risk customers
* Revenue concentration by segment
* Customer-level purchase behavior
* Recommended retention actions

## Dataset

The project uses the UCI Online Retail dataset, which contains real transaction records from a UK-based online retail business.

Dataset source: UCI Machine Learning Repository — Online Retail Dataset

## Tools Used

* Python
* pandas
* Power BI
* DAX
* GitHub

## Dashboard Pages

### Page 1 — Customer Segmentation & CLV Dashboard

This page provides the executive customer intelligence overview, including:

* Total revenue
* Champion revenue percentage
* Total customers
* At-risk customers
* Average annual CLV
* Monthly revenue trend
* Revenue concentration by segment
* Top customers by revenue

### Page 2 — Customer Drillthrough Profile

This page allows the user to drill through into a selected customer and review:

* Customer revenue
* Average order value
* Estimated annual CLV
* Recency
* Segment classification
* Customer action recommendation
* Products purchased by the selected customer
* Customer vs segment benchmark

## Data Preparation

Python was used to clean and prepare the raw retail transaction data.

The script:

* Removed records with missing Customer IDs
* Removed cancelled invoices
* Removed invalid quantity and price records
* Created total sales values
* Calculated Recency, Frequency, and Monetary metrics
* Assigned RFM scores
* Classified customers into business segments
* Estimated annual CLV
* Exported Power BI-ready CSV files

## Project Structure

```text
Data/
Dashboard/
Scripts/
Output/
Case_Study/
```

## Case Study

A full PDF case study is included in the `Case_Study` folder.

## Author

Rand Muassess
