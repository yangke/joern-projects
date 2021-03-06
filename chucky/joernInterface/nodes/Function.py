from joernInterface.JoernInterface import jutils
from joernInterface.nodes.Node import Node
from joernInterface.nodes.Callee import Callee
from joernInterface.nodes.Identifier import Identifier
from joernInterface.nodes.ASTNode import ASTNode
from joernInterface.nodes.Symbol import Symbol


class Function(Node):
    
    def __init__(self, node_id, properties = None):
        Node.__init__(self, node_id, properties) 

    def __str__(self):
        return '{}'.format(self.name)
    
    def __eq__(self, other):
           return self.node_id == other.node_id
       
    def symbols(self):
        lucene_query = 'functionId:"{}" AND type:Symbol'.format(self.node_id)
        symbols = jutils.lookup(lucene_query)
        return map(lambda x : Symbol(x[0], x[1].get_properties()), symbols)
    
    def callers(self):
        """ All Caller of this function """
        lucene_query = 'type:Callee AND code:"{}"'.format(self.get_property('name'))
        traversal = 'transform{ g.v(it.functionId) }'
        callers = set()
        results = jutils.lookup(lucene_query, traversal = traversal)
        if results:
            for node_id, node in results:
                callers.add(Function(node_id, node))
        return list(callers) 
    
    def callees(self):
        lucene_query = 'functionId:"{}" AND type:Callee'.format(self.node_id)
        result = jutils.lookup(lucene_query)
        return map(lambda x : Callee(x[0], x[1].get_properties()), result)

    def parameters(self):
        lucene_query = 'functionId:"{}" AND type:Identifier'.format(self.node_id)
        traversal = 'filterParameters()'
        symbols = jutils.lookup(lucene_query, traversal = traversal)
        return map(lambda x : Identifier(x[0], x[1].get_properties()), symbols)

    def variables(self):
        lucene_query = 'functionId:"{}" AND type:Identifier'.format(self.node_id)
        traversal = 'filterVariables()'
        symbols = jutils.lookup(lucene_query, traversal = traversal)
        return map(lambda x : Identifier(x[0], x[1].get_properties()), symbols)

    def api_symbol_nodes(self):
        traversal = 'functionToAPISymbolNodes()'
        result = jutils.raw_lookup(self.node_selection, traversal)
        return map(lambda x : ASTNode(x[0], x[1].get_properties()), result)

    
    def symbolsByName(self, code):
        lucene_query = 'type:Symbol AND functionId:"{}" AND code:"{}"'
        lucene_query = lucene_query.format(self.node_id, code)
        result = jutils.lookup(lucene_query)
        return Symbol(result[0][0], result[0][1].get_properties())

    
    def calleesByName(self, code):
        lucene_query = 'type:Callee AND functionId:"{}" AND code:"{}"'
        lucene_query = lucene_query.format(self.node_id, code)
        result = jutils.lookup(lucene_query)
        return map(lambda x : Callee(x[0], x[1].get_properties()), result)
    
    @property
    def name(self):
        return self.get_property('name')

    @property
    def signature(self):
        return self.get_property('signature')
    def location(self):
        id = self.node_id
        query = """g.v(%s)
        .ifThenElse{it.type == 'Function'}{
         it.sideEffect{loc = it.location; }.functionToFile()
         .sideEffect{filename = it.filepath; }
         }{
           it.ifThenElse{it.type == 'Symbol'}
           {
             it.transform{ g.v(it.functionId) }.sideEffect{loc = it.location; }
             .functionToFile()
             .sideEffect{filename = it.filepath; }
            }{
             it.ifThenElse{it.type == 'BasicBlock'}{
               it.sideEffect{loc = it.location}.basicBlockToAST()
               .astNodeToFunction().functionToFile()
               .sideEffect{filename = it.filepath; }
             }{
              // AST node
              it.astNodeToBasicBlock().sideEffect{loc = it.location; }
              .basicBlockToAST().astNodeToFunction()
              .functionToFile().sideEffect{filename = it.filepath; }
              }
           }
        }.transform{ filename + ':' + loc }
        """ % (id)
        y=jutils.joern.runGremlinQuery(query)
        for x in y:
            return x    
