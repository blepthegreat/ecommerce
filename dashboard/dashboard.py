import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load Data
@st.cache_resource
def load_data():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
    data_path = os.path.join(BASE_DIR, "data")
    
    order_items = pd.read_csv(os.path.join(data_path, "order_items_dataset.csv"))
    order_payments = pd.read_csv(os.path.join(data_path, "order_payments_dataset.csv"))
    products = pd.read_csv(os.path.join(data_path, "products_dataset.csv"))
    return order_items, order_payments, products

# Load datasets
order_items, order_payments, products = load_data()

# Title
st.title("E-Commerce Data Analysis Dashboard")

# Sidebar Menu for Filters
st.sidebar.header("Filter Data")
num_categories = st.sidebar.slider("Jumlah Kategori Terlaris", 5, 20, 10)

# Filter by Category Selection
selected_category = st.sidebar.multiselect(
    "Pilih Kategori Produk",
    options=products["product_category_name"].unique(),
    default=products["product_category_name"].unique().tolist()
)

# **Analisis Produk Terlaris**
st.header("📦 10 Kategori Produk Terlaris")

# Step 1: Filter data based on selected categories
filtered_data = order_items[order_items["product_id"].isin(products[products["product_category_name"].isin(selected_category)]["product_id"])]
product_sales = filtered_data.groupby("product_id")["order_item_id"].count().reset_index()

# Step 2: Merge with products data to get product categories and translated category names
product_sales = product_sales.merge(products[['product_id', 'product_category_name', 'product_category_name_english']], on='product_id', how='left')

# Step 3: Calculate total sales per category and sort by total sales
category_sales_total = product_sales.groupby(['product_category_name', 'product_category_name_english'])['order_item_id'].sum().reset_index()

# Step 4: Sort the categories by total sales and get the top 10
top_10_categories = category_sales_total.sort_values(by='order_item_id', ascending=False).head(num_categories)

# Step 5: Create a bar plot for the top 10 product categories with translated category names
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='order_item_id', y='product_category_name_english', data=top_10_categories, hue='product_category_name_english', palette='coolwarm', ax=ax)
ax.set_title(f"Top {num_categories} Produk Kategori Terlaris dengan Nama Kategori Terjemahan", fontsize=14)
ax.set_xlabel("Jumlah Terjual", fontsize=12)
ax.set_ylabel("Kategori Produk", fontsize=12)
plt.xticks(rotation=45)
st.pyplot(fig)

# **Visualisasi Pie Chart**
st.header("📊 Distribusi Penjualan Kategori Produk")
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(top_10_categories['order_item_id'], labels=top_10_categories['product_category_name_english'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette("coolwarm", num_categories))
ax.set_title("Distribusi Penjualan Berdasarkan Kategori Produk")
st.pyplot(fig)

# **Analisis Metode Pembayaran**
st.header("💳 Metode Pembayaran yang Paling Banyak Digunakan")

payment_counts = order_payments["payment_type"].value_counts()

# Dropdown for payment method selection
payment_method = st.sidebar.selectbox("Pilih Metode Pembayaran", payment_counts.index.tolist())

# Filter by selected payment method
payment_filtered = order_payments[order_payments["payment_type"] == payment_method]

fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=payment_counts.index, y=payment_counts.values, palette='viridis', ax=ax)
ax.set_title(f"Metode Pembayaran: {payment_method}", fontsize=14)
ax.set_xlabel("Metode Pembayaran", fontsize=12)
ax.set_ylabel("Jumlah Transaksi", fontsize=12)
plt.xticks(rotation=45)
st.pyplot(fig)

# Show more detailed information if needed
st.write("**Detail Pembayaran:**")
st.write(payment_filtered)

# **Kesimpulan**
st.write("\n**Kesimpulan:**")
st.write("- Kategori produk yang paling banyak dibeli adalah yang memiliki jumlah order tertinggi.")
st.write("- Metode pembayaran yang paling sering digunakan perlu mendapat perhatian lebih untuk meningkatkan pengalaman pelanggan.")
