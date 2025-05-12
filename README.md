# Jewelry Sales Report Generator

This application helps you generate monthly sales reports for your jewelry business. It creates Excel reports with sales data, charts, and summary statistics.

## Features

- Pre-defined categories for different jewelry items
- Automatic calculation of total sales
- Generation of sales charts (bar chart and pie chart)
- Summary statistics including total sales, average sale price, and total items sold
- Easy-to-use Excel interface for data entry

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python jewelry_sales_report.py
```

## How to Use

1. When you run the script, it will create an Excel file named `Jewelry_Sales_[Month]_[Year].xlsx`
2. Open the Excel file and enter your sales data:
   - Fill in the "Quantity Sold" and "Unit Price" for each category
   - The "Total Sales" column will be calculated automatically
3. Save the Excel file
4. Run the script again to update the report with your data and generate charts

## Report Contents

The Excel report contains two sheets:
1. **Sales Data**: Contains detailed sales information for each category
2. **Summary**: Shows overall statistics including total sales, average sale price, and total items sold

## Charts

The application generates two charts in the `sales_charts` directory:
1. A bar chart showing total sales by category
2. A pie chart showing the distribution of sales across categories

## Categories Included

- Rings
- Chains
- Silver Anklets
- Gold Necklaces
- Diamond Earrings
- Bracelets
- Pendants
- Other 