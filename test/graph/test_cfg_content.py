__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.graph.cfg_content import CFGContent
from program_slicing.graph.cdg_content import CDGContent
from program_slicing.graph.cdg_content import CDG_CONTENT_TYPE_OBJECT


class CGFContentTestCase(TestCase):

    def test_constructor(self):
        pass
     
    def test_is_empty(self):
        pass
        
    def test_append(self):
        pass
    
    def test_content(self):
        cdg_content_a = CDGContent("a", CDG_CONTENT_TYPE_OBJECT, (0, 0))
        cdg_content_b = CDGContent("b", CDG_CONTENT_TYPE_OBJECT, (1, 1))
        cdg_content_c = CDGContent("c", CDG_CONTENT_TYPE_OBJECT, (2, 2))
        a = CFGContent(content=[cdg_content_a, cdg_content_b])
        self.assertFalse(a.is_empty())
        self.assertEqual([cdg_content_a, cdg_content_b], a.content)
        a.append(cdg_content_c)
        self.assertEqual([cdg_content_a, cdg_content_b, cdg_content_c], a.content)
        self.assertEqual(cdg_content_a, a.get_root())
        b = CFGContent()
        self.assertTrue(b.is_empty())
