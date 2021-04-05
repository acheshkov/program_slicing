__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/22'

from unittest import TestCase

from program_slicing.decomposition import slicing
from program_slicing.graph.parse import LANG_JAVA


class SlicingTestCase(TestCase):

    def test_decompose_dir(self):
        pass

    def test_decompose_file(self):
        pass

    def test_decompose_code(self):
        source_code = "class A {" \
                      "    void main() {" \
                      "        int a = 0;" \
                      "        int b = 10;" \
                      "        a = b;" \
                      "        b += a;" \
                      "    }" \
                      "}"
        res = [decomposition for decomposition in slicing.decompose_code(source_code, LANG_JAVA)]
        self.assertEqual(2, len(res))
