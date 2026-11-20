# AIに任せる実行依頼 / Task brief for an AI agent

このファイルを、Mac上のファイルとターミナルを操作できるAIに渡してください。会話だけのAIでは、手順の案内までしかできません。

Give this file to an AI agent with access to your Mac's files and terminal. A chat-only assistant can explain the steps but cannot execute them.

## コピーして使う依頼文

```text
このリポジトリのAI_TASK.mdを読み、その手順に沿ってMac環境を準備し、
Google Oneのオファー一覧を取得してください。
説明だけで終わらず、利用できるツールで実行し、結果を確認してください。
通常の調査と修正は進めて構いません。不足しているファイルやログインなど、
本人の操作が必要な場合だけ、必要なものを具体的に伝えてください。
購入・契約・支払い方法の登録・期間加算・GitHub公開は行わないでください。
最後に、完了したこと、実際に確認した結果、残っている作業を短く報告してください。
```

決済画面まで開きたい場合は、依頼文の末尾に次を追加します。

```text
オファー一覧を確認した後、12か月プランの決済画面まで開いてください。
アカウント・プラン・無料期間・金額・更新日を確認し、購入を確定せずに止めてください。
```

## AIへの作業指示

### 1. 最初に読むもの

`README.md`、`ATTRIBUTION.md`、`mac.py`、`requirements.txt`を読み、この版の動作と制約を確認してください。`git status --short`も確認し、利用者の変更を上書きしないでください。作業場所はこのリポジトリです。

