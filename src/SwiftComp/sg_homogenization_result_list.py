import sg_result

class SGHomogenizationResultList(object):
    """SG Structural Result class"""
    def __init__(self):
        self.ResultList = []

    def setHomogenizationResult(self, SGHomogennizationResult):

        for i in range(len(self.ResultList)):
            if self.ResultList[i].result_name == SGHomogennizationResult.result_name:
                self.ResultList[i] = SGHomogennizationResult
                return
        
        self.ResultList.append(SGHomogennizationResult)


class SGHomogenizationResult(sg_result.SGResult):
    '''SG Extract Result class'''
    def __init__(self):
        sg_result.SGResult.__init__(self)
