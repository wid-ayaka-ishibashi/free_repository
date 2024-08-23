#%%
import pdfplumber
import pandas as pd
import os

# PDFファイルからすべてのテーブルを抽出する
def extract_tables_from_pdf(pdf_paths):
    # テーブルを格納するリストを作成
    all_tables = []
    # 各pdfファイルで繰り返す
    for pdf_path in pdf_paths:
        # 与えられたパスからpdfを開く
        with pdfplumber.open(pdf_path) as pdf:
            # pdfのページごとに処理を行う
            for page in pdf.pages:
                # ページからテーブルを抽出する
                tables = page.extract_tables()
                # 抽出したテーブルをリストに格納
                all_tables.extend(tables)
    # 指定したpdf内にあるテーブルを返す(1つのページに複数の表があるときのために長さも)
    return all_tables, len(all_tables)

# 引数に指定されたリストを連結する関数
def concatenate_table(tables_list):
    # 連結基になるデータの指定
    concatenate_base = pd.DataFrame(tables_list[0])
    # 月カラムを作成して1月の分は事前に入れておく
    concatenate_base["年月"] = "2023-01"
    for i in range(1, len(tables_list)):
        # 結合するデータに月カラムの値を入れておく
        df=pd.DataFrame(tables_list[i])
        df["年月"]=f"2023-{i+1:02}"
        # 連結基になるデータにくっつけていく
        concatenate_base = pd.concat([concatenate_base, df])
    # CSV出力した際の列番号を消去したものでconcatenate_baseを更新
    concatenate_base = pd.DataFrame(concatenate_base.values[1:], columns=concatenate_base.iloc[0])
    # 連結したデータを返す
    return concatenate_base

# csvに変換する関数
def save_to_csv(df, output_file):
    # utf-8だと文字化けして、shit-jisだとエラーが出るので
    df.to_csv(output_file, index=False, encoding="cp932")

# pdfをダウンロードしている前提でファイル名取得
dir_path=".\\depart_task_confirm\\01"
file_name=os.listdir(dir_path)

# pdfファイルパスリストを定義
pdf_path=[]
# ディレクトリパスをリスト化
dir_list=[".\\depart_task_confirm\\01\\", ".\\depart_task_confirm\\02\\",
          ".\\depart_task_confirm\\03\\", ".\\depart_task_confirm\\04\\",
          ".\\depart_task_confirm\\05\\", ".\\depart_task_confirm\\06\\",
          ".\\depart_task_confirm\\07\\", ".\\depart_task_confirm\\08\\",
          ".\\depart_task_confirm\\09\\", ".\\depart_task_confirm\\10\\",
          ".\\depart_task_confirm\\11\\", ".\\depart_task_confirm\\12\\"]

# file_nameから繰り返しを行うと月別の同じファイルが格納されていく
for file in file_name:
    for dir in dir_list:
        pdf_path.append(dir+file)

# 各月ファイルごとにスライス
tokyo_path=pdf_path[:12]

return_tokyo=extract_tables_from_pdf(tokyo_path)
# 1つのファイルのページごとに繰り返されているのでreturn_tokyo[i][j]でデータ抽出する
# return_tokyo[1]より長さが51(index:0~50)となっている
# 4つの表×12=48の長さになるはずだが12月に4+3=7つの表が入っているためである
# 1つ目の表は4の倍数で格納されている
tokyo_list1=[]
for i in range(0, 48, 4):
    tokyo_list1.append(return_tokyo[0][i])
