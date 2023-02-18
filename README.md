# OSC_OBSController
 VRChatのExpressionメニューからOSCでOBSを制御する
 
 たまに通信に失敗してエラーがでます
## 使い方
###### OBSの設定
1. OBSを開いて [ツール → Websocketの設定] に移動する

![image](https://user-images.githubusercontent.com/74849003/219845943-ec1803d7-de2a-4f5b-a088-76ca0f52531e.png)

2. "Websocketサーバーを有効にする"にチェックを入れる

![image](https://user-images.githubusercontent.com/74849003/219846013-22fa79a7-cc50-4843-a88e-348a3e3ce11f.png)

###### サーバーの設定

3.　config.jsonのポートおよびパスワードをOBSのwebsocketの接続情報と揃える
(リモートコンピュータのOBSを制御する場合は、IPアドレスも揃える）

![image](https://user-images.githubusercontent.com/74849003/219845556-289bc322-6258-49aa-9814-dbf547067c0a.png)

4. OBSのオーディオデバイス名をconfig.jsonの"devices"に入力

(設定しなくても動きますが音量メニューのコントロールが使えません)

![image](https://user-images.githubusercontent.com/74849003/219845871-f4b9036f-6180-4f40-8c8e-8a774af9393d.png)

###### アバター(Unity)の設定

5. ![ここ](https://github.com/bdunderscore/modular-avatar/releases/latest)からModular Avatarをダウンロードしてインポートする。

6. 付属のunitypackageをインポートする。

![image](https://user-images.githubusercontent.com/74849003/219846450-cc2ac7c0-cd75-4f1a-9a53-f31f897a2212.png)

7. ```nekochanfood/OSC_OBSController```内にあるプレハブ (日本語にしたい場合は_JPがついてるプレハブ) をアバターにD&Dする。

8. アバターをアップロードする。

###### VRChatの設定

9. アップロードしたアバターに変更し、Radial Menuを開いて ```Options > OSC > Enabled```がオンになっていることを確認する。

![image](https://user-images.githubusercontent.com/74849003/219849169-ba32e377-0cd9-4158-b457-d069d1e212b6.png)

10. OBSを開く。

11. ```OSC_OBSController.exe```を開いて、```sync completed```と表示されれば通信ができる状態です。

![image](https://user-images.githubusercontent.com/74849003/219847234-1d3a9988-db00-42c3-8f74-d10e405d511b.png)

12. Expression Menu内に```OBS コントロール```というメニューがあるので押す。

![image](https://user-images.githubusercontent.com/74849003/219847307-0285da68-0c1f-41a0-8eaf-0e7cf28450be.png)

13. 一応説明です。

![image](https://user-images.githubusercontent.com/74849003/219849369-0b321e46-0971-4a0a-ae1f-25e603ecae0e.png)

| 名前  | 意味 |
| ------------- | ------------- |
| コントロールメニュー  | 録画やリプレイバッファのオンオフ  |
| 音量  | デスクトップ音声やマイクの音量の調節やミュート  |
| フォルダを開く  | 保存した動画のフォルダを開く  |
| 録画した動画を開く  | 最後に録画した動画を開く  |
| コンフィグ  | パラメータの更新とサーバーのシャットダウン  |

ちなみにですがconfig.jsonの```locales```を```"locales/ja_jp.json"```にすると日本語になります。
