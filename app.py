import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import folium
from wordcloud import WordCloud
from streamlit_folium import folium_static
from folium.plugins import FloatImage
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.figure_factory as ff

@st.cache_resource
def load_data():
    product = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/products-cleaned.csv", index_col=False)
    trimmed = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/main.csv", index_col=False)
    price = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/price.csv", index_col=False)
    shareStatistic = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/shareStatistic.csv", index_col=False)
    statistic = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/statistic.csv", index_col=False)
    reviewStatistic = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/reviewStatistic.csv", index_col=False)
    brand = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/brand.csv", index_col=False)
    info = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/info.csv", index_col=False)
    misc = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/misc.csv", index_col=False)
    sentiment = pd.read_csv("C:/Users/Admin/OneDrive - Đại học FPT- FPT University/This PC/Documents/Datasets/sentiment.csv", index_col=False)
    return product, trimmed, price, shareStatistic, statistic, reviewStatistic, brand, info, misc, sentiment

def main():
    product, trimmed, price, shareStatistic, statistic, reviewStatistic, brand, info, misc, sentiment = load_data()
    selected_tab = st.sidebar.selectbox("Select a tab", ["Main", "Miscellaneous"])
    
    if selected_tab == "Main":
        dashboard(product)
        
    if selected_tab == "Locations":
        with st.container():
            st.header("Locations")
            location(info)
        with st.container():
            st.header("Word Cloud")
            word(sentiment)

def dashboard(data):
    st.header("Sales Trends Analysis")
    
    st.subheader("Overall")
    col1, col2 = st.columns(2)
    with col1:
        sales_by_category = data.groupby('category_name')['salesTotal'].sum().reset_index()
        plot_donut_chart(sales_by_category, 'salesTotal', 'Total Sales by Category', col1)
        
        average_price_by_category = data.groupby('category_name')['market'].mean().reset_index()
        plot_colored_bar_chart(average_price_by_category, 'market', 'Average Price by Category', col1)
    with col2:
        data['totalProfit'] = data['profit'] + data['sellyProfit']
        profit_by_category = data.groupby('category_name')['totalProfit'].sum().reset_index()
        plot_donut_chart(profit_by_category, 'totalProfit', 'Profit by Category', col2)
        
        selected_category = st.sidebar.selectbox('Select Category', sorted(data['category_name'].unique()))
        filtered_data = data[data['category_name'] == selected_category]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=filtered_data.index, y=filtered_data['base'], name='Base'))
        fig.add_trace(go.ErrorBar(x=filtered_data.index, y=filtered_data['base'], error_y=dict(type='data', symmetric=False, array=filtered_data['base'] - filtered_data['minimum'], arrayminus=filtered_data['maximum'] - filtered_data['base']), name='Error Bar'))
        fig.update_layout(xaxis=dict(tickmode='array', tickvals=filtered_data.index, ticktext=filtered_data.index, title='Data Points'), yaxis=dict(title='Price'), title=f'Category: {selected_category}')
        col2.plotly_chart(fig)
    
    st.subheader('Top-Selling Products')
    top_products = data.groupby('inventory_name')['salesTotal'].sum().reset_index().nlargest(5, 'salesTotal')
    st.table(top_products)

def plot_donut_chart(data, value_col, title, column):
    fig = go.Figure(data=[go.Pie(labels=data['category_name'], values=data[value_col], hole=0.4)])
    fig.update_layout(title=title, showlegend=True)
    column.plotly_chart(fig)

def plot_colored_bar_chart(data, value_col, title, column):
    fig = go.Figure(data=[go.Bar(x=data['category_name'], y=data[value_col],
                                marker=dict(color=px.colors.qualitative.Pastel))])
    fig.update_layout(title=title, xaxis_title='Category', yaxis_title=value_col)
    column.plotly_chart(fig)

def location(data):
    data = data[(data['latitude'] != 0) & (data['longitude'] != 0)]
    m = folium.Map(location=[14.0583, 108.2772], zoom_start=5, max_bounds=True, width='100%')
        
    for index, row in data.iterrows():
        popup_text = f"<b>Supplier:</b> {row['supplier_name']}<br>"
        popup_text += f"<b>Inventory:</b> {row['inventory_name']}<br>"
        popup_text += f"<b>Address:</b> {row['address']}<br>"
        popup_text += f"<b>Province:</b> {row['provinceName']}<br>"
        popup_text += f"<b>District:</b> {row['district']}<br>"
        popup_text += f"<b>Ward:</b> {row['ward']}<br>"
        popup_text += f"<b>Category:</b> {row['category_name']}<br>"
        popup_text += f"<b>Weight:</b> {row['weight']}<br>"
        popup_text += f"<b>Volume:</b> {row['volume']}<br>"
            
        folium.Marker(location=[row['latitude'], row['longitude']], popup=folium.Popup(popup_text, max_width=500)).add_to(m)
        
    folium_static(m)

def word(data):
    text_data = ' '.join(data['content'].astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='cool', max_font_size=150).generate(text_data)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    st.pyplot(plt)

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    main()
