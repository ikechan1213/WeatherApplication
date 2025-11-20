import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime

# --- グローバル変数 (アイコン画像を保持するため、関数外で定義) ---

# 予報アイコン用 (メインアイコンの参照もここに格納して安定させます)
forecast_img_tk_list = []


# --- 関数エリア ---

def get_weather():
    # ★★★★★ 個別のAPIキー ★★★★★
    API_KEY = "5466d0fcf87088ea5156d2d890018262"

    # グローバル変数へのアクセス宣言
    global forecast_img_tk_list
    global icon_label  # メインアイコンウィジェット本体
    global forecast_icon_labels  # 予報アイコンウィジェットのリスト

    # リストを初期化 (前回検索時の画像をクリア)
    forecast_img_tk_list = []

    # メインアイコンもリセットし、参照を一旦クリア
    icon_label.config(image='')

    # 入力欄から都市名を取得
    city = city_entry.get()
    if not city:
        messagebox.showwarning("警告", "都市名を入力してください")
        return

    # --- 予報ラベルとアイコンをリセット ---
    for label in forecast_labels:
        label.config(text="---")
    for forecast_icon_widget in forecast_icon_labels:
        forecast_icon_widget.config(image='')

    # APIリクエストURL (現在の天気を取得)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"

    try:
        # APIにリクエストを送信 (現在の天気)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # --- 必要な情報を取り出す (現在の天気) ---
        city_name = data["name"]
        weather_description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        current_icon_id = data["weather"][0]["icon"]

        # --- ラベルに情報を表示 (メインエリア) ---
        city_label.config(text=f"都市名: {city_name}")
        weather_label.config(text=f"天気: {weather_description}")
        temp_label.config(text=f"気温: {temp:.1f} °C")
        feels_like_label.config(text=f"体感気温: {feels_like:.1f} °C")

        # --- メインエリアの天気アイコンを表示 ---
        icon_url = f"http://openweathermap.org/img/wn/{current_icon_id}@2x.png"
        icon_response = requests.get(icon_url)
        img_data = Image.open(BytesIO(icon_response.content))
        resized_image = img_data.resize((120, 120))

        # ⬇️ メインアイコン用の画像オブジェクトを作成
        main_icon_image = ImageTk.PhotoImage(resized_image)

        # ★★★ メインアイコンの参照を固定（リストとウィジェット自身に保持）★★★
        forecast_img_tk_list.append(main_icon_image)  # リストで永続参照を確保
        icon_label.config(image=main_icon_image)
        icon_label.image = main_icon_image  # ウィジェット自身にも参照を持たせる

        # --- 5日間予報の処理 ---

        # 5日間予報のAPIリクエストURL
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ja"

        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # 今日の日付を取得
        today = datetime.now().date()
        daily_forecasts = []

        # 予報データから、明日以降の「日本時間12時(UTC 03:00)」のデータだけを抽出
        for item in forecast_data["list"]:
            dt_txt = item["dt_txt"]
            dt_obj = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")

            # 今日より未来の日付、かつ UTC 03:00:00 (JST 12:00:00) のデータのみを抽出
            if "03:00:00" in dt_txt and dt_obj.date() > today:
                daily_forecasts.append(item)

        # -----------------------------------------------
        # 抽出したデータをGUIラベルとアイコンに反映
        # -----------------------------------------------

        # ★★★ 修正: リストの0番目から「明日」以降のデータを5日分反映 ★★★
        for i in range(5):
            label_index = i  # ラベルのインデックスは 0, 1, 2, 3, 4

            if i < len(daily_forecasts):
                day_data = daily_forecasts[i]

                # 日付、天気、気温の取得
                dt_obj = datetime.strptime(day_data["dt_txt"], "%Y-%m-%d %H:%M:%S")
                date_str = dt_obj.strftime("%m/%d (%a)")
                desc = day_data["weather"][0]["description"]
                temp = day_data["main"]["temp"]
                forecast_icon_id = day_data["weather"][0]["icon"]

                # ラベルに設定
                forecast_labels[label_index].config(text=f"{date_str}: {desc} / {temp:.1f} °C")

                # --- 予報アイコンをリストに設定 ---
                icon_url_forecast = f"http://openweathermap.org/img/wn/{forecast_icon_id}.png"
                icon_response_forecast = requests.get(icon_url_forecast)
                img_data_forecast = Image.open(BytesIO(icon_response_forecast.content)).resize((40, 40))
                img_tk_forecast = ImageTk.PhotoImage(img_data_forecast)

                forecast_img_tk_list.append(img_tk_forecast)  # 参照を保持
                forecast_icon_labels[label_index].config(image=img_tk_forecast)
            else:
                # データが足りない欄は "---" に戻し、アイコンもクリア
                forecast_labels[label_index].config(text="---")
                forecast_icon_labels[label_index].config(image='')

    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            messagebox.showerror("エラー", "都市が見つかりませんでした。")
        else:
            messagebox.showerror("エラー", f"APIエラー: {err}")
    except Exception as e:
        messagebox.showerror("エラー", f"予期せぬエラーが発生しました: {e}")


