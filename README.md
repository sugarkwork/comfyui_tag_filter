# comfyui_tag_filter

WD14Tagger などが出力したタグを、特定のカテゴリに分けて、カテゴリごとにフィルタリングして返す ComfyUI のカスタムノードです。

# TagFilter

特定のカテゴリに属するタグだけを抽出します。
smile や grin などは、expression というカテゴリです。
色のついているものは color カテゴリです。

![image](https://github.com/sugarkwork/comfyui_tag_fillter/assets/98699377/cde288d8-2d23-4989-9d1f-3b5ff3845c72)

include_categories は、含めたいカテゴリ名をカンマ区切りで指定します。

include_categories に expression と入力すると、上のチェックボックスをクリックしたのと同じ結果になります。

exclude_categories は逆に取り除きたいカテゴリを指定できます。服のタグだけ取りたいが色の指定は不要な場合に、include_categories に cloth と入れて、exclude_categories に color と打ちます。

何がどのカテゴリに分類されているかは、[tag_category.json](https://github.com/sugarkwork/comfyui_tag_fillter/blob/main/tag_category.json) を見て確認してください。

tag_category.json は AI により自動仕分けされた、タグのカテゴリ分けファイルです。誤った内容が含まれる場合もあります（細々と手動で調整を進めています）

# TagRemover

プロンプトの中から指定されたタグを削除したい時に使います。
TagFilter と合わせて使うと、表情のタグだけ消す、色（color）タグだけ消す、といった事が出来ます。

![image](https://github.com/sugarkwork/comfyui_tag_fillter/assets/98699377/694aadc3-8968-4153-bd52-8809aec47df6)

# TagReplace (動作検証中、うまく動かないかも)

同じカテゴリのタグを置き換えます。

例えば long hair というタグが含まれるプロンプトを入力し、置き換えるタグに twintails を指定すると、long hair を twintails に置き換える事が出来ます。

どれぐらい近いタグを置き換えるかを、0.0 ～ 1.0 で指定します。1.0 を指定するとカテゴリとして完全一致した場合にのみタグが置換されます。0.3 ぐらいがちょうどいいです。うまく置換されない場合は値を下げてください。

![image](https://github.com/sugarkwork/comfyui_tag_fillter/assets/98699377/c492c518-0531-4735-8a73-3a29ae0b9a1b)

# TagSwitcher

default_image と image1 という画像をセットする必要があります。
input_tags に WD14 Tagger などのから出力されたタグを渡して、tag1 にフィルタリングするタグをセットします。
こうすると、input_tags の中に tag1 のタグが含まれる場合（どれか1つでも含まれる条件なら any1 を True）に、image1 の画像を出力します。
同様に tag2 のタグが含まれる場合は image2 を出力します。

使用用途としては、例えば入力画像にもし猫耳が含まれる場合には絶対消すという処理を行いたい場合。
CLIPSeg Masking などのノードで動物の耳を検出しそれを Big lama Remover で消去した画像を作ります。
もし画像のタグに animal_ears, cat_ears が含まれる場合、Big lama で消去した画像を出力し、それらの動物耳のタグが含まれない場合は元の画像を出力します。

何が嬉しいかというと、CLIPSeg は、探したい対象物が画面内に見つけられない場合、適当な部分をマスクしてしまい、無関係なものを消してしまう事があります。

TagSwitcher では入力タグに基づいて、その物が画像内に含まれる場合のみに動作し、対象物を消去した画像を提供出来ます。

![image](https://github.com/user-attachments/assets/f875272b-5512-4907-8d80-42e89b38e776)

# TagMerger

ただタグをマージするだけです。既に存在するタグを無視されます。

![image](https://github.com/user-attachments/assets/fb3d5fc7-b6fb-4e2a-9b5d-4d210935ab56)

# TagSelector

タグをカテゴリで指定、あるいは指定したカテゴリのタグだけ除外します。exclude が False で選択。exclude が True で指定したカテゴリを除外します。

ホワイトリストのオプションは、タグの中でも「tag_category.json」に記載があるタグのみを許可して、不明なタグを削除します。

フレキシブルフィルターは、例えば「crasy long hair」という謎のタグを使用した場合でも、自動的にこれを「long hair」であると認識して「long hair」のカテゴリである「hair style」にマッチさせて、タグの認識を柔軟に処理します。

![Image](https://github.com/user-attachments/assets/15dd8dec-f9db-4b1a-bac6-bf14dee5a43d)

# TagEnhance / TagCategoryEnhance

タグを、指定されたタグに関して、タグの強度を追加あるいは置き換えします。

TagCategoryEnhance は、タグの強度の調整の際にタグではなくタグのカテゴリを指定して、強度の追加あるいは置き換えを行います。

![Image](https://github.com/user-attachments/assets/cdc18942-27a7-4864-8e13-1259cf84ac4a)

# TagIf

特定のタグが含まれる場合に、output1, 2, 3 に設定した文字列を出力します。

例えば、特定のタグの条件下でポジティブタグ、ネガティブタグを出力するなどの使い方が出来ます。

![Image](https://github.com/user-attachments/assets/712a0310-7d1e-4842-8fb3-c9813c08b947)

# TagComparator

2つのタグ群を比較して、タグ１だけのタグ、タグ２だけのタグ、共通のタグを出します。

何に使うのかは分かりません。

![Image](https://github.com/user-attachments/assets/52c5a31d-33cf-4071-8a17-23b76962c98d)

# TagWildcardFilter

タグをワイルドカード（* ← このアスタリスク）でフィルタリングします。

例えば、wildcard に *hair と指定すると、long_hair や　short_hair がヒットします。

逆に hair* とすると、hair_ornament のようなものだけをフィルタリング出来ます。

アスタリスクを含めない場合は、タグの文字列の中のどこかに含まれる場合、つまり \*hair\* を指定した事と同じになります。

![image](https://github.com/user-attachments/assets/d947b63a-2857-403a-b203-74eff3217d8a)

# TagCategory

入力されたタグが所属しているカテゴリー名をカンマ区切りで出力します。

![image](https://github.com/user-attachments/assets/547a8895-79e6-445d-bcde-8cd638f571f0)

