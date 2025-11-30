# 📖 ガイド2: 0からGitHub Pagesに公開する手順

このガイドでは、Pygameで作ったゲームをWebブラウザで遊べるようにし、GitHub Pagesで世界中に公開する手順を解説します。

---

## 📍 全体の流れ

1.  **構成**: Web公開用のフォルダ構成にする
2.  **修正**: コードをWeb対応（Pygbag用）に修正する
3.  **公開**: GitHubにプッシュして公開設定を行う

---

## Step 1: Web公開用のフォルダ構成

Pygbag（変換ツール）の仕様上、以下のルールを守る必要があります。

1.  **ゲームごとにフォルダを分ける**
2.  **メインファイル名は必ず `main.py` にする**

**推奨される構成:**
```
project_folder/
├── dodge_game/         # 避けゲーム用フォルダ
│   └── main.py         # 必ず main.py という名前！
└── fighting_game/      # 格闘ゲーム用フォルダ
    └── main.py         # 必ず main.py という名前！
```

---

## Step 2: コードの修正（Web対応）

ブラウザで動かすために、Pythonコードに以下の修正が必要です。

### 2-1. 非同期処理の追加（必須）
ブラウザがフリーズしないように、`asyncio` を使って制御をブラウザに返す必要があります。

**修正前:**
```python
def main():
    while True:
        # ゲームの処理
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
```

**修正後:**
```python
import asyncio  # 追加

async def main():  # async をつける
    while True:
        # ゲームの処理
        pygame.display.update()
        clock.tick(60)
        await asyncio.sleep(0)  # 必須！これを入れないと止まります

if __name__ == "__main__":
    asyncio.run(main())  # asyncio.run で実行
```

### 2-2. 日本語フォントの廃止
WebAssembly（ブラウザ版）では、PCに入っている日本語フォントが使えません。
文字化けを防ぐため、**ゲーム内のテキストはすべて英語（英数字）**にしてください。

---

## Step 3: GitHubへのプッシュと公開

このプロジェクトには、自動でWeb変換して公開する仕組み（GitHub Actions）が設定されています。

### 3-1. GitHubにプッシュ
ターミナルで以下のコマンドを実行します。

```powershell
git add .
git commit -m "Web公開の準備完了"
git push
```

### 3-2. GitHub Pagesを有効化
1.  GitHubのリポジトリページを開きます。
2.  **Settings**（設定）タブをクリック。
3.  左メニューの **Pages** をクリック。
4.  **Build and deployment** の **Source** を以下に変更：
    *   `Deploy from a branch` ➔ **`GitHub Actions`**

### 3-3. 公開完了！
設定を変更すると自動的にビルドが始まります。数分後、以下のURLでゲームが遊べるようになります。

`https://<ユーザー名>.github.io/<リポジトリ名>/`

---

## 🧪 ローカルでのテスト方法

公開前に自分のパソコンで確認したい場合は、以下のコマンドを使います。

```powershell
# 仮想環境に入る
.venv\Scripts\activate

# pygbagをインストール
pip install pygbag

# ゲームフォルダを指定して実行
pygbag dodge_game
```
ブラウザで `http://localhost:8000` を開くとテストプレイできます。

---

## ❓ トラブルシューティング

**Q: 画面が真っ暗で動かない**
A: ブラウザのコンソール（F12キー）を見てください。「No main.py found」ならファイル名が間違っています。「SyntaxError」ならコードの修正が必要です。

**Q: 音が出ない**
A: ブラウザの仕様で、ユーザーが画面をクリックするまで音が出ないことがあります。
