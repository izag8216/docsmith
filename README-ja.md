# docsmith

[![header](https://raw.githubusercontent.com/izag8216/docsmith/main/docs/docsmith-header.svg)](https://github.com/izag8216/docsmith)

**軽量なdocstringからMarkdown APIドキュメント生成ツール**

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-29A745?style=for-the-badge&logo=license&logoColor=white)
![PyPI](https://img.shields.io/badge/PyPI-v0.1.0-4B8BBE?style=for-the-badge&logo=pypi&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-80%25%2B-FF6B6B?style=for-the-badge&logo=test&logoColor=white)

## 概要

docsmithはPythonの`ast`モジュールを使用して、コード**をインポートせずに**docstring、型注釈、コード構造を抽出します。Jinja2テンプレートを使用してカスタマイズ可能なクリーンマルチドキュメントを描画し、Google、NumPy、Sphinxのdocstring形式をサポートしています。

Sphinx（reStructuredTextと複雑な設定が必要）や`pdoc`（コードをインポートして副作用が発生する可能性がある）とは異なり、docsmithはAPIドキュメントを生成するための軽量で副作用のないソリューションを提供します。

## インストール

```bash
pip install docsmith
```

ソースからインストール:

```bash
git clone https://github.com/izag8216/docsmith.git
cd docsmith
pip install -e .
```

## クイックスタート

### ディレクトリのドキュメントを生成

```bash
docsmith generate ./src --format google --output docs/api.md
```

### 单一モジュールのドキュメントを生成

```bash
docsmith single path/to/module.py --output api.md
```

### ライブリロードでサーブ

```bash
docsmith serve ./src --port 8090 --watch
```

### ドキュメントカバレッジを確認

```bash
docsmith diff old_docs.md new_docs.md --check-coverage
```

## 機能

- **ASTベースのパース**: コードをインポートせずにdocstringを抽出（副作用ゼロ）
- **マルチフォーマットサポート**: Google、NumPy、Sphinx docstring形式
- **Jinja2テンプレート**: 完全カスタマイズ可能な出力テンプレート
- **カバレッジ diff**: API surfaceの変更を比較
- **ウォッチモード**: ファイル変更時に自動再生成

## サポートされているDocstring形式

### Google形式

```python
def func(arg1, arg2):
    """ Summary line.

    Args:
        arg1: arg1の説明。
        arg2: arg2の説明。

    Returns:
        戻り値の説明。
    """
```

### NumPy形式

```python
def func(arg1, arg2):
    """
    Summary line.

    Parameters
    ----------
    arg1 : type
        arg1の説明。
    arg2 : type
        arg2の説明。

    Returns
    -------
    type
        戻り値の説明。
    """
```

### Sphinx形式

```python
def func(arg1, arg2):
    """
    Summary line.

    :param arg1: arg1の説明。
    :param arg2: arg2の説明。
    :returns: 戻り値の説明。
    """
```

## カスタムテンプレート

Jinja2テンプレートを使用してカスタム出力を生成:

```bash
docsmith generate ./src --template docs/my_template.j2 --output docs/api.md
```

## 設定

設定ファイルを初期化:

```bash
docsmith init
```

これにより、カレントディレクトリに`.docsmith.toml`が作成されます。

## CLIコマンド

| コマンド | 説明 |
|---------|------|
| `generate` | Pythonソースファイルのドキュメントを生成 |
| `single` | 单一モジュールのドキュメントを生成 |
| `serve` | ライブリロードでドキュメントをサーブ |
| `diff` | 2つのドキュメントファイルをAPI surface変更のために比較 |
| `init` | docsmith設定ファイルを初期化 |

## 開発

### セットアップ

```bash
pip install -e ".[dev]"
```

### テスト実行

```bash
pytest
```

### カバレッジ付きで実行

```bash
pytest --cov=docsmith --cov-report=term-missing --cov-fail-under=80
```

### リント

```bash
black src/
ruff check src/
```

## ライセンス

MITライセンス - 詳細は[LICENSE](LICENSE)をご覧ください。

## リンク

- [ドキュメント](docs/)
- [APIリファレンス](docs/api.md)
- [使い方ガイド](docs/usage.md)