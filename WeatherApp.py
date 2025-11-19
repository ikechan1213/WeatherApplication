import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime


# --- 関数エリア ---

def get_weather():
    # ★★★★★ 個別のAPIキー ★★★★★
    API_KEY = "5466d0fcf87088ea5156d2d890018262"

    # 入力欄から都市名を取得
    city = city_entry.get()
    if not city:
        messagebox.showwarning("警告", "都市名を入力してください")
        return

        # --- (ここから追加) 予報ラベルをリセット ---
    for label in forecast_labels:
            label.config(text="---")

    # APIリクエストURL (現在の天気を取得)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"

    try:

        # --- (ここから5日間予報の処理) ---

        # 5日間予報のAPIリクエストURL
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ja"

        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # 3時間ごとのデータ(40件)から、お昼(12:00)のデータだけを抽出
        daily_forecasts = []
        for item in forecast_data["list"]:
            if "12:00:00" in item["dt_txt"]:
                daily_forecasts.append(item)

        # 抽出したデータを5日分、GUIラベルに反映
        for i in range(len(daily_forecasts[:5])):  # 5日分に制限
            day_data = daily_forecasts[i]

            # 日付のフォーマットを "YYYY-MM-DD HH:MM:SS" から "MM/DD (曜)" に変更
            dt_obj = datetime.strptime(day_data["dt_txt"], "%Y-%m-%d %H:%M:%S")
            # %a は 曜日 (例: 'Sat')。ロケール(実行環境)によっては日本語になります。
            date_str = dt_obj.strftime("%m/%d (%a)")

            # 天気
            desc = day_data["weather"][0]["description"]

            # 気温
            temp = day_data["main"]["temp"]

            # ラベルに設定
            forecast_labels[i].config(text=f"{date_str}: {desc} / {temp:.1f} °C")
        # ここまでが5日間予報処理

        # APIにリクエストを送信
        response = requests.get(url)
        response.raise_for_status()  # エラーがあれば例外を発生

        # 返ってきたJSONデータをPythonの辞書に変換
        data = response.json()

        # --- 必要な情報を取り出す ---

        # 都市名
        city_name = data["name"]

        # 天気の詳細 (例: "晴れ", "曇り")
        weather_description = data["weather"][0]["description"]

        # 気温 (摂氏)
        temp = data["main"]["temp"]

        # 体感気温
        feels_like = data["main"]["feels_like"]

        # 天気アイコンID
        icon_id = data["weather"][0]["icon"]

        # --- ラベルに情報を表示 ---
        city_label.config(text=f"都市名: {city_name}")
        weather_label.config(text=f"天気: {weather_description}")
        temp_label.config(text=f"気温: {temp:.1f} °C")
        feels_like_label.config(text=f"体感気温: {feels_like:.1f} °C")

        # --- 天気アイコンを表示 ---
        icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        icon_response = requests.get(icon_url)

        # PILを使って画像を開く
        img_data = Image.open(BytesIO(icon_response.content))

        # Tkinterで使える画像形式に変換
        # ★★ 注意: global img_tk を使わないと画像が表示されない ★★
        global img_tk
        img_tk = ImageTk.PhotoImage(img_data)

        icon_label.config(image=img_tk)

    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            messagebox.showerror("エラー", "都市が見つかりませんでした。")
        else:
            messagebox.showerror("エラー", f"APIエラー: {err}")
    except Exception as e:
        messagebox.showerror("エラー", f"予期せぬエラーが発生しました: {e}")


# --- GUIエリア ---

# メインウィンドウの作成
root = tk.Tk()
root.title("天気予報アプリ")
root.geometry("400x500")

# 都市名入力フレーム
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

city_label_info = tk.Label(input_frame, text="都市名 (英語):")
city_label_info.pack(side=tk.LEFT, padx=5)

city_entry = tk.Entry(input_frame, width=20)
city_entry.pack(side=tk.LEFT, padx=5)

search_button = tk.Button(input_frame, text="天気取得", command=get_weather)
search_button.pack(side=tk.LEFT, padx=5)

# 結果表示フレーム
result_frame = tk.Frame(root)
result_frame.pack(pady=20)

# 各情報を表示するラベル
city_label = tk.Label(result_frame, text="都市名: ---", font=("Arial", 16))
city_label.pack(pady=5)

weather_label = tk.Label(result_frame, text="天気: ---", font=("Arial", 14))
weather_label.pack(pady=5)

temp_label = tk.Label(result_frame, text="気温: --- °C", font=("Arial", 14))
temp_label.pack(pady=5)

feels_like_label = tk.Label(result_frame, text="体感気温: --- °C", font=("Arial", 14))
feels_like_label.pack(pady=5)

# 天気アイコン表示用ラベル
icon_label = tk.Label(result_frame)
icon_label.pack(pady=10)

# --- 5日間予報の表示フレーム  ---
forecast_frame = tk.Frame(root)
forecast_frame.pack(pady=10)

forecast_title_label = tk.Label(forecast_frame, text="5日間の予報", font=("Arial", 14, "bold"))
forecast_title_label.pack(pady=5)

# 5日分のラベルを保持するリスト(リストを作ることでこの後のgetweatherで1つめのラベルは1日目という用に分かりやすくしている)
forecast_labels = []
for _ in range(5):
    label = tk.Label(forecast_frame, text="---", font=("Arial", 12))
    label.pack()
    forecast_labels.append(label)

# メインループの開始
root.mainloop()