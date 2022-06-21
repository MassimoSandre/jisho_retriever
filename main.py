from jisho_retriever import JishoRetriever

ret = JishoRetriever(information=True,block_size=80,pause=0.1)

DOWNLOAD_FROM_LEVEL = 3
DOWNLOAD_UNTIL_LEVEL = 1

for i in range(5-DOWNLOAD_FROM_LEVEL,5-DOWNLOAD_UNTIL_LEVEL + 1):
    x = ret.generate_info_json_by_level(5-i)

    

