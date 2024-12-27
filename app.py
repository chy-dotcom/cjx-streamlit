import matplotlib
import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
from matplotlib.font_manager import FontProperties  # 新增，用于加载字体文件

# 设置字体，确保支持中文（以下代码修改为从指定文件夹加载字体文件的方式）
font_path = "font/simhei.ttf"  # 假设字体文件在项目根目录下的font文件夹里，根据实际情况调整路径
font_prop = FontProperties(fname=font_path)  # 创建字体属性对象，指定字体文件路径
matplotlib.rcParams['font.family'] = font_prop.get_name()  # 应用字体配置到matplotlib相关参数中

# 加载停用词的函数
def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = set(word.strip() for word in file.readlines())  # 去除换行符和空格
    return stopwords

# 1. 获取网页文本内容
def fetch_text_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        return text
    except Exception as e:
        return str(e)

# 2. 分词和词频统计（加入停用词处理功能）
def get_word_frequency(text):
    stopwords = load_stopwords("stoppedwords.txt")
    # 使用jieba进行中文分词
    words = jieba.cut(text)
    # 去除停用词、单字
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
    word_counts = Counter(filtered_words)  # 统计词频
    return word_counts

# 3. 生成并展示词云
def generate_wordcloud(word_counts):
    wordcloud = WordCloud(font_path='font/simsun.ttc', width=800, height=600).generate_from_frequencies(word_counts)

    # 创建一个新的图形
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # 不显示坐标轴

    # 保存到缓冲区并返回
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # 关闭当前图形以释放内存
    buf.seek(0)  # 将指针移动到缓冲区的开始
    return buf

# Streamlit应用
def main():
    st.title("文章词频分析与图型展示")

    # 用户输入URL
    url = st.text_input("请输入文章URL:", "")

    if url:
        # 获取网页文本内容
        text = fetch_text_from_url(url)

        if "Error" in text:
            st.error("无法抓取该页面，请检查URL是否正确")
        else:
            st.subheader("抓取文章列表")
            # 使用st.markdown结合HTML的div和CSS样式来给文本添加边框显示
            bordered_text = f'<div style="border: 1px solid gray; padding: 10px;">{text}</div>'
            st.markdown(bordered_text, unsafe_allow_html=True)

            # 词频统计
            word_counts = get_word_frequency(text)
            most_common_words = word_counts.most_common(20)

            # 词频排名前20
            st.subheader("词频排名前20的词汇")
            st.write(most_common_words)

            # 图表类型筛选
            chart_type = st.sidebar.selectbox("选择图表类型",
                                              ["词云图", "柱状图", "饼图", "条形图", "折线图", "散点图", "面积图"])

            # 绘制不同类型的图表
            if chart_type == "词云图":
                wordcloud_buf = generate_wordcloud(word_counts)
                st.image(wordcloud_buf)
            elif chart_type == "柱状图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.bar(labels, values)
                ax.set_title("柱状图标题", fontproperties=font_prop)  # 设置标题使用指定字体
                ax.set_xlabel("X轴标签", fontproperties=font_prop)  # 设置X轴标签使用指定字体
                ax.set_ylabel("Y轴标签", fontproperties=font_prop)  # 设置Y轴标签使用指定字体
                plt.xticks(rotation=90)
                st.pyplot(fig)
            elif chart_type == "饼图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.pie(values, labels=labels, autopct='%1.1f%%')
                ax.set_title("饼图标题", fontproperties=font_prop)  # 设置标题使用指定字体
                st.pyplot(fig)
            elif chart_type == "条形图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.barh(labels, values)
                ax.set_title("条形图标题", fontproperties=font_prop)  # 设置标题使用指定字体
                ax.set_xlabel("X轴标签", fontproperties=font_prop)  # 设置X轴标签使用指定字体
                ax.set_ylabel("Y轴标签", fontproperties=font_prop)  # 设置Y轴标签使用指定字体
                st.pyplot(fig)
            elif chart_type == "折线图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.plot(labels, values)
                ax.set_title("折线图标题", fontproperties=font_prop)  # 设置标题使用指定字体
                ax.set_xlabel("X轴标签", fontproperties=font_prop)  # 设置X轴标签使用指定字体
                ax.set_ylabel("Y轴标签", fontproperties=font_prop)  # 设置Y轴标签使用指定字体
                plt.xticks(rotation=90)
                st.pyplot(fig)
            elif chart_type == "散点图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.scatter(labels, values)
                ax.set_title("散点图标题", fontproperties=font_prop)  # 设置标题使用指定字体
                ax.set_xlabel("X轴标签", fontproperties=font_prop)  # 设置X轴标签使用指定字体
                ax.set_ylabel("Y轴标签", fontproperties=font_prop)  # 设置Y轴标签使用指定字体
                plt.xticks(rotation=90)
                st.pyplot(fig)
            elif chart_type == "面积图":
                data = list(most_common_words)
                labels, values = zip(*data)
                fig, ax = plt.subplots()
                ax.fill_between(labels, values)
                ax.set_title("面积图标题", fontproperties=font_prop)  # 设置标题使用指定字体
                ax.set_xlabel("X轴标签", fontproperties=font_prop)  # 设置X轴标签使用指定字体
                ax.set_ylabel("Y轴标签", fontproperties=font_prop)  # 设置Y轴标签使用指定字体
                plt.xticks(rotation=90)
                st.pyplot(fig)

            # 交互式词频过滤
            st.subheader("交互式词频过滤")
            min_frequency = st.slider("选择最小频率", min_value=1, max_value=max(word_counts.values()), value=1)
            filtered_words = {word: count for word, count in word_counts.items() if count >= min_frequency}
            st.write(filtered_words)


if __name__ == "__main__":
    main()
