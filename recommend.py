import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pymysql
from sql import host, user, passwd, db2


def connect_sql():
    # 连接数据库
    db = pymysql.connect(host=host, user=user, passwd=passwd, db=db2, charset='utf8')
    cursor = db.cursor()
    sql = "SELECT book_cm_isbn, book_name, author, object FROM book_info"
    # 导入用户借书习惯
    sql_2 = "SELECT user_id, user_br_book_id FROM borrowlist"
    # 导入书籍信息
    try:
        cursor.execute(sql)
        books_df = pd.DataFrame(cursor.fetchall(), columns=['book_id', 'title', 'author', 'genre'])
        cursor.execute(sql_2)
        borrow_df = pd.DataFrame(cursor.fetchall(), columns=['user_id', 'book_id'])

        return books_df, borrow_df
    except Exception as e:
        print(e)
        return None, None

    finally:
        db.close()
        cursor.close()


# 定义一个函数来获取推荐书籍
def get_recommendations(title, cosine_sim, books_df):
    """
    基于内容的推荐算法
    :param title:
    :param cosine_sim:
    :return:
    """
    # 找到与输入书籍最相似的书籍
    try:
        # 找到输入书籍的索引
        idx = books_df[books_df['title'] == title].index[0]
        # 找到最相似的书籍的索引
        sim_scores = list(enumerate(cosine_sim[idx]))
        # 按相似度排序
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        sim_scores = sim_scores[1:15]
        book_indices = [i[0] for i in sim_scores]
        return books_df.loc[book_indices, ['title', 'genre']]
    except IndexError:
        print(f"书籍 '{title}' 未找到在数据库中。")
        return []

def recommend_books(user_id):
    books_df, borrow_df = connect_sql()
    # print(books_df)
    # print(borrow_df)
    # 数据预处理
    if books_df is not None or borrow_df is not None:

        books_df.drop_duplicates(subset=['book_id'], inplace=True)
        borrow_df.drop_duplicates(inplace=True)
        # print(books_df)
        # print(borrow_df)
    # 使用基于内容的推荐算法
    tfidf = TfidfVectorizer(stop_words='english')
    # 填充缺失值
    books_df['genre'] = books_df['genre'].fillna('')  # 填充genre列的缺失值为空字符串
    # 计算TF-IDF值
    tfidf_matrix = tfidf.fit_transform(books_df['genre'])
    # 计算余弦相似度
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    # 示例：为用户推荐书籍
    user_id = str(user_id)


    if user_id in borrow_df['user_id'].values:
        user_books = borrow_df[borrow_df['user_id'] == user_id]['book_id'].tolist()
    else:
        user_books = []
        print(f"No books found for user_id: {user_id}")
    # print(f"用户{user_id}的借阅书籍：{user_books}")
    if not user_books:
        print(f"用户{user_id}没有借阅记录。")

    user_book_titles = books_df[books_df['book_id'].isin(user_books)]['title'].tolist()
    print(f"用户{user_id}的借阅书籍：{user_book_titles}")
    book_info = []
    for title in user_book_titles:
        recommend_book = get_recommendations(title, cosine_sim, books_df)
        book_info = recommend_book[['title', 'genre']].apply(lambda x: f"书名: {x['title']}, 类别: {x['genre']}",
                                                             axis=1)
    for info in book_info:
        print(info)
    print("\n")
    return book_info


if __name__ == '__main__':
    recommend_books()
