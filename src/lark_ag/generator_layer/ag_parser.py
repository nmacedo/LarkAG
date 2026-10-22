from importlib import resources
import json
from lark import Lark, Token
from lark.visitors import Transformer

from ..errors import AGDefinitionError


class AGTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.cfg = ''
        self.attributeDict = {}
        self.semanticDict = {}

        self.symbolTable = {}
        self.hasIgnore = False

    def start(self, tree):
        # Whitespace is ignored by default, unless the grammar declares its own %ignore
        cfg = self.cfg if self.hasIgnore else self.cfg + "\n%import common.WS\n%ignore WS\n"
        return {'cfg': cfg, 'attributes': self.attributeDict, 'semantics': self.semanticDict, 'symbolTable': self.symbolTable}
    

    # SYNTAX
    def rule(self, tree):
        string=tree[0].value + tree[1]
        if len(tree) == 4:
            string += tree[3]
        
        auxArray = []
        for idx, x in enumerate(tree[-1]['cfg']):
            auxArray.append(x+" -> "+tree[0].value+"_"+str(idx))
        
        string += ' : ' + " | ".join(auxArray)
        self.cfg += string + '\n'

        self.semanticDict[tree[0].value] = tree[-1]['semantics']
        self.symbolTable[tree[0].value] = tree[-1]['symbols']

        if tree[0].value not in self.symbolTable[tree[0].value]:
            self.symbolTable[tree[0].value].append(tree[0].value)
        return string
    
    def rule_params(self, tree):
        if tree[0] == None:
            return ''
        else:
            return '{' + ', '.join([x.value for x in tree]) + '}'
    
    def token(self, tree):
        string = tree[0].value + tree[1]

        if len(tree) == 4:
            string += tree[3]
        
        string += ' : ' + " | ".join(tree[-1]['cfg'])
        self.cfg += string + '\n'

        return string

    def ignore(self, tree):
        self.hasIgnore = True
        directive = '%ignore ' + ' | '.join(tree[0]['cfg'])
        self.cfg += directive + '\n'
        return directive
    
    
    def import_path(self, tree):
        return ''.join(x if isinstance(x, str) else x.value for x in tree)

    def name_list(self, tree):
        return '(' + ', '.join(tree) + ')'

    def import_directive(self, tree):
        directive = '%import ' + tree[0]
        if tree[1] is not None:
            directive += ' -> ' + tree[1]
        self.cfg += directive + '\n'
        return directive

    def multi_import(self, tree):
        directive = '%import ' + tree[0] + ' ' + tree[1]
        self.cfg += directive + '\n'
        return directive

    def declare(self, tree):
        directive = '%declare ' + ' '.join(tree)
        self.cfg += directive + '\n'
        return directive

    def override_rule(self, tree):
        # rule() already appended the definition as the last cfg line
        self.cfg = self.cfg[:-len(tree[0]) - 1] + '%override ' + tree[0] + '\n'
        return '%override ' + tree[0]

    def token_params(self, tree):
        if tree[0] == None:
            return ''
        else:
            return '{' + ', '.join([x.value for x in tree]) + '}'
        
    def priority(self, tree):
        return '.' + tree[0].value

    def priority(self, tree):
        return '.' + tree[0].value
    
    def expansions(self, tree):
        flat_symbols = []
        for x in tree:
            if x['symbols'] != None:
                flat_symbols += x['symbols']

        dict= {'cfg': [x['cfg'] for x in tree],'semantics':[],'symbols':list(set(flat_symbols))}

        for x in tree:
            if(x['semantics']!=None):
                newDict = {}
                newDict['semantics'] = x['semantics']
                newDict['rhs'] = x['cfg']
                dict['semantics'].append(newDict)

        return dict
    
    def expansions_token(self, tree):
        return self.expansions(tree)
    
    def alias(self, tree):
        if len(tree) == 2:
            return {
                'cfg': tree[0]['cfg'],
                'symbols': tree[0]['symbols'],
                'semantics': tree[1],
            }
        return {
            'cfg': tree[0]['cfg'],
            'symbols': tree[0]['symbols'],
            'semantics': None,
        }
        
    def alias_token(self, tree):
        return {'cfg': tree[0], 'symbols': None, 'semantics': None}
        
    def expansion(self, tree):
        symbols = []
        # For each element in the tree, if it is of type Token(symbol), add it to the symbols list
        for x in tree:
            if type(x['tree'][0]) == Token:
                symbols.append(x['tree'][0].value)
            elif isinstance(x['tree'][0], dict):
                symbols += x['tree'][0]['symbols']
        
        # Return the cfg of all the elements in the tree and the symbols list
        return {'cfg':' '.join([x['cfg'] for x in tree]), 'symbols':symbols}
    
    def expr(self, tree):
        atom = tree[0]['cfg'] if isinstance(tree[0], dict) else tree[0]
        if tree[1] == None:
            return {'cfg':atom, 'tree':tree}
        elif tree[1].type == 'NUMBER':
            string = atom + '~' + tree[1].value
            if len(tree) == 3 and tree[2] != None:
                string += '..' + tree[2].value
            return {'cfg':string, 'tree':tree}
        elif len(tree) == 2:
            return {'cfg':atom + tree[1].value, 'tree':tree}
        
    def atom(self, tree):
        return tree[0]
    
    def group(self, tree):
        return {'cfg': '(' + ' | '.join(tree[0]['cfg']) + ')', 'symbols': tree[0]['symbols']}
    
    def maybe(self, tree):
        return {'cfg': '[' + ' | '.join(tree[0]['cfg']) + ']', 'symbols': tree[0]['symbols']}
    
    def value(self, tree):
        return tree[0]
    
    def literal_range(self, tree):
        return tree[0].value + '..' + tree[1].value
    
    def name(self, tree):
        return tree[0]
    
    def literal(self, tree):
        return tree[0].value
    
    def template_usage(self, tree):
        return tree[0] + '{' + ', '.join(tree[1:]) + '}'


    # SEMANTICS
    def semantics(self, tree):
        list=[]
        for x in tree:
            if(x!=None):
                list= list + x

        return list

    def attributes(self, tree):
        for attribute in tree[2:]:
            attribute['inheritance']=tree[0].value
            if (tree[1] in self.attributeDict):
                if(attribute['name'] not in self.attributeDict[tree[1]]):
                    self.attributeDict[tree[1]].update({attribute['name']: attribute})
                else:
                    raise AGDefinitionError(f"Attribute '{attribute['name']}' is already defined for '{tree[1]}'")
            else:
                self.attributeDict[tree[1]] = {attribute['name']: attribute}
        
        return {tree[1]: tree[2:]}

    def attribute(self, attribute):
        return {'name': attribute[0], 'type': attribute[1], 'used': 0}
    
    def nt_id(self, tree):
        return tree[0].value
    
    def att_id(self, tree):
        return tree[0].value
    
    def type(self, tree):
        if len(tree) == 1:
            return tree[0].value
        return tree[0].value + '[' + ', '.join(tree[1:]) + ']'

    def evaluations(self, tree):
        return tree

    def evaluation(self, tree):
        return {"code":tree[0] +" = "+ tree[1], "type":"er"}
    
    def conditions(self, tree):
        return tree

    def condition(self, tree):
        message=tree[1].value if len(tree) > 1 else "Semantic error"
        return {"code":tree[0].strip(), "message": message.strip(" \"'"), "type":"cc"}
    
    def translations(self, tree):
        return tree
    
    def translation(self, tree):
        return {"code":tree[0] + '(' + ', '.join([x for x in tree[1:]]) + ')', "type":"tr"}
    
    def fun_id(self, tree):
        return tree[0].value
    
    def attribute_call(self, tree):
        if len(tree) == 2:
            return tree[0] + '.' + tree[1]
        elif len(tree) == 3:
            return tree[0] + '[' + tree[1].value + '].' + tree[2]
        
    def CODE_EXPR(self, tree):
        return tree.rstrip(';')


class AGParser:
    def __load_grammar__(self):
        # Open the grammar.lark file inside this folder(make sure it works when run from anywhere)
        with resources.path('lark_ag.generator_layer', 'grammar.lark') as path:
            with open(path, 'r') as file:
                return file.read()
        
    def __init__(self):
        self.parser = Lark(self.__load_grammar__(), start='start', parser='lalr')

    def parse(self, text):
        tree = self.parser.parse(text)
        return tree