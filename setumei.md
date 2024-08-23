---
puppeteer:
    displayHeaderFooter: true
    headerTemplate: '<div style="font-size: 12px; margin-left: 1cm;"></div>'
    footerTemplate: '<div style="font-size: 12px; margin-left: 19cm;"><span class="pageNumber"></span>/<span class="totalPages"></span></div>'
---
# 参考

<div style="text-align: right;">
新規作成　2024/08/23
</div>

---

## 1. 処理イメージ

1. テーブルを3つに分ける
1. ヘッダー加工
1. サブカテゴリに主要カテゴリ項目付与
1. 結合
1. 欠損埋め、ヘッダー整理

---

ここでは分かりやすくするため「年月 = "2023-07","2023-08"」の2ヵ月分で説明する。
※「カテゴリ」名は勝手に設定。

<image src="svg/data1.svg" width=40%>

### 1.1 テーブルを3つに分ける

<div style="display: flex; justify-content: space-between;">
       <div style="width: 50%">
            ●主要カテゴリ（PK：カテゴリ、年月）
            <image src ="svg/data_main_cate.svg"><br>
            ●主要カテゴリ総額（PK：年月）
            <image src ="svg/data_total.svg">
       </div>
       <div style="width: 45%">
            ●サブカテゴリ（PK：カテゴリ、年月）
            <image src ="svg/data_sub_cate.svg">
       </div>
</div>

### 1.2 ヘッダー加工

<div style="display: flex; justify-content: space-between;">
       <div style="width: 50%">
            ●主要カテゴリ
            <image src ="svg/data_main_cate2.svg"><br>
            ●主要カテゴリ総額
            <image src ="svg/data_total2.svg">
       </div>
       <div style="width: 45%">
            ●サブカテゴリ
            <image src ="svg/data_sub_cate2.svg">
       </div>
</div>

### 1.3 サブカテゴリに主要カテゴリ項目作成

<image src="svg/data_sub_cate3.svg" width=60%>

### 1.4 結合

※Excelで作ったのでヘッダーはpandasの`merge()`と違うかも。年月のddhhmmddは無視。
<image src="svg/data2.svg" width=70%>

### 1.5 欠損埋め、ヘッダー整理

<image src="svg/data3_fin.svg" width=80%>

## 2.参考コード

```Python

# 「# 横持変換」の続きから
# 本来カラム名がすべて設定されていることが望ましい
concatenated_tables.rename(
    columns={concatenated_tables.columns[0]: "カテゴリ"}, inplace=True)
concatenated_tables.head()

category_dict = {
    "衣料品": ["紳士服・洋品", "婦人服・洋品", "子供服・洋品", "その他衣料品"],
    "身のまわり品": [""],
    "雑貨": ["化粧品", "美術・宝飾・貴金属", "その他雑貨"],
    "家庭用品": ["家具", "家電", "その他家庭用品"],
    "食料品": ["生鮮食品", "菓子", "惣菜", "その他食料品"],
    "食堂喫茶": [""],
    "サービス": [""],
    "その他": [""]
}

# 主要カテゴリ
category_keys = category_dict.keys()
df_main_category = concatenated_tables[
    concatenated_tables["カテゴリ"].isin(category_keys)
]

# サブカテゴリ
category_calues = [
    item for sublist in category_dict.values() for item in sublist
]
df_sub_category = concatenated_tables[
    concatenated_tables["カテゴリ"].isin(category_calues)
]

# 総額
df_total = concatenated_tables[concatenated_tables["カテゴリ"] == "総額"]

# 面倒なので無理やりカラム名変更
df_main_category.columns = [
    "主要カテゴリ", "主要カテゴリ売上高(千円)", "主要カテゴリ構成比（％）",
    "主要カテゴリ対前年増減(-)率( % )", "年月"]
df_sub_category.columns = [
    "サブカテゴリ", "サブカテゴリ売上高(千円)", "サブカテゴリ構成比（％）",
    "サブカテゴリ対前年増減(-)率( % )", "年月"]
df_total.drop(columns=["カテゴリ", "構成比（％）"], inplace=True)
df_total.columns = [
    "主要カテゴリ総額売上高(千円)","主要カテゴリ総額対前年増減(-)率( % )",
    "年月"]

# サブカテゴリに主要カテゴリ列追加
def add_main_category_column(df, category_dict):
    category_map = {v: k for k, values in category_dict.items()
                    for v in values}
    df["主要カテゴリ"] = df["サブカテゴリ"].map(category_map)
    return df


df_sub_category = add_main_category_column(df_sub_category, category_dict)

# 結合
df_finaly = df_main_category.merge(
    df_sub_category, how="left", on=["主要カテゴリ", "年月"]) \
    .merge(df_total, how="left", on="年月")

# カラム名並び替え・欠損値補完
df_finaly = df_finaly[[
    col for col in df_finaly.columns if col != "年月"] + ["年月"]]
df_finaly.fillna("-", inplace=True)
```
