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
        idx = books_df[books_df['title'] == title].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:6]
        book_indices = [i[0] for i in sim_scores]
        return books_df.loc[book_indices, ['title', 'genre']]
    except IndexError:
        print(f"书籍 '{title}' 未找到在数据库中。")
        return []


def recommend_books():
    books_df, borrow_df = connect_sql()
    print(f"books_df: {books_df}, borrow_df: {borrow_df}")
    # 数据预处理
    if books_df is not None or borrow_df is not None:
        print(1)
        books_df.drop_duplicates(subset=['book_id'], inplace=True)
        borrow_df.drop_duplicates(inplace=True)
    print(f"books_df: {books_df}, borrow_df: {borrow_df}")
    # 使用基于内容的推荐算法
    tfidf = TfidfVectorizer(stop_words='english')

    books_df['genre'] = books_df['genre'].fillna('')
    tfidf_matrix = tfidf.fit_transform(books_df['genre'])
    print(f"tfidf_matrix: {tfidf_matrix}")
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    print(f"cosine_sim: {cosine_sim}")
    print(1)
    print(borrow_df['user_id'].dtype)  # 打印 user_id 列的数据类型
    # 示例：为用户推荐书籍
    user_id = str(2303080201)
    print(borrow_df.head())  # 打印数据框的前几行，查看数据框的内容
    print(borrow_df['user_id'].unique())  # 打印数据框中所有唯一的 user_id
    print(borrow_df['user_id'].dtype)  # 打印 user_id 列的数据类型

    if user_id in borrow_df['user_id'].values:
        user_books = borrow_df[borrow_df['user_id'] == user_id]['book_id'].tolist()
        print(f"用户{user_id}的借阅书籍：{user_books}")
    else:
        user_books = []
        print(f"No books found for user_id: {user_id}")
    print(f"用户{user_id}的借阅书籍：{user_books}")
    if not user_books:
        print(f"用户{user_id}没有借阅记录。")

    user_book_titles = books_df[books_df['book_id'].isin(user_books)]['title'].tolist()
    print(f"用户{user_id}的借阅书籍：{user_book_titles}")
    for title in user_book_titles:
        print(f"推荐书籍给用户，基于书籍: {title}")
        recommend_book = get_recommendations(title, cosine_sim, books_df)
        book_info = recommend_book[['title', 'genre']].apply(lambda x: f"书名: {x['title']}, 类别: {x['genre']}",
                                                             axis=1)
        print(f'推荐书籍：{book_info}')
        for info in book_info:
            print(info)
        print("\n")
        return book_info


if __name__ == '__main__':
    recommend_books()
