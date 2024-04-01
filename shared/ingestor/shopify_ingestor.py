import os
from shared.ingestor.ingestor import Ingestor
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from langchain.docstore.document import Document

class ShopifyIngestor(Ingestor):
    def __init__(self, config):
        super().__init__('')
        
        self.config = config

    def ingest(self):
        if self.config is None:
            return None

        docs = self.get_documents()

        return docs
    
    def get_documents(self):
        docs = []
        data = self.get_cleaned_products()

        for doc in data:
            d=Document(
                page_content=doc.get('expanded_description'),
                metadata=self.get_metadata(doc)
            )

            docs.append(d)

        return docs

    def get_cleaned_products(self):
        products = self.get_all_products()
        products_df = pd.DataFrame(products)

        cleaned_df = self.preprocessing(products_df)
        cleaned_products = cleaned_df.to_dict('records')

        return cleaned_products

    def get_all_products(self):
        products = []

        params = {
            "limit": 250
        }

        headers = {
            "X-Shopify-Access-Token": self.config.get('api_key')
        }

        url = f"{self.config.get('store_url')}/admin/api/{self.config.get('api_version')}/{self.config.get('resource')}.json"
        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        products.extend(data["products"])

        try:
            while response.links["next"]:
                response = requests.get(response.links["next"]["url"], headers=headers)
                data = response.json()

                products.extend(data["products"])

                time.sleep(2)
        except KeyError:
            return products
        
    def clean_html_tags(self, row):
        soup = BeautifulSoup(row["body_html"], "html.parser")
        text = soup.get_text()
        row["body_html"] = text

        return row

    def get_img_src(self, row):
        images = []

        for image in row["images"]:
            images.append(image["src"])

        row["images"] = images

        return row

    def get_price(self, row):
        prices = []

        for v in row["variants"]:
            prices.append({
                "price": v["price"],
                "title": v["title"],
                "id": v["product_id"],
            })

        row["prices"] = prices

        return row

    def create_expandend_description(self, row):
        if row["body_html"] == "" and row["tags"] == "":
            row["expanded_description"] = row["title"]
        elif row["body_html"] == "" and row["tags"] != "":
            row["expanded_description"] = "Title: " + row['title'] + " Tags: " + row['tags']
        elif row["body_html"] != "" and row["tags"] == "":
            row["expanded_description"] = "Title: " + row['title'] + " Description: " +row["body_html"]
        else:
            row["expanded_description"] = "Title: " + row['title'] + " Description: " +row["body_html"] + " Tags: " + row['tags']
        return row

    def preprocessing(self, df):
        df = df[df["status"] == "active"]
        df.fillna("", inplace=True)

        df = df.apply(lambda row: self.get_img_src(row), axis=1)
        df = df.apply(lambda row: self.get_price(row), axis=1)
        df = df.apply(lambda row: self.create_expandend_description(row), axis=1)
        df = df.apply(lambda row: self.clean_html_tags(row), axis=1)

        df = df.rename(columns={"body_html": "description"})
        df = df[["id", "title", "handle", "product_type", "description", "expanded_description", "tags", "prices",  "images"]]

        return df

    def get_metadata(self, record: dict) -> dict:
        metadata = dict()

        metadata["id"] = record.get("id")
        metadata["title"] = record.get("title")
        metadata["tags"] = record.get("tags")
        metadata["images"] = record.get("images")
        metadata["handle"] = record.get("handle")
        metadata["product_type"] = record.get("product_type")
        metadata["prices"] = record.get("prices")

        return metadata