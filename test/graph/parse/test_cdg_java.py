__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.graph.parse.cdg_java import parse
from program_slicing.graph.cdg_content import \
    CDG_CONTENT_TYPE_FUNCTION, \
    CDG_CONTENT_TYPE_VARIABLE, \
    CDG_CONTENT_TYPE_ASSIGNMENT, \
    CDG_CONTENT_TYPE_CALL, \
    CDG_CONTENT_TYPE_STATEMENTS, \
    CDG_CONTENT_TYPE_BRANCH, \
    CDG_CONTENT_TYPE_LOOP, \
    CDG_CONTENT_TYPE_BREAK, \
    CDG_CONTENT_TYPE_GOTO, \
    CDG_CONTENT_TYPE_OBJECT, \
    CDG_CONTENT_TYPE_EXIT


class CDGJavaTestCase(TestCase):

    def test_parse(self):
        pass