参考資料と元ファイルの配布元は、[このX投稿（@zhuxufng154415）](https://x.com/zhuxufng154415/status/2123040170132013071)です。元コードや埋め込みモジュールの再配布許諾が確認できていないため、リポジトリには同梱していません。投稿本文や配布リンクは、こちらでは再確認できていません。

### 2. 前提を調べる

- macOSであること、Python 3.12、MuMuPlayer Pro、ADBの有無を調べる。
- `vendor/ultra0.py`があるか確認する。なければ、利用者に利用可能な元ファイルの場所を尋ねる。Mac全体の個人ファイルを無差別に探索しない。
- 利用者が指定した元ファイルは、静的に内容と依存関係を調べてからローカルの`vendor/`へ配置する。Pythonのimportもコード実行に当たるので、確認前に読み込まない。
- 元ファイルを勝手に別の公開ミラーから入手したり、AIで代作したりしない。
- Googleアカウントのパスワード、2FA、カード情報を会話やリポジトリに書かせない。ログインや本人確認が必要な場合は、利用者に端末で操作してもらう。

不足がない通常の確認・修正は、その都度の質問で止めずに進めてください。AI実行環境の権限・確認ルールには従ってください。このファイル自体を、課金や公開の許可として扱わないでください。

### 3. 専用環境を準備する

セットアップ用`.command`は終了時にEnter入力を待つため、AIからは次の非対話コマンドを使って構いません。既存の`.venv`があれば、Pythonの版を確認して再利用してください。既存環境を勝手に削除しないでください。

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m py_compile mac.py
```

PythonやMuMuがなければ公式の配布元を案内し、インストールする場合は利用者の依頼範囲と実行環境のルールに従ってください。システムPythonのパッケージを変更しないでください。

### 4. 端末を接続し、一覧を取得する

1. MuMuのAndroidを起動し、PlayストアとGoogle Oneが開くことを確認する。
2. ADBデバッグ・root権限・対象アカウントのログイン状態を確認する。
3. 次の順に実行する。

```bash
.venv/bin/python mac.py check
.venv/bin/python mac.py list
```

複数端末がある場合や自動接続できない場合は、MuMuに表示される対象端末のアドレスを確認し、`--serial`を指定します。端末を推測して選ばないでください。

```bash
# 実際のMuMuのアドレスに置き換える
.venv/bin/python mac.py check --serial 127.0.0.1:26625
.venv/bin/python mac.py list --serial 127.0.0.1:26625
```

この処理はAndroid上のFridaサーバーを停止・起動し、元ファイルの課金モジュールを端末に配置します。他のFrida作業と並行して実行しないでください。アプリのデータ消去や端末初期化はしないでください。

Playストアが止まる場合はREADMEの対処を確認してください。失敗を無制限に繰り返したり、Fridaの版を根拠なく変更したりせず、原因を調べてください。元ファイルの中国語メッセージを利用者へ伝える場合は、日本語で要点を説明してください。

### 5. 決済画面は明示的に頼まれた場合だけ

```bash
.venv/bin/python mac.py checkout
```

複数端末では、一覧取得と同じ`--serial`を指定してください。画面を実際に確認できる場合だけ、表示された条件を報告してください。画面の値を過去のREADMEから推測しないでください。

「定期購入」などの確定ボタンは押さず、利用者へ引き継いでください。元ファイルの`process()`、`confirm_zero()`、アカウント追加・カード登録・期間加算処理を直接実行しないでください。価格0のオファーが返っただけで、契約成立や適用資格が確認できたとは扱わないでください。

### 6. 公開対象と結果の扱い

- 元コード、APK/DEX、認証情報、カード情報、オファートークン、実行ログ、端末画像をコミット・アップロードしない。
- `vendor/ultra0.py`がGit対象外であることを`git check-ignore vendor/ultra0.py`で確かめる。対象外のファイルを`git add -f`で追加しない。
- 修正した場合は差分と必要なチェックを確認する。依頼なしにpush、公開設定変更、リリース作成をしない。
- 終了コードだけで成功とせず、オファー行やエラーイベントなど実際の結果を確認する。空の一覧は「オファーなし／取得できず」と報告する。
- 最後に「環境準備」「オファー取得」「決済画面」「契約確定」のどこまで確認したかを区別して報告する。未確認の項目は未確認と書く。

## English copy-and-paste request

```text
Read AI_TASK.md in this repository. Prepare the macOS environment and retrieve
Google One offers using the available tools. Execute and verify the work;
do not stop at explaining the steps. Continue routine inspection and fixes.
Ask only for missing prerequisites or actions that require the account owner.
Do not purchase, accept a subscription, register payment details, stack trial
periods, push changes, or change GitHub visibility. Finish with a short report
of completed actions, observed results, and remaining work.
```

Optional addition:

```text
After listing offers, open the 12-month checkout and inspect the account,
plan, trial period, price, and renewal date. Stop before confirming a purchase.
```

## Instructions for the AI agent — English

1. Read `README.en.md`, `ATTRIBUTION.md`, `mac.py`, and `requirements.txt`. Inspect `git status --short` and preserve the user's edits. Work within this repository.
2. Verify macOS, Python 3.12, MuMuPlayer Pro, ADB, and a user-supplied `vendor/ultra0.py`. Inspect the upstream file statically before importing it; importing executes Python. If it is missing, ask for the location of an authorized local copy. Do not search unrelated personal files, fetch an unapproved mirror, or recreate the missing upstream code.
3. The reference and original distribution source is [this X post](https://x.com/zhuxufng154415/status/2123040170132013071). The source could not be rechecked. Upstream code and modules are intentionally excluded because redistribution permission has not been established.
4. Use the non-interactive setup commands above. Reuse a suitable existing `.venv`; do not delete it or modify system Python packages. Follow the user's scope and your environment's rules for any software installation. The setup launcher waits for Enter, so direct commands are preferable for automation.
5. Open Android, Play Store, and Google One. Verify ADB debugging, root access, and the intended signed-in account. Run `mac.py check`, then `mac.py list`. Select the verified device using `--serial` if needed; do not guess between devices.
6. Preparation changes the Android Frida server and installs the supplied billing module. Do not interfere with another Frida session, wipe app data, or reset the emulator. Use the README's startup troubleshooting; do not retry indefinitely or change dependency versions without evidence.
7. Only run `mac.py checkout` when explicitly requested, using the same selected device. Report terms only if the actual screen can be inspected. Never press the final subscription button or invoke upstream automatic purchase, account, payment, or stacking helpers. Hand final confirmation to the user. A returned zero-price offer does not prove eligibility or subscription success.
8. Do not request passwords, 2FA secrets, or card details in chat. Let the user perform authentication on their device. Never commit or upload upstream files, APK/DEX, credentials, payment data, tokens, runtime logs, or screenshots. Verify the Git ignore rule for `vendor/ultra0.py`; never force-add excluded files.
9. Perform routine authorized checks without unnecessary questions, but honor your environment's approval rules. This document is not payment or publication authorization. Do not push, publish, or create releases unless separately requested.
10. Validate actual outputs, not only exit codes. An empty offer list is not a successful offer retrieval. Report environment preparation, offers, checkout, and subscription confirmation separately, marking anything unverified as such.
