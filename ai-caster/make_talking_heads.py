from PIL import Image
import imageio
import numpy as np
import math

def create_animation(image_path, output_path, frames=100):
    # 画像を開く
    img = Image.open(image_path).convert('RGBA')
    img_size = img.size  # 初期画像のサイズを保存しておく

    # 揺れるための余白を確保するための新しい画像サイズを計算
    new_size = (img_size[0] + 50, img_size[1] + 50)  # 余白として上下左右に25ピクセルずつ追加

    # フレームのリストを作成する
    images = []

    for i in range(frames):
        # 左右に揺れる効果を作成
        rotation = 10 * math.sin(2 * math.pi * i / frames)  # 10度の揺れ

        # 大きめの透明画像を作成
        bg_img = Image.new('RGBA', new_size, (0, 0, 0, 0))

        # 元の画像を回転させる
        rotated_img = img.rotate(rotation, resample=Image.BICUBIC, expand=True)

        # 回転後の画像サイズと位置を計算
        rotated_img_size = rotated_img.size
        new_left = (new_size[0] - rotated_img_size[0]) / 2
        new_top = (new_size[1] - rotated_img_size[1]) / 2

        # 透明画像の中央に回転後の画像を貼り付け
        bg_img.paste(rotated_img, (int(new_left), int(new_top)), rotated_img)

        # フレームリストに追加
        images.append(np.array(bg_img))

    # フレームのリストをGIFとして保存
    imageio.mimsave(output_path, images, fps=30)

create_animation("announcer.jpeg", "announcer.mp4")
create_animation("idol.jpeg", "idol.mp4")

