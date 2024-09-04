import streamlit as st
import os
from .connetion import StorageManager

# 初始化 StorageManager 实例
storage_manager = StorageManager()

# 标题
st.title("Interactive Network Graph")

# 选择元数据显示选项
show_ddo_metadata = st.checkbox("Show DDO Metadata", value=False)
show_fdo_metadata = st.checkbox("Show FDO Metadata", value=True)
show_rel_metadata = st.checkbox("Show Relationship Metadata", value=False)

# 绘制关系网络
storage_manager.draw_relationship_network(show_ddo_metadata, show_fdo_metadata, show_rel_metadata)

# 显示网络图
html_path = 'network.html'
if os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8') as html_file:
        source_code = html_file.read()
    st.components.v1.html(source_code, height=750, width=900, scrolling=True)
else:
    st.error("The network graph HTML file was not found.")
