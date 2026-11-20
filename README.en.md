# Google AI Pro · macOS / MuMu

[日本語](README.md) · [English](README.en.md) · [Attribution and scope](ATTRIBUTION.md)

A local adapter and guide for using an existing Google One billing-offer script with MuMuPlayer Pro on macOS. It prepares the environment, lists offers, and opens checkout. Any purchase must be confirmed manually on Android.

**[This X post by @zhuxufng154415](https://x.com/zhuxufng154415/status/2123040170132013071) is both the reference for this project and the distribution source of the original files.** The upstream script and embedded module are not included here.

## Delegate to an AI agent

Give [AI_TASK.md](AI_TASK.md) to an agent with access to your Mac's files and terminal. It includes Japanese and English copy-and-paste requests and instructions for setup and offer retrieval. The default task stops after listing offers; opening checkout requires an explicit request. Final purchase confirmation remains with you.

## Verification scope

| Item | Status |
| --- | --- |
| Environment | Apple Silicon Mac, Python 3.12, MuMu Android 12, Frida 16.5.9 |
| Original script | Offer listing and a 12-month free checkout were observed on November 20, 2026 |
| This adapter | Syntax and unit checks completed; a full device run has not been verified |
| Subscription or extension | Not verified; this adapter has no automatic confirmation or stacking feature |

Offer availability and eligibility vary by account, region, and date. A free trial may renew as a paid subscription: check the price and renewal date shown in your checkout.

## Requirements

- macOS with Python 3.12.
- MuMuPlayer Pro with a running Android instance, ADB debugging, and root access.
- Working Google Play Store and Google One, signed into the intended account.
- Your own authorized copy of the original `ultra0.py`.

Obtain the original file from the distribution source above and place it at `vendor/ultra0.py`. Versions with a different function interface may be incompatible. The source post and its download links could not be rechecked because access was restricted.

```text
google-ai-pro-macos/
├── mac.py
├── vendor/
│   └── ultra0.py  ← supplied locally; excluded from Git
└── Mac環境セットアップ.command
```

## Setup

```bash
git clone https://github.com/myan69/google-ai-pro-macos.git
cd google-ai-pro-macos
# Place your upstream file at vendor/ultra0.py first
bash Mac環境セットアップ.command
```

Setup creates `.venv` and installs Frida 16.5.9. ADB discovery checks the MuMu bundle, PATH, and Android SDK. Set `ADB_PATH` to use another ADB executable.

## Usage

Start Android in MuMu and open Play Store and Google One first.

| Launcher | Action |
| --- | --- |
| `0_環境チェック.command` | Prepare and check Google apps, ADB, and Frida |
| `1_オファー一覧.command` | Display offer periods and prices |
| `2_決済画面を開く.command` | Open the 12-month offer checkout; stop before confirmation |

Double-click a launcher in Finder or run the equivalent command:

```bash
.venv/bin/python mac.py check
.venv/bin/python mac.py list
.venv/bin/python mac.py checkout
```

Review the account, plan, free period, price, and renewal date. Confirm manually only if the terms match what you want. After subscribing, verify the subscription and next payment date in Google Play → Payments & subscriptions.

This adapter does not invoke upstream account-addition, card-registration, purchase-confirmation, or stacking helpers. The upstream file is still imported as executable Python code: supply only a file you trust.

## Troubleshooting

MuMu's ADB port can change after a restart. If trying ports 26624–26626 does not connect, specify the address shown by your instance. Also use `--serial` when multiple devices are connected.

```bash
# Replace this address with your instance's address
.venv/bin/python mac.py check --serial 127.0.0.1:26625
```

If Play Store stalls at its logo, restart Android and check that the Google apps open independently. The adapter stops Frida, starts the Google apps first, and then starts Frida with `--disable-preload`. Do not run other Frida tasks on the device simultaneously.

## Distribution and local data

This repository distributes only the newly written Mac adapter, launchers, documentation, and tests. It excludes upstream code, embedded APK/DEX files, credentials, payment data, offer tokens, runtime logs, and device captures. See [Attribution and scope](ATTRIBUTION.md) for upstream licensing information.

The adapter does not print or save offer tokens and suppresses upstream console output. Review the supplied upstream code for any behavior it performs itself. Environment preparation provisions root/Frida and the local billing module on Android. This adapter does not invoke the upstream proxy-clearing helper.

## Development

```bash
python3.12 -m unittest discover -s tests -v
python3.12 -m py_compile mac.py
```

The newly written files in this repository are available under the [MIT License](LICENSE). It does not cover separately supplied upstream files. This is not an official Google or MuMu tool.
