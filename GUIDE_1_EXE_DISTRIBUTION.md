# 📖 ガイド1: 0からEXEを作って配布する手順

このガイドでは、Pythonで作ったゲームをWindowsアプリ（EXEファイル）に変換し、GitHub Releasesを使って友達に配布するまでの手順を解説します。

---

## 📍 全体の流れ

1.  **準備**: 開発環境を整える
2.  **開発**: ゲームを作る
3.  **変換**: ゲームをEXEファイルにする
4.  **配布**: GitHub Releasesで公開する

---

## Step 1: 準備（開発環境を作る）

まずは道具を揃えます。

### 1-1. PythonとVS Codeのインストール
*   [Python公式サイト](https://www.python.org/downloads/) からPythonをインストール（**"Add Python to PATH"** にチェックを入れること！）
*   [VS Code公式サイト](https://code.visualstudio.com/) からエディタをインストール

### 1-2. プロジェクトの作成
1.  適当なフォルダ（例: `C:\my_games`）を作成し、VS Codeで開きます。
2.  **仮想環境（venv）**を作成します（推奨）。
    ```powershell
    # ターミナルで実行
    python -m venv .venv
    .venv\Scripts\activate
    ```
3.  必要なライブラリをインストールします。
    ```powershell
    pip install pygame pyinstaller
    ```

---

## Step 2: ゲームを作る

VS Codeで `main.py` などのファイルを作成し、Pygameを使ってゲームを開発します。
（このプロジェクトの `dodge.py` や `fighting_original.py` が完成品の例です）

---

## Step 3: ゲームをEXE化する

作ったPythonファイルは、そのままではPythonが入っていないパソコンで動きません。
**PyInstaller** を使ってEXEファイルに変換します。

### 3-1. EXE化コマンドの実行

ターミナルで以下のコマンドを実行します。

```powershell
# 例: dodge.py をEXEにする場合
pyinstaller --onefile --windowed --name "MyDodgeGame" dodge.py
```

**オプションの意味:**
*   `--onefile`: 1つのEXEファイルにまとめる
*   `--windowed`: 黒い画面（コンソール）を出さない
*   `--name`: 出来上がるEXEの名前を指定

### 3-2. 完成品の確認
コマンド完了後、`dist` フォルダの中に `MyDodgeGame.exe` が生成されます。
これが配布用のゲームソフトです！

---

## Step 4: GitHub Releasesで配布する

GitHubの「Releases」機能を使うと、バージョン管理しながらソフトを配布できます。

### 4-1. GitHubにコードをアップロード
まだリポジトリがない場合は作成し、コードをプッシュします。

```powershell
git init
git add .
git commit -m "Initial commit"
# リポジトリURLは自分のものに変えてください
git remote add origin https://github.com/あなたのユーザー名/リポジトリ名.git
git push -u origin main
```

### 4-2. Releaseの作成
1.  GitHubのリポジトリページを開きます。
2.  右側の **「Releases」** をクリックし、**「Create a new release」** を選択。
3.  **Tag version**（例: `v1.0`）とタイトルを入力。
4.  `dist` フォルダ内の **EXEファイル** をドラッグ＆ドロップでアップロード。
    *   ※ファイルサイズが大きい場合はZIP圧縮してください。
5.  **「Publish release」** をクリック。

これで配布ページが完成しました！URLを共有すれば誰でもダウンロードできます。

---

## ⚠️ 注意点：ファイルサイズ制限

GitHub Releasesには **1ファイルあたり2GB** の制限があります。

### 容量が大きい場合の対処法
1.  **ZIP圧縮する**: エクスプローラーで右クリック→「圧縮」でサイズを減らす。
2.  **Git LFSを使う**: 2GBを超える巨大なファイルは「Git LFS」という仕組みを使う必要がありますが、通常の2DゲームであればZIP圧縮で十分です。

---

## ❓ よくある質問

**Q: ウイルス対策ソフトに警告される**
A: 自作ソフトは「デジタル署名」がないため、警告が出ることがあります。配布時は「警告が出たら『詳細情報』→『実行』を押してね」と伝えましょう。

**Q: 画像や音楽が表示されない**
A: `--onefile` でEXE化した場合、画像ファイルのパス指定に工夫が必要です。
`sys._MEIPASS` という特殊な変数を使ってパスを取得するコードを書く必要があります（詳しくは「PyInstaller 画像 埋め込み」で検索）。
