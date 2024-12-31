import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from wordcloud import WordCloud
import io
import pandas as pd

# 加载停用词的函数
def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = set(word.strip() for word in file.readlines())
    return stopwords

# 获取网页文本内容
def fetch_text_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        titles = [a.get('title', '') for a in soup.find_all('a')]
        text = '\n'.join(titles)
        return text
    except Exception as e:
        return str(e)
        
# 分词和词频统计
def get_word_frequency(text):
    stopwords = load_stopwords("stoppedwords.txt")
    words = jieba.cut(text)
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
    word_counts = Counter(filtered_words)
    return word_counts

# 生成并展示词云
def generate_wordcloud(word_counts):
    wordcloud = WordCloud(font_path='font/simsun.ttc', width=800, height=600).generate_from_frequencies(word_counts)
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

# 设置字体，确保支持中文
font_path = 'font/SimHei.ttf'  # 确保这个路径与您的项目结构相匹配
font_prop = fm.FontProperties(fname=font_path)

# Streamlit应用
def main():
    st.title("文章词频分析与图型展示")
    url = st.text_input("请输入文章URL:", "")
    if url:
        text = fetch_text_from_url(url)
        if "Error" in text:
            st.error("无法抓取该页面，请检查URL是否正确")
        else:
            st.subheader("抓取文章列表")
            bordered_text = f'<div style="border: 1px solid gray; padding: 10px;">{text}</div>'
            st.markdown(bordered_text, unsafe_allow_html=True)
            word_counts = get_word_frequency(text)

            # 获取词频排名前20的词汇，并转换为DataFrame展示，替换原来的展示方式
            top_20_word_counts_df = pd.DataFrame(list(word_counts.most_common(20)), columns=['词语', '频率'])
            st.subheader("词频排名前20的词汇")
            st.dataframe(top_20_word_counts_df)

            chart_type = st.sidebar.selectbox("选择图表类型", ["词云图", "柱状图", "饼图", "条形图", "折线图", "散点图", "面积图"])
            if chart_type == "词云图":
                wordcloud_buf = generate_wordcloud(word_counts)
                st.image(wordcloud_buf)
            else:
                data = list(word_counts.most_common(20))  # 这里还是用前20的数据来做图表，可根据实际需求调整
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                if chart_type == "柱状图":
                    ax.bar(labels, values)
                elif chart_type == "饼图":
                    ax.pie(values, labels=labels, autopct='%1.1f%%', textprops={'fontproperties': font_prop})
                elif chart_type == "条形图":
                    ax.barh(labels, values)
                elif chart_type == "折线图":
                    ax.plot(labels, values)
                elif chart_type == "散点图":
                    ax.scatter(labels, values)
                elif chart_type == "面积图":
                    ax.fill_between(labels, values)
                ax.set_xticklabels(ax.get_xticklabels(), fontproperties=font_prop)
                ax.set_yticklabels(ax.get_yticklabels(), fontproperties=font_prop)
                ax.set_title(chart_type + ' 图表', fontproperties=font_prop)
                plt.xticks(rotation=90)
                st.pyplot(fig)

            st.subheader("交互式词频过滤")
            min_frequency = st.slider("选择最小频率", min_value=1, max_value=max(word_counts.values()), value=1)
            filtered_words = {word: count for word, count in word_counts.items() if count >= min_frequency}
            st.write(filtered_words)

if __name__ == "__main__":
    main()
