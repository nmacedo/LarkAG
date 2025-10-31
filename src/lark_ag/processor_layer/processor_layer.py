from lark import Lark

class ProcessorLayer:
    def __init__(self, grammar, interpreter):
        self.parser = Lark(grammar)
        self.interpreter = interpreter

    def process(self, input):
        tree = self.parser.parse(input)
        self.interpreter.visit(tree)
        return tree
    