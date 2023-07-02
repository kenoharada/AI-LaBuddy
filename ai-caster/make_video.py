from PIL import Image, ImageDraw, ImageFont
import textwrap
import json

# from matplotlib import font_manager
# fonts = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')

# # フォントファイルのパスのリストが出力されます
# for font in fonts:
#     print(font)


def create_slide(title, contents, image_path='slide.png'):
    W, H = (1600, 900)
    image = Image.new('RGB', (W, H), color=(73, 109, 137))
    d = ImageDraw.Draw(image)
        
    # フォントの設定(システムにインストールされているフォントを指定)
    # フォントのサイズは、タイトルとコンテンツで異なります
    title_font = ImageFont.truetype('ヒラギノ角ゴシック W1.ttc', 50)
    content_font = ImageFont.truetype('ヒラギノ角ゴシック W3.ttc', 50)
    
    # タイトルの位置を計算します
    w, h = d.textsize(title, font=title_font)
    title_position = ((W-w)/2, 40)  # 上部の余白を増やす

    # タイトルを画像に描きます
    d.text(title_position, title, fill=(255, 255, 255), font=title_font)
    
    # コンテンツのテキストを改行します
    lines = textwrap.wrap(contents, width=30)
    y_text = H/3 - 20
    for line in lines:
        width, height = d.textsize(line, font=content_font)
        text_position = (20, y_text)  # X座標を固定値に変更して左揃えにします
        d.text(text_position, line, fill=(255, 255, 255), font=content_font)
        y_text += height

    image.save(image_path)

# テスト
# create_slide("こちらがタイトルです", "こちらが内容です。この内容は100文字以内である必要があります。")

from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
# 小さな動画の読み込み
announcer = VideoFileClip("announcer.mp4").set_duration(3)
idol = VideoFileClip("idol.mp4").set_duration(3)

# 位置とサイズを調整（必要に応じて値を調整）
announcer = announcer.resize(height=200).set_position(('left', 'bottom'))
idol = idol.resize(height=200).set_position(('right', 'bottom'))
movies = []


today_info = json.load(open('today_info.json', 'r', encoding='utf-8'))
today_dialogue_list = json.load(open('today_dialogue.json', 'r', encoding='utf-8'))
create_slide(today_info['date'], today_info['text'], 'today_slide.png')
background = ImageClip('today_slide.png')

clips = []
silent_clip = AudioFileClip("silent.mp3")
for dialogue in today_dialogue_list:
    audio_clips = []
    silence_duration = 0.5  # 無音期間の長さを秒単位で設定します
    audio = AudioFileClip(dialogue['audioPath'])
    audio_clips.append(audio)
    audio_clips.append(silent_clip.set_duration(silence_duration))
    
    audio = CompositeAudioClip(audio_clips)

    duration = audio.duration

    # 背景画像を音声の長さに合わせる
    bg_clip = background.set_duration(duration)

    if dialogue['person'] == 'アイドル':
        # 偶数番の時は右下にidol.mp4を載せる
        clip = CompositeVideoClip([bg_clip, idol.set_duration(duration)]).set_audio(audio)
    else:
        # 奇数番が流れている時は背景画像の左下の部分にannouncer.mp4を載せる
        clip = CompositeVideoClip([bg_clip, announcer.set_duration(duration)]).set_audio(audio)
    
    clips.append(clip)

# クリップを連結して出力
final_clip = concatenate_videoclips(clips)
final_clip.write_videofile("today.mp4")
movies.append("today.mp4")

news_info = json.load(open('techcrunch.json', 'r', encoding='utf-8'))
for idx, news in enumerate(news_info):
    try:
        news_dialogue_list = json.load(open(f'news_dialogue_{idx}.json', 'r', encoding='utf-8'))
        create_slide('テックニュース', news_info[idx]['title_ja'], f'news_slide_{idx}.png')
        background = ImageClip(f'news_slide_{idx}.png')
        clips = []
        silent_clip = AudioFileClip("silent.mp3")
        for dialogue in news_dialogue_list:
            audio_clips = []
            silence_duration = 0.5  # 無音期間の長さを秒単位で設定します
            audio = AudioFileClip(dialogue['audioPath'])
            audio_clips.append(audio)
            audio_clips.append(silent_clip.set_duration(silence_duration))
            
            audio = CompositeAudioClip(audio_clips)

            duration = audio.duration

            # 背景画像を音声の長さに合わせる
            bg_clip = background.set_duration(duration)

            if dialogue['person'] == 'アイドル':
                # 偶数番の時は右下にidol.mp4を載せる
                clip = CompositeVideoClip([bg_clip, idol.set_duration(duration)]).set_audio(audio)
            else:
                # 奇数番が流れている時は背景画像の左下の部分にannouncer.mp4を載せる
                clip = CompositeVideoClip([bg_clip, announcer.set_duration(duration)]).set_audio(audio)
            
            clips.append(clip)

        # クリップを連結して出力
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(f"tech_{idx}.mp4")
        movies.append(f"tech_{idx}.mp4")
    except:
        continue

# 動画を全て繋げる
final_clip = concatenate_videoclips([VideoFileClip(movie) for movie in movies])
final_clip.write_videofile("news.mp4")





