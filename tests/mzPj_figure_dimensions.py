import sys, unittest, struct, zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mzPj_plots import runner

def png():
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',200,100,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\0'*600)*100))+chunk(b'IEND',b'')

class Sizes(unittest.TestCase):
    def test_image(self):
        for kw,size in [({},(800,500)),({'width':600},(600,300)),({'height':240},(480,240)),({'width':610,'height':340},(610,340))]:
            n=runner();n['_pj_add_image'](png(),**kw);i=n['results']['items'][-1]
            self.assertEqual((i['width'],i['height']),size)
    def test_svg(self):
        for kw,size in [({},(800,500)),({'width':600},(600,300)),({'height':240},(480,240)),({'width':610,'height':340},(610,340))]:
            n=runner();n['_pj_add_svg']('<svg viewBox="0 0 200 100"><rect width="200" height="100"/></svg>',**kw);i=n['results']['items'][-1]
            self.assertEqual(i['type'],'Svg');self.assertIn('width="'+str(size[0])+'"',i['content']);self.assertIn('height="'+str(size[1])+'"',i['content'])
            self.assertNotIn('<details',i['content'])
    def test_validation(self):
        for value in [True,0,-1,2.5,'600',float('nan')]:
            n=runner()
            with self.assertRaises(ValueError):n['_pj_add_image'](png(),width=value)
            with self.assertRaises(ValueError):n['_pj_add_svg']('<svg/>',width=value)
        n=runner()
        with self.assertRaises(ValueError):n['_pj_add_svg']('<div/>')

if __name__=='__main__':unittest.main()
