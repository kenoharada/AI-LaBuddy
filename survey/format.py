import os
import glob
import json
import pandas as pd
questions = [
    'What is this paper about? What is the main topic/idea/theme?',
    'What makes this paper impressive compared to previous research? What are the novel contributions? What is new compared to previous work? How does it outperform previous research?',
    'What is the core of the technique or method of this paper?',
    'How was this paper\'s effectiveness validated? What experiments were conducted? What are the evaluation methods?',
    'Are there any discussions? What are the limitations of this paper? What are the future works?',
    'What are the next papers to read? What are the related papers?'
]
item_label_jp = {
    'What is this paper about? What is the main topic/idea/theme?': 'どんなもの？',
    'What makes this paper impressive compared to previous research? What are the novel contributions? What is new compared to previous work? How does it outperform previous research?': '先行研究と比べてどこがすごい？',
    'What is the core of the technique or method of this paper?': '技術や手法のキモはどこ？',
    'How was this paper\'s effectiveness validated? What experiments were conducted? What are the evaluation methods?': 'どうやって有効だと検証した？',
    'Are there any discussions? What are the limitations of this paper? What are the future works?': '議論はある？',
    'What are the next papers to read? What are the related papers?': '次読むべき論文は？'
}

item_label_en = {
    'What is this paper about? What is the main topic/idea/theme?': 'What is it about?',
    'What makes this paper impressive compared to previous research? What are the novel contributions? What is new compared to previous work? How does it outperform previous research?': 'What makes this paper impressive compared to previous research?',
    'What is the core of the technique or method of this paper?': 'What is the core of the technique ',
    'How was this paper\'s effectiveness validated? What experiments were conducted? What are the evaluation methods?': 'How was this paper\'s effectiveness validated?',
    'Are there any discussions? What are the limitations of this paper? What are the future works?': 'Are there any discussions?',
    'What are the next papers to read? What are the related papers?': 'What are the next papers to read?'
}
import json

# HTMLテンプレート
html_template_ja = '''
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>論文の要約</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
    }}

    .paper {{
        max-width: 800px;
        margin: 2rem auto;
        padding: 1rem;
    }}

    h2 {{
        margin: 0;
    }}

    .authors {{
        font-style: italic;
        margin-bottom: 1rem;
    }}

    .container {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(3, auto);
        gap: 1rem;
        margin-bottom: 2rem;
    }}

    .item {{
        background-color: #f1f1f1;
        padding: 1rem;
        border-radius: 4px;
    }}

    .item h3 {{
        font-size: 1.1rem;
        margin: 0 0 0.5rem 0;
        padding: 2px 4px;
    }}

    .item p {{
        margin: 0;
        padding-top: 0.5rem;
    }}

    @media screen and (max-width: 600px) {{
        .container {{
            grid-template-columns: 1fr;
            grid-template-rows: repeat(6, auto);
        }}
    }}
</style>
</head>
<body>
{papers_html}
</body>
</html>
'''

html_template_en = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Summary of papers</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
    }}

    .paper {{
        max-width: 800px;
        margin: 2rem auto;
        padding: 1rem;
    }}

    h2 {{
        margin: 0;
    }}

    .authors {{
        font-style: italic;
        margin-bottom: 1rem;
    }}

    .container {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(3, auto);
        gap: 1rem;
        margin-bottom: 2rem;
    }}

    .item {{
        background-color: #f1f1f1;
        padding: 1rem;
        border-radius: 4px;
    }}

    .item h3 {{
        font-size: 1.1rem;
        margin: 0 0 0.5rem 0;
        padding: 2px 4px;
    }}

    .item p {{
        margin: 0;
        padding-top: 0.5rem;
    }}

    @media screen and (max-width: 600px) {{
        .container {{
            grid-template-columns: 1fr;
            grid-template-rows: repeat(6, auto);
        }}
    }}
