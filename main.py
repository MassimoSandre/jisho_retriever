from jisho_retriever import JishoRetriever

ret = JishoRetriever(information=True,block_size=80,pause=0)

# DOWNLOAD_FROM_LEVEL = 5
# DOWNLOAD_UNTIL_LEVEL = 1

# for i in range(5-DOWNLOAD_FROM_LEVEL,5-DOWNLOAD_UNTIL_LEVEL + 1):
#     x = ret.generate_kanji_info_json_by_level(5-i)

# x = ret.get_kanji_list_by_level()
# import json
# file = open("output/complete_kanji_list.json","w", encoding="utf8")
# json.dump(x, file, indent=4,ensure_ascii=False)
# file.close()

ret.generate_words_info_json_by_level(5)