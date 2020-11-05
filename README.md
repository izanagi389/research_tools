## 研究利用ツール

研究で利用中（開発中）

### 開発環境
・MacOS　Mojave（10.14.6）  
・Python (3.8.5)  
・pip (20.1.1)  


### get_tweet.py

TwitterAPIを用いてツイートのタイトル、URLを取得し、csvファイルに格納  
API_KEY、TwitterIDなどの設定などは別記ファイル（今回はdoc2vec_config.py）に記載

### get_news.py

NewsAPIを用いてキーワード検索した記事のURLを取得。  
その後、「BeautifulSoup4」を用いて記事をスクレイピング  
記事の内容、URLをcsvファイルに格納  
API_KEYなどの設定などは別記ファイル（今回はconfig.py）に記載

### doc2vec.py

csvからテキストデータを取得し  
「Doc2Vec」を利用し、コサイン類似度を抽出  
設定などは別記ファイル（今回はdoc2vec_config.py）に記載

### word_movers_distance.py

csvからテキストデータを取得し  
「Word2Vecモデル」「word movers distance」を用いて、二つの文章類似度を計算  
設定は別記ファイル（今回はword2vec_config.py）に記載

### maiking_graph.py

csvデータから抽出した数値をヒストグラムに変換し、画像として保存する  

### search_similar_word.py

csvからテキストデータを取得し  
LDAを用いてテキストデータのトピックを生成する
