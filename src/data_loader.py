import pandas as pd
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "Sales_Analytics_Dataset.xlsx"

def load_data():
    fact = pd.read_excel(DATA_FILE, sheet_name="FactSales")
    products = pd.read_excel(DATA_FILE, sheet_name="DimProduct")
    customers = pd.read_excel(DATA_FILE, sheet_name="DimCustomer")
    regions = pd.read_excel(DATA_FILE, sheet_name="DimRegion")
    dates = pd.read_excel(DATA_FILE, sheet_name="DimDate")
    fact["OrderDate"] = pd.to_datetime(fact["OrderDate"])
    dates["Date"] = pd.to_datetime(dates["Date"])
    fact = (
        fact.merge(products, on="ProductID", how="left")
            .merge(customers, on="CustomerID", how="left")
            .merge(regions, on="RegionID", how="left")
    )
    return fact, products, customers, regions, dates