tokyo_lists=[tokyo_list1]
# 連結からcsv出力まではfor文で処理
for i, tokyo in enumerate(tokyo_lists):
    # 事前にヘッダーを削除する処理
    # recent以外はtokyo_list[0~11]に1月から12月のデータが入っている
    # 12ヶ月分繰り返し
    for j in range(len(tokyo)):
        # i=0, i=3の時はヘッダーが1行
        # 1月分のヘッダーは削除しない
        if j>=1 and (i==0 or i==3):
            tokyo[j].pop(0)
        # i=1, i=2のときはヘッダーはない
    concatenated_tables=concatenate_table(tokyo)
    # カラム整理
    column_list=list(concatenated_tables.columns)
    for j, column in enumerate(column_list):
        if column != None:
            concatenated_tables.rename(columns={concatenated_tables.columns[j]:concatenated_tables.columns[j].replace("\n", "")}, inplace=True)
            concatenated_tables.rename(columns={concatenated_tables.columns[j]:concatenated_tables.columns[j].replace(" ", "")}, inplace=True)
            concatenated_tables.rename(columns={concatenated_tables.columns[j]:concatenated_tables.columns[j].replace("　", "")}, inplace=True)
            concatenated_tables.rename(columns={concatenated_tables.columns[j]:concatenated_tables.columns[j].replace("※", "")}, inplace=True)
    # カラム名がなぜか1月になっているので強引に変更
    if "2023-01" in concatenated_tables.columns:
        concatenated_tables.rename(columns={"2023-01":"年月"}, inplace=True)
    # 数字の前処理
    # tokyo1の処理
    if i==0:
        concatenated_tables.iloc[:, 1]=concatenated_tables.iloc[:, 1].replace(",", "", regex=True)
        concatenated_tables.iloc[:, 1]=concatenated_tables.iloc[:, 1].astype("int64")
        # 空白削除
        concatenated_tables.iloc[:, 0]=concatenated_tables.iloc[:, 0].replace(' ', '', regex=True)
        # 横持変換
        category_data={
                    '衣料品':["紳士服・洋品", "婦人服・洋品", "子供服・洋品", "その他衣料品"], 
                    '身のまわり品':[""], 
                    '雑貨':["化粧品", "美術・宝飾・貴金属", "その他雑貨"], 
                    '家庭用品':["家具", "家電", "その他家庭用品"], 
                    '食料品':["生鮮食品", "菓子", "惣菜", "その他食料品"], 
                    '食堂喫茶':[""], 
                    'サービス':[""], 
                    'その他':[""]
                    }
        concatenated_tables_horizontal=pd.DataFrame(columns=["主要カテゴリ", "主要カテゴリ売上高(千円)", "主要カテゴリ構成比(%)", "主要カテゴリ対前年増減(-)率(%)",
                                                            "サブカテゴリ", "サブカテゴリ売上高(千円)", "サブカテゴリ構成比(%)", "サブカテゴリ対前年増減(-)率(%)",
                                                            "主要カテゴリ総額売上高(千円)", "主要カテゴリ総額対前年増減(-)率(%)", "年月"])
        
        # 行インデックスを作成
        row_index = 0
        # 各月ごとの繰り返し処理
        for month in range(12):
            # 各月のデータ抽出
            temp = concatenated_tables[concatenated_tables["年月"]==f"2023-{month+1:02}"]
            # tempのインデックスを項目名に設定
            temp.index = temp[""]

            # 主要カテゴリ、サブカテゴリ、(年月)を決めればユニークになる
            # キーとリスト形式の値を抽出
            for key, values in category_data.items():
                # key:主要カテゴリ, value:サブカテゴリ
                # リスト形式の値を1つ1つ取り出す
                for value in values:
                    concatenated_tables_horizontal.loc[row_index, "主要カテゴリ"] = key
                    concatenated_tables_horizontal.loc[row_index, "主要カテゴリ売上高(千円)"] = temp.loc[key, "売上高(千円)"]
                    concatenated_tables_horizontal.loc[row_index, "主要カテゴリ構成比(%)"] = temp.loc[key, "構成比（％）"]
                    concatenated_tables_horizontal.loc[row_index, "主要カテゴリ対前年増減(-)率(%)"] = temp.loc[key, "対前年増減(-)率(%)"]
                    if value == "":
                        concatenated_tables_horizontal.loc[row_index, "サブカテゴリ"] = "-"
                        concatenated_tables_horizontal.loc[row_index, "サブカテゴリ売上高(千円)"] = "-"
                        concatenated_tables_horizontal.loc[row_index, "サブカテゴリ構成比(%)"] = "-"
                        concatenated_tables_horizontal.loc[row_index, "サブカテゴリ対前年増減(-)率(%)"] = "-"
                    else:
                        concatenated_tables_horizontal.loc[row_index, "サブカテゴリ"] = value
                        concatenated_tables_horizontal.loc[row_index, "サブカテゴリ売上高(千円)"] = temp.loc[value, "売上高(千円)"]
                        concatenated_tables_horizontal.loc[row_index, "サブカテゴリ構成比(%)"] = temp.loc[value, "構成比（％）"]
                        concatenated_tables_horizontal.loc[row_index, "サブカテゴリ対前年増減(-)率(%)"] = temp.loc[value, "対前年増減(-)率(%)"]
                    concatenated_tables_horizontal.loc[row_index, "主要カテゴリ総額売上高(千円)"] = temp.loc["総額", "売上高(千円)"]
                    concatenated_tables_horizontal.loc[row_index, "主要カテゴリ総額対前年増減(-)率(%)"] = temp.loc["総額", "対前年増減(-)率(%)"]
                    concatenated_tables_horizontal.loc[row_index, "年月"] = f"2023-{month+1:02}"
                    # 行インデックスの更新
                    row_index += 1
        concatenated_tables = concatenated_tables_horizontal
    # 出力先ファイルを指定
    output_file=f".\\depart_task_confirm\export1\\tokyo{i+1}.csv"
    # csv出力
    save_to_csv(concatenated_tables, output_file)