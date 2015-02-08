
import os.path
#from joerntools.KNN import KNN
from KNN import KNN
from joernInterface.nodes.Function import Function

"""
Employs an embedder to first embed a set of entities (e.g., functions)
and then determine the k nearest neighbors to a given entity.
"""
class NearestNeighborSelector:
    
    """
    @param basedir: directory for temporary files. We assume
                    that the cache lives at $basedir/cache
    
    @param embeddingDir: the directory to store the embedding.    
    """
    
    def __init__(self, basedir, embeddingDir):
        self.embeddingDir = embeddingDir
        self.k = 10
        self.cachedir = os.path.join(basedir, "cache")
    
    def setK(self, k):
        self.k = k+1
    
    """
    Get nearest neighbors of entity in set of allEntities
    """
    def getNearestNeighbors(self, entity, allEntities):
        
        if len(allEntities) < self.k:
            return []

        return self._nearestNeighbors(entity, self.k, allEntities)
    
    
    def _nearestNeighbors(self, entity, k, allEntities):
        
        nodeId = entity.getId()
        
        limit=[str(e.getId()) for e in allEntities]
        
        knn = KNN()
        knn.setEmbeddingDir(self.cachedir)
        knn.setK(k)
        knn.setLimitArray(limit)
        knn.initialize()
        
        ids,similarities = knn.getNeighborsFor(str(nodeId))
        if str(nodeId) not in ids:
            ids.pop()
            ids.append(str(nodeId))
        return [Function(i) for i in ids],similarities
    
    '''
    def _createLimitFile(self, entities):
        filename = os.path.join(self.cachedir, 'limitfile')
        f = file(filename, 'w')
        f.writelines([str(e.getId()) + '\n' for e in entities] )
        f.close()
        return filename
    '''
            
