# README.md

このappディレクトリ内にDjangoのプロジェクトを作成していく。

バージョン管理にはpipenvを用いることとする


## 1. (初回のみ)
はじめにpipenvを使える状態にする
基本的には、pythonが使える環境で
```bash:
$ pip install pipenv
```
を実行すれば使えるようになると思われる。

```bash:
$ pipenv --version
```
でバージョンが表示されればOK

---

<details>

<summary>WSL2環境でこれを書いているときに行ったこと</summary>

はじめに、
```bash:
$ sudo apt install pipenv
```

としたが、
```bash:
$ pipenv --version
```

を実行したときに、足りないものがいくつかあるといわれたため
```bash:
$ sudo apt remove pipenv
```

を行い、
```bash:
$ pip install pipenv
```

を行ったら、そのままではパスが通っていないらしく、WSLのパスはよくわからないので

この状態で
```bash:
$ sudo apt install pipenv
```

を行ったら、使えるようになったていた。
</details>

---



## 2. (初回のみ) 
仮想環境を作成する。
```bash:
$ pipenv --python 3.10
```

を実行する。今回はpythonは3.10系を使うことにする。
次回からは仮想環境に入るだけで良い

## 3. (毎回)
仮想環境に入る
```bash:
$ pipenv shell
```
で仮想環境に入ることができる。仮想環境に入ることによって、仮想環境にインストールしたものを使用することができる。


## 4. (必要に応じて)
実装にあたって必要なものをインストールする。
一番最初(仮想環境を作成したとき)に行う。
インストールすべきものが増えたときに再び行う必要がある。
仮想環境に入った状態で
```bash:
$ pipenv sync --dev
```
を行う。これを行うと、pipfile.lockの情報から、精度よくバージョンをそろえて必要なものがインストールされる。