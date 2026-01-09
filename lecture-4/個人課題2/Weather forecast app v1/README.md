## 2522091 平 偉倫

気象庁APIを利用した天気予報アプリケーション


##  機能

-  全国の地域リストを表示
-  選択した地域の天気予報を表示
-  直近3日間の詳細予報
-  週間予報（7日間）
-  ネオンテーマのモダンUI



```bash
# リポジトリをクローン
git clone <repository-url>
cd weather-forecast

# 依存関係をインストール
pip install flet requests
```


## 使用API

- 地域リスト: `http://www.jma.go.jp/bosai/common/const/area.json`
- 天気予報: `https://www.jma.go.jp/bosai/forecast/data/forecast/{地域コード}.json`