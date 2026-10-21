#Consists of the AGParser, Interpreter Generator and calls to the Lark Parser

# AG -> This module -> Interpreter + Lark Parser
import json
from .ag_parser import AGParser, AGTransformer
from .interpreter_generator import InterpreterGenerator
from lark.visitors import Interpreter

class GeneratorLayer:
    def __parse_ag__(self) -> None:
        parser = AGParser()
        transformer = AGTransformer()
        tree = parser.parse(self.grammar)
        res=transformer.transform(tree)
        self.__cfg__=res['cfg']
        self.__attributes__=res['attributes']
        self.__semantics__=res['semantics']
        self.__symbol_table__=res['symbolTable']

    def __generate_interpreter__(self) -> None:
        self.interpreter_generator = InterpreterGenerator(self.__semantics__, self.__attributes__, self.__symbol_table__)

    def __init__(self, grammar) -> None:
        self.grammar = grammar
        self.__parse_ag__()
        self.__generate_interpreter__()
        
    def print_contents(self, option=None) -> None:
        if(option == None):
            print(self.__cfg__)
            print(json.dumps(self.__attributes__, indent=2))
            print(json.dumps(self.__semantics__, indent=2))
        elif(option == 'cfg'):
            print(self.__cfg__)
        elif(option == 'attributes'):
            print(json.dumps(self.__attributes__, indent=2))
        elif(option == 'semantics'):
            print(json.dumps(self.__semantics__, indent=2))
    
    def getCFG(self) -> str:
        return self.__cfg__
    
    def getInterpreterFile(self) -> str:
        return self.interpreter_generator.generateFile()
    
    def getInterpreter(self) -> Interpreter:
        return self.interpreter_generator.generateInterpreter()
    
    def getRootLevelAttributes(self) -> dict:
        return self.__attributes__.get('start', {})