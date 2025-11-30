# 🎮 Pygame Games Collection

Playable in your browser! This project contains Pygame games that can be played directly on GitHub Pages.
ブラウザで遊べるPygameゲーム集です。

## 🕹️ Games / ゲーム一覧

### ⚡ Ultimate Dodge!
Dodge enemies and aim for the high score!
敵を避けてハイスコアを目指すゲーム。

**Controls / 操作方法:**
- **Arrow Keys**: Move (移動)
- **SPACE**: Start Game (ゲーム開始)

### 👊 Fighting Game
Battle through 5 stages and defeat the boss!
5つのステージを勝ち抜き、ボスを倒す格闘ゲーム。

**Controls / 操作方法:**
- **Arrow Keys**: Move (移動)
- **W / ↑**: Jump (ジャンプ)
- **Z / S / ↓**: Punch (パンチ)
- **X**: Kick (キック)
- **SPACE**: Slide (スライディング)
- **R**: Restart (リスタート)

---

## 🚀 How to Play / 遊び方

### Online (Recommended)
Go to the GitHub Pages URL after publishing:
公開後、以下のURLで遊べます：

**🌐 `https://<YOUR-USERNAME>.github.io/<REPO-NAME>/`**

### Local / ローカルで遊ぶ

```bash
# 1. Install dependencies / 依存関係のインストール
pip install -r requirements.txt

# 2. Play Dodge Game / 避けゲームをプレイ
python dodge_game/main.py

# 3. Play Fighting Game / 格闘ゲームをプレイ
python fighting_game/main.py
```

---

## 📚 Documentation / ドキュメント

### 📖 [GUIDE_1_EXE_DISTRIBUTION.md](GUIDE_1_EXE_DISTRIBUTION.md)
**0からEXEを作って配布する手順**
Windowsアプリとして配布したい場合はこちら。

### 📖 [GUIDE_2_WEB_PUBLISH.md](GUIDE_2_WEB_PUBLISH.md)
**0からGitHub Pagesに公開する手順**
ブラウザで遊べるように公開したい場合はこちら。

### 📖 [GUIDE_3_TECH_INFO.md](GUIDE_3_TECH_INFO.md)
**使用技術と用語の解説**
使われている技術や単語の意味を知りたい場合はこちら。

---

## 📁 Project Structure / プロジェクト構成

```
game_tutorial/
├── dodge_game/
│   └── main.py                # Dodge Game (Web/Local)
├── fighting_game/
│   └── main.py                # Fighting Game (Web/Local)
├── dodge_original.py          # Backup (EXE source)
├── fighting_original.py       # Backup (EXE source)
├── index.html                 # Portal Page
├── requirements.txt           # Dependencies
└── .github/
    └── workflows/
        └── build.yml          # Auto Deploy Config
```

---

## 🛠️ Tech Stack

- Python 3.11+
- Pygame
- Pygbag (for WebAssembly)
- GitHub Actions
