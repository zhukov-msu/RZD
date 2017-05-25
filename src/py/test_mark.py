from rail import Rail, Path
from xml_loader import load, xml_dump

railway = load('D:/CMC_MSU/master/science/data/21/21-35.a11.a11.xml')
railway.rails[0].mark_rail(min_amplitude=4)
railway.rails[1].mark_rail(min_amplitude=4)
xml_dump(railway, 'test.xml')
# print(len(list_parts))