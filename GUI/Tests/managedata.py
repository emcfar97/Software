import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest

from ..managedata.ribbonView import Ribbon

# class test_tag_parsing(unittest.TestCase):
#     """
#     Test that it can parse tags properly
#     """
#     @classmethod
#     def setUpClass(self):
    
#         self.tag_parser = Ribbon(None, test=True).tag_parser

#     def test_empty_string(self):
#         'test empty string'
        
#         self.assertEqual(self.tag_parser(''), ' qwd')
        
#     def test_single_term(self):
#         'test single term'
        
#         self.assertEqual(self.tag_parser('a'), '+a')
        
#     def test_negation(self):
#         'test NOT operator'
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('NOT a'), '-a qwd')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('-a'), '-a qwd')
        
#     def test_and_operatior(self):
#         'test AND operator'
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a AND b'), '+a +b')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('-a AND b'), '-a +b')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a AND -b'), '+a -b')
            
#         with self.subTest():
#             self.assertEqual(self.tag_parser('-a AND -b'), '-a -b qwd')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a and b'), '+a +and +b')        
        
#     def test_or_operator(self):
#         'test OR operator'
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a OR b'), 'a b')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('-a OR b'), '-a b')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a OR -b'), 'a -b')
            
#         with self.subTest():
#             self.assertEqual(self.tag_parser('-a OR -b'), '-a -b qwd')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a or b'), '+a +or +b')
        
#     def test_wildcard_operator(self):
#         'test wildcard operator'
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a* b'), '+a* +b')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a b*'), '+a +b*')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('*a *b'), '+*a +*b')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a* b*'), '+a* +b*')
        
#     def test_parentheses(self):
#         'test parentheses'
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a OR b AND c'), '+(a b) +c')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('-a OR b AND c'), '+(-a b) +c')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a OR -b AND c'), '+(a -b) +c')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a OR b AND -c'), '+(a b) -c')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a* OR b AND c'), '+(a* b) +c')

#         with self.subTest():
#             self.assertEqual(self.tag_parser('a OR b* AND c'), '+(a b*) +c')
            
#         with self.subTest():
#             self.assertEqual(self.tag_parser('a OR b AND c*'), '+(a b) +c*')

#         with self.subTest():
#             self.assertEqual(self.tag_parser('-(a OR b) AND c'), '-(a b) +c')
        
#         with self.subTest():
#             self.assertEqual(self.tag_parser('-(a OR b) AND -c'), '-(a b) -c qwd')

#     @classmethod
#     def tearDownClass(self):
           
#         Qapp.quit()
    
class test_tag_parsing(unittest.TestCase):
    """
    Test that it can parse tags properly
    """
    
    @classmethod
    def setUpClass(self):
        
        import pyparsing as pp
        from pyparsing import pyparsing_common

        LPAR, RPAR = map(pp.Suppress, '()')
        expr = pp.Forward()
        operand = pyparsing_common.real | pyparsing_common.integer | pyparsing_common.identifier
        factor = operand | pp.Group(LPAR + expr + RPAR)
        term = factor + pp.ZeroOrMore(pp.oneOf('* AND ') + factor )
        expr <<= term + pp.ZeroOrMore(pp.oneOf('+ OR') + term )

        self.expr = pp.infixNotation(operand, [
            (pp.oneOf('- NOT'), 1, pp.opAssoc.RIGHT),
            (pp.oneOf('* AND'), 2, pp.opAssoc.LEFT),
            (pp.oneOf('+ OR'), 2, pp.opAssoc.LEFT),
            ])
    
    # def test_empty_string(self):
    #     'test empty string'
        
    #     self.assertEqual(self.expr.parseString(''), [''])
        
    def test_single_term(self):
        'test single term'
        
        self.assertEqual(self.expr.parseString('a').asList(), ['a'])
        
    def test_negation(self):
        'test NOT operator'
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('NOT a').asList(), [['NOT', 'a']]
                )
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('-a').asList(), [['-', 'a']]
                )
        
    def test_and_operatior(self):
        'test AND operator'
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a AND b').asList(), [['+a', 'AND', '+b']]
                )
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('-a AND b').asList(), [['-a', 'AND', '+b']]
                )
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a AND -b').asList(), [['+a', 'AND', '-b']]
                )
            
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('-a AND -b').asList(), [['-a', 'AND', '-b']]
                )
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a and b').asList(), [['a', 'and', 'b']]
                )        
        
    def test_or_operator(self):
        'test OR operator'
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a OR b').asList(), ['a', 'OR' 'b'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('-a OR b').asList(), ['-a', 'OR', 'b'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a OR -b').asList(), ['a', 'OR', '-b'])
            
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('-a OR -b').asList(), ['-a', 'or', '-b'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a or b').asList(), ['+a', 'or', '+b'])
        
    def test_wildcard_operator(self):
        'test wildcard operator'
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a* b').asList(), ['+a*', '+b'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a b*').asList(), ['+a', '+b*'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('*a *b').asList(), ['+*a', '+*b'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a* b*').asList(), ['+a*', '+b*'])
        
    def test_parentheses(self):
        'test parentheses'
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a OR b AND c').asList(), ['+', ['a', 'or', 'b'], 'AND', '+c'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('-a OR b AND c').asList(), '+', ['-a', 'OR' 'b'], 'AND', '+c')
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a OR -b AND c').asList(), ['+', ['a', 'OR', '-b'], 'AND', '+c'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a OR b AND -c').asList(), ['+', ['a', 'OR', 'b'], 'AND', '-c'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a* OR b AND c').asList(), ['+', ['a*', 'OR', 'b'], 'AND', '+c'])

        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a OR b* AND c').asList(), ['+', ['a', 'OR', 'b*'], 'AND', '+c'])
            
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('a OR b AND c*').asList(), ['+', ['a', 'OR', 'b'], 'AND', '+c*'])

        with self.subTest():
            self.assertEqual(
                self.expr.parseString('-(a OR b) AND c').asList(), ['-', ['a', 'OR', 'b'], 'AND', '+c'])
        
        with self.subTest():
            self.assertEqual(
                self.expr.parseString('-(a OR b) AND -c').asList(), ['-', ['a', 'OR', 'b'], 'AND', '-c'])

if __name__ == '__main__':
    
    Qapp = QApplication([])
    unittest.main()
    Qapp.exec_()