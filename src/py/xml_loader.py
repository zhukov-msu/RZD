
import xml.etree.cElementTree as ET
from rail import *
from coord import *
import codecs

def load(os_path, skip_back_motion=True):
    # print(os_path)
    parser = ET.XMLParser(encoding="cp1251")
    with codecs.open(os_path, 'r',encoding='cp1251') as f:
        tree = ET.parse(os_path, parser=parser)
    # tree = ET.parse(os_path)
    root = tree.getroot()
    if root.tag == "Path":
        atr = root.attrib
    else:
        return 0
    path = Path(dir_name=atr['DirName'], dir_code=atr['DirCode'], date=atr['Date'], move_dir=False if atr['MoveDir'] == '0' else True,
                rails=[])

    for r_num, rail in enumerate(root):
        atr = rail.attrib
        r = Rail(False if atr['thread'] == 'Left' else True,path.move_dir)
        path.rails.append(r)
        for i, point in enumerate(rail):
            if point.tag == 'P':
                c = Coord(str_data=point.attrib['x'])
                path.rails[r_num].points.append(Point(coord=c))
                for ch in point:
                    signals = [(int(v.attrib['A']), int(v.attrib['D'])) for v in ch.findall('v')]
                    path.rails[r_num].points[i].channels[int(ch.attrib['N'])] = Channel(int(ch.attrib['N']), signals)
            elif point.tag == 'Notes':
                for note in point:
                    c = Coord(str_data=note.attrib['x'])
                    n = note.attrib['comment']
                    r.add_note(c, n)
    return path

def xml_dump(path, os_path):
    # type: (Path, str) -> object
    root = ET.Element("Path", DirName=path.dir_name, Date=path.date, MoveDir='1' if path.move_dir else '0',
                      DirCode=path.dir_code)
    for rail in path.rails:
        notes = []
        tree_rail = ET.SubElement(root, 'Rail', thread='Right' if rail.right else 'Left')
        for pnum, point in enumerate(rail.points):
            xml_point = ET.SubElement(tree_rail, 'P',
                                      x=str(point.coord.km)+'|'+str(point.coord.pk)+'|'+str(point.coord.mm),
                                      b='0', i=str(pnum))
            for num, channel in point.channels.items():
                xml_ch = ET.SubElement(xml_point, 'C', N=str(num))
                for v in channel.signals:
                    xml_v = ET.SubElement(xml_ch, 'v', A=str(v[0]), D=str(v[1]))
            if point.note:
                notes += [(str(point.coord.km)+'|'+str(point.coord.pk)+'|'+str(point.coord.mm), point.note)]

        xml_notes = ET.SubElement(tree_rail, 'Notes')
        for note in notes:
            xml_note = ET.SubElement(xml_notes, 'Note', comment=str(note[1]), x=str(note[0]))
    tree = ET.ElementTree(root)
    tree.write(os_path, encoding='utf-8')