# --- GUIエリア ---

# 使用する背景色を定義 (例: Light Cyan)
MAIN_COLOR = '#E0FFFF'

# メインウィンドウの作成
root = tk.Tk()
root.title("天気予報アプリ")
root.geometry("500x670")
root.config(bg=MAIN_COLOR)

# 都市名入力フレーム
input_frame = tk.Frame(root, bg=MAIN_COLOR)
input_frame.pack(pady=10)

city_label_info = tk.Label(input_frame, text="都市名 (英語):", bg=MAIN_COLOR)
city_label_info.pack(side=tk.LEFT, padx=5)

city_entry = tk.Entry(input_frame, width=20)
city_entry.pack(side=tk.LEFT, padx=5)

search_button = tk.Button(input_frame, text="天気取得", command=get_weather)
search_button.pack(side=tk.LEFT, padx=5)

# 結果表示フレーム
result_frame = tk.Frame(root, bg=MAIN_COLOR)
result_frame.pack(pady=20)

# 各情報を表示するラベル
city_label = tk.Label(result_frame, text="都市名: ---", font=("Arial", 16), bg=MAIN_COLOR)
city_label.pack(pady=5)

weather_label = tk.Label(result_frame, text="天気: ---", font=("Arial", 14), bg=MAIN_COLOR)
weather_label.pack(pady=5)

temp_label = tk.Label(result_frame, text="気温: --- °C", font=("Arial", 14), bg=MAIN_COLOR)
temp_label.pack(pady=5)

feels_like_label = tk.Label(result_frame, text="体感気温: --- °C", font=("Arial", 14), bg=MAIN_COLOR)
feels_like_label.pack(pady=5)

# 天気アイコン表示用ラベル (メインアイコン)
icon_label = tk.Label(result_frame, bg=MAIN_COLOR)
icon_label.pack(pady=10)

# --- 5日間予報の表示フレーム  ---
forecast_frame = tk.Frame(root, bg=MAIN_COLOR)
forecast_frame.pack(pady=10)

forecast_title_label = tk.Label(forecast_frame, text="5日間の予報", font=("Arial", 14, "bold"), bg=MAIN_COLOR)
forecast_title_label.grid(row=0, column=0, columnspan=2, pady=5)

# 5日分のラベルを保持するリスト
forecast_labels = []
forecast_icon_labels = []  # アイコン画像用
for i in range(5):
    # 1. アイコンを表示するラベルを作成
    # ⬇️ 【重要】メインのicon_labelと変数名が衝突しないように修正
    forecast_icon_widget = tk.Label(forecast_frame, bg=MAIN_COLOR)
    # 1列目 (左側) に配置
    forecast_icon_widget.grid(row=i + 1, column=0, padx=5, pady=2)
    forecast_icon_labels.append(forecast_icon_widget)

    # 2. テキストを表示するラベルを作成
    text_label = tk.Label(forecast_frame, text="---", font=("Arial", 12), bg=MAIN_COLOR)
    # 2列目 (右側) に配置
    text_label.grid(row=i + 1, column=1, sticky="w", pady=2)
    forecast_labels.append(text_label)

# メインループの開始
root.mainloop()