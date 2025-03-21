import datetime as dt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import streamlit as st

# Load Data
def load_data():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
    data_path = os.path.join(BASE_DIR, "data")
    
    order_items = pd.read_csv(os.path.join(data_path, "order_items_dataset.csv"))
    order_payments = pd.read_csv(os.path.join(data_path, "order_payments_dataset.csv"))
    products = pd.read_csv(os.path.join(data_path, "products_dataset.csv"))
    return order_items, order_payments, products

# Load datasets
order_items, order_payments, products = load_data()

# Cek kolom-kolom yang ada dalam products
print(products.columns)

# Jika kolom 'product_category_name_english' tidak ada, tambahkan kolom tersebut menggunakan dictionary terjemahan
category_translation = {
    'cama_mesa_banho': 'Bedding, Furniture, and Bath',
    'beleza_saude': 'Beauty and Health',
    'esporte_lazer': 'Sports and Leisure',
    'bebes': 'Baby',
    'utilidades_domesticas': 'Housewares',
    'automotivo': 'Automotive',
    'livros': 'Books',
    'informatica_acessorios': 'Computers and Accessories',
    'moveis_decoracao': 'Furniture and Decoration',
    'telefonia': 'Telephony'
}

# Menambahkan kolom terjemahan kategori produk
products['product_category_name_english'] = products['product_category_name'].map(category_translation)

# Merge order_items_dataset_df with products_dataset_df to get product_category_name
merged_df = pd.merge(order_items, products[['product_id', 'product_category_name', 'product_category_name_english']], on='product_id', how='left')

# Menghitung jumlah transaksi berdasarkan kategori produk dan metode pembayaran
# Note: 'payment_type' from order_payment_df is used as a proxy for 'payment_method'
payment_category_counts = merged_df.groupby(['product_category_name', order_payments['payment_type']]).size().unstack(fill_value=0)

# Rename columns for clarity and to match the barplot arguments
payment_category_counts = payment_category_counts.rename_axis(index='product_category_name')  # Rename index
payment_category_counts = payment_category_counts.reset_index()  # Reset index to column

# Melt the DataFrame to long format for easier plotting with seaborn
payment_category_counts = payment_category_counts.melt(id_vars=['product_category_name'], var_name='payment_method', value_name='transaction_count')

# Top 10 Categories Sales Calculation
product_sales = merged_df.groupby("product_id")["order_item_id"].count().reset_index()

# Merge dengan produk untuk mendapatkan kategori produk dan nama kategori terjemahan
product_sales = product_sales.merge(products[['product_id', 'product_category_name', 'product_category_name_english']], on='product_id', how='left')

# Menghitung total penjualan per kategori produk
category_sales_total = product_sales.groupby(['product_category_name', 'product_category_name_english'])['order_item_id'].sum().reset_index()

# Mengurutkan kategori berdasarkan total penjualan dan mendapatkan top 10
top_10_categories = category_sales_total.sort_values(by='order_item_id', ascending=False).head(10)

# Visualisasi menggunakan barplot
plt.figure(figsize=(12, 6))
sns.barplot(x='order_item_id', y='product_category_name_english', data=top_10_categories, hue='product_category_name_english', palette='coolwarm')
plt.title("Top 10 Kategori Produk Terlaris dengan Nama Kategori Terjemahan", fontsize=14)
plt.xlabel("Jumlah Terjual", fontsize=12)
plt.ylabel("Kategori Produk", fontsize=12)
plt.show()

# Visualisasi Pie Chart untuk distribusi kategori produk terlaris
plt.figure(figsize=(8, 8))
plt.pie(top_10_categories['order_item_id'], labels=top_10_categories['product_category_name_english'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette("coolwarm", 10))
plt.title("Distribusi Penjualan Berdasarkan Kategori Produk Terlaris", fontsize=14)
plt.show()

# Streamlit Dashboard
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

# Analisis Produk Terlaris
st.header("📦 10 Kategori Produk Terlaris")
# Filter data berdasarkan kategori yang dipilih
filtered_data = order_items[order_items["product_id"].isin(products[products["product_category_name"].isin(selected_category)]["product_id"])]
product_sales = filtered_data.groupby("product_id")["order_item_id"].count().reset_index()
product_sales = product_sales.merge(products, on="product_id", how="left")
product_sales = product_sales.groupby("product_category_name")["order_item_id"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=product_sales.index[:num_categories], y=product_sales.values[:num_categories], palette='coolwarm', ax=ax)
ax.set_title("Top {} Produk Kategori Terlaris".format(num_categories), fontsize=14)
ax.set_xlabel("Kategori Produk", fontsize=12)
ax.set_ylabel("Jumlah Terjual", fontsize=12)
plt.xticks(rotation=45)
st.pyplot(fig)

# Visualisasi Pie Chart
st.header("📊 Distribusi Penjualan Kategori Produk")
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(product_sales[:num_categories], labels=product_sales.index[:num_categories], autopct='%1.1f%%', startangle=140, colors=sns.color_palette("coolwarm", num_categories))
ax.set_title("Distribusi Penjualan Berdasarkan Kategori Produk")
st.pyplot(fig)

# Analisis Metode Pembayaran
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

st.write("\n**Kesimpulan:**")
st.write("- Kategori produk yang paling banyak dibeli adalah yang memiliki jumlah order tertinggi.")
st.write("- Metode pembayaran yang paling sering digunakan perlu mendapat perhatian lebih untuk meningkatkan pengalaman pelanggan.")
