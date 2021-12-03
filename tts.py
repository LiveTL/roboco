from gtts import gTTS
import datetime

UNIX_EPOCH = datetime.datetime.utcfromtimestamp(0)

def tts(text):
    message = gTTS(text=text)
    filename = f'tts/{(datetime.datetime.utcnow() - UNIX_EPOCH).total_seconds() * 1000:.0f}.mp3' 
    message.save(filename) 
    return filename


if __name__ == "__main__":
    import time
    tts("""England när hon efterträdde sin bror, Edvard VI. Under denna process lät Maria bränna nästan 300 religiösa meningsmotståndare på bål, främst personer av reformert tro, vilket ledde till att hon började kallas Bloody Mary (Blodiga Maria). Marias ambition att återinföra katolicismen""")
    time.sleep(1)
    tts("""クロアジモドキはアジ科に属する海水魚であり、クロアジモドキ属を構成する唯一の種である。インド洋、太平洋西部の大陸棚でみられ、その分布域は西はアフリカ東海岸、東は日本やオーストラリア北部まで広がる""")
    time.sleep(1)
    tts("""奥古斯塔斯·奥斯利·斯坦利一世（1867年－1958年）是美国肯塔基州的一位政治家，曾担任该州第38任州长，还曾担任代表该州的联邦众议员和联邦参议员。1903至1915年，斯坦利成为代表肯塔基州第2国会选区的联邦众议员，并在这一期间赢得了进步改革者的声誉。1904年起，他呼吁对美国烟草公司展开反垄断调查，这场调查最终令联邦最高法院于1911年拆散了美国烟草公司。他的许多理念都纳入了《克莱顿反托拉斯法》。斯坦利的州长任期是肯塔基州进步时代的顶点。1958年8月12日，奥古斯塔斯·奥斯利·斯坦利一世在首都哥伦比亚特区逝世，享年91岁。""")
    time.sleep(1)
    tts("""고대 로마는 기원전 8세기경 이탈리아 중부의 작은 마을에서 발전하여 지중해를 아우르는 고대사상 거대한 제국을 이룬 문명이다. 기원전 7세기경 로마는 지역 중심지로 번영하던 도시국가였다. 기원전 500년경에는 왕정이 무너지고 귀족과 평민 계급이 공화정을 세웠다. 기원전 1세기 말 아우구스투스가 제정 시대를 열었다. 제정 초기의 로마 제국은 강력한 패권을 바탕으로 '팍스 로마나'로 불리는 태평성대를 구가하였으며, 라틴어 문학의 전성기를 이루었다. 트라야누스 황제 시대에 제국은 최대의 영토를 확보하여, 그 패권이 스코틀랜드에서 수단까지, 포르투갈의 대서양 연안에서 캅카스 지방까지 미쳤다. 하나의 세계를 이룬 이 거대한 제국 안에서, 그리스, 오리엔트, 셈족, 서유럽 등 고대 세계의 여러 문화가 융화되고 다시 확산되었다. 고대 로마는 서구 세계의 법, 정치, 전쟁, 예술, 문학 등의 분야의 발전에 크게 기여하였으며, 그 영향은 오늘날까지도 이어지고 있다. 이후 로마 제국은 이민족의 침략으로 쇠퇴기에 접어들었으며, 동로마와 서로마 제국으로 나뉘게 되었다.""")
    time.sleep(1)
    tts("""a cat and a dog""")