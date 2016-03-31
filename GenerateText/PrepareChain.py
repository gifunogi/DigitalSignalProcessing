"""
以下ソースコード流用部分
"""

# coding:utf-8

u"""
与えられた文書からマルコフ連鎖のためのチェーン（連鎖）を作成して、DBに保存するファイル
"""

import unittest

import sys
import re
import MeCab
import sqlite3
import codecs
from collections import defaultdict


def main():
	if len(sys.argv) > 1:
		data = sys.argv[1]
	else:
		".\lyrics.txt"
	f = codecs.open(data, "r", "cp932")
	text = f.read()

	chain = PrepareChain(text)
	triplet_freqs = chain.make_triplet_freqs()
	chain.save(triplet_freqs, True)

	f.close()


class PrepareChain(object):
	u"""
	チェーンを作成してDBに保存するクラス
	"""
	BEGIN = u"__BEGIN_SENTENCE__"
	END = u"__END_SENTENCE__"

	DB_PATH = "..\chain.db"
	DB_SCHEMA_PATH = "..\schema.sql"

	def __init__(self, text):
		u"""
		初期化メソッド
		@param text チェーンを生成するための文章
		"""
		if isinstance(text, str):
			text = text.decode("utf-8")
		self.text = text

		# 形態素解析用タガー
		self.tagger = MeCab.Tagger('-Ochasen')

	def make_triplet_freqs(self):
		u"""
		形態素解析から3つ組の出現回数まで
		@return 3つ組とその出現回数の辞書 key: 3つ組（タプル） val: 出現回数
		"""
		# 長い文章をセンテンス毎に分割
		sentences = self._divide(self.text)

		# 3つ組の出現回数
		triplet_freqs = defaultdict(int)

		# センテンス毎に3つ組にする
		for sentence in sentences:
			# 形態素解析
			morphemes = self._morphological_analysis(sentence)
			# 3つ組をつくる
			triplets = self._make_triplet(morphemes)
			# 出現回数を加算
			for (triplet, n) in triplets.items():
				triplet_freqs[triplet] += n

		return triplet_freqs

	def _divide(self, text):
		u"""
		「。」や改行などで区切られた長い文章を一文ずつに分ける
		@param text 分割前の文章
		@return 一文ずつの配列
		"""
		# 改行文字以外の分割文字（正規表現表記）
		delimiter = u"。|．|\."

		# 全ての分割文字を改行文字に置換（splitしたときに「。」などの情報を無くさないため）
		text = re.sub(ur"({0})".format(delimiter), r"\1\n", text)

		# 改行文字で分割
		sentences = text.splitlines()

		# 前後の空白文字を削除
		sentences = [sentence.strip() for sentence in sentences]

		return sentences

	def _morphological_analysis(self, sentence):
		u"""
		一文を形態素解析する
		@param sentence 一文
		@return 形態素で分割された配列
		"""
		morphemes = []
		sentence = sentence.encode("utf-8")
		node = self.tagger.parseToNode(sentence)
		while node:
			if node.posid != 0:
				morpheme = node.surface.decode("utf-8")
				morphemes.append(morpheme)
			node = node.next
		return morphemes

	def _make_triplet(self, morphemes):
		u"""
		形態素解析で分割された配列を、形態素毎に3つ組にしてその出現回数を数える
		@param morphemes 形態素配列
		@return 3つ組とその出現回数の辞書 key: 3つ組（タプル） val: 出現回数
		"""
		# 3つ組をつくれない場合は終える
		if len(morphemes) < 3:
			return {}

		# 出現回数の辞書
		triplet_freqs = defaultdict(int)

		# 繰り返し
		for i in xrange(len(morphemes)-2):
			triplet = tuple(morphemes[i:i+3])
			triplet_freqs[triplet] += 1

		# beginを追加
		triplet = (PrepareChain.BEGIN, morphemes[0], morphemes[1])
		triplet_freqs[triplet] = 1

		# endを追加
		triplet = (morphemes[-2], morphemes[-1], PrepareChain.END)
		triplet_freqs[triplet] = 1

		return triplet_freqs

	def save(self, triplet_freqs, init=False):
		u"""
		3つ組毎に出現回数をDBに保存
		@param triplet_freqs 3つ組とその出現回数の辞書 key: 3つ組（タプル） val: 出現回数
		"""
		# DBオープン
		con = sqlite3.connect(PrepareChain.DB_PATH)

		# 初期化から始める場合
		if init:
			# DBの初期化
			with open(PrepareChain.DB_SCHEMA_PATH, "r") as f:
				schema = f.read()
				con.executescript(schema)

			# データ整形
			datas = [(triplet[0], triplet[1], triplet[2], freq) for (triplet, freq) in triplet_freqs.items()]

			# データ挿入
			p_statement = u"insert into chain_freqs (prefix1, prefix2, suffix, freq) values (?, ?, ?, ?)"
			con.executemany(p_statement, datas)

		# コミットしてクローズ
		con.commit()
		con.close()

	def show(self, triplet_freqs):
		u"""
		3つ組毎の出現回数を出力する
		@param triplet_freqs 3つ組とその出現回数の辞書 key: 3つ組（タプル） val: 出現回数
		"""
		for triplet in triplet_freqs:
			print "|".join(triplet), "\t", triplet_freqs[triplet]


"""
以上ソースコード流用部分
"""


if __name__ == '__main__':
	# unittest.main()
	main()