</style>
</head>
<body>
{papers_html}
</body>
</html>
'''

# paperのHTMLテンプレート
paper_template = '''
<div class="paper">
    <h2><a href="{url}" target="_blank">{title}</a></h2>
    <p class="authors">{authors}</p>
    <div class="container">
        <div class="item">
            <h3>{item_1_title}</h3>
            <p>{item_1_desc}</p>
        </div>
        <div class="item">
            <h3>{item_2_title}</h3>
            <p>{item_2_desc}</p>
        </div>
        <div class="item">
            <h3>{item_3_title}</h3>
            <p>{item_3_desc}</p>
        </div>
        <div class="item">
            <h3>{item_4_title}</h3>
            <p>{item_4_desc}</p>
        </div>
        <div class="item">
            <h3>{item_5_title}</h3>
            <p>{item_5_desc}</p>
        </div>
        <div class="item">
            <h3>{item_6_title}</h3>
            <p>{item_6_desc}</p>
        </div>
    </div>
</div>
'''


if __name__ == '__main__':
    result_data = 'result_data'
    save_dir = 'output'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    json_path_list = glob.glob(os.path.join(result_data, '*.json'))
    result_html_ja = 'result_ja.html'
    result_html_en = 'result.html'
    result_csv = 'result.csv'
    result_data = []


    # 各paperの情報を埋め込んだHTMLを作成
    papers_html = ''
    for json_path in json_path_list:
        with open(json_path, 'r', encoding='utf-8') as f:
            paper = json.load(f)
            result_data.append(paper)
        filled_paper_template = paper_template.format(
            title=paper['title'],
            url=paper['id'],
            authors=', '.join(paper['authors']),
            item_1_title=item_label_jp[questions[0]],
            item_1_desc=paper['jp_'+questions[0]],
            item_2_title=item_label_jp[questions[1]],
            item_2_desc=paper['jp_'+questions[1]],
            item_3_title=item_label_jp[questions[2]],
            item_3_desc=paper['jp_'+questions[2]],
            item_4_title=item_label_jp[questions[3]],
            item_4_desc=paper['jp_'+questions[3]],
            item_5_title=item_label_jp[questions[4]],
            item_5_desc=paper['jp_'+questions[4]],
            item_6_title=item_label_jp[questions[5]],
            item_6_desc=paper['jp_'+questions[5]],
        )
        papers_html += filled_paper_template

    # 最終的なHTMLを生成
    final_html_ja = html_template_ja.format(papers_html=papers_html)

    # 最終的なHTMLをファイルに書き込む
    with open(os.path.join(save_dir, result_html_ja), 'w', encoding='utf-8') as file:
        file.write(final_html_ja)
    
    # 各paperの情報を埋め込んだHTMLを作成
    papers_html = ''
    for json_path in json_path_list:
        with open(json_path, 'r', encoding='utf-8') as f:
            paper = json.load(f)
        filled_paper_template = paper_template.format(
            title=paper['title'],
            url=paper['id'],
            authors=', '.join(paper['authors']),
            item_1_title=item_label_en[questions[0]],
            item_1_desc=paper[questions[0]],
            item_2_title=item_label_en[questions[1]],
            item_2_desc=paper[questions[1]],
            item_3_title=item_label_en[questions[2]],
            item_3_desc=paper[questions[2]],
            item_4_title=item_label_en[questions[3]],
            item_4_desc=paper[questions[3]],
            item_5_title=item_label_en[questions[4]],
            item_5_desc=paper[questions[4]],
            item_6_title=item_label_en[questions[5]],
            item_6_desc=paper[questions[5]],
        )
        papers_html += filled_paper_template

    # 最終的なHTMLを生成
    final_html_en = html_template_ja.format(papers_html=papers_html)

    # 最終的なHTMLをファイルに書き込む
    with open(os.path.join(save_dir, result_html_en), 'w', encoding='utf-8') as file:
        file.write(final_html_en)

    print("HTMLファイルが生成されました。")

    # JSONリストをpandas DataFrameに変換
    papers_df = pd.DataFrame(result_data)

    # authorsリストをカンマ区切りの文字列に変換
    papers_df['authors'] = papers_df['authors'].apply(lambda authors: ', '.join(authors))

    # DataFrameをCSVファイルに保存
    papers_df.to_csv(os.path.join(save_dir, result_csv), index=False)
        
