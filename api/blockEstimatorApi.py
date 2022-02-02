import os
import requests
from dotenv import load_dotenv
config = load_dotenv("local.env")
SERVER_URL = os.getenv("SERVER_URL").rstrip('/')

class BlockEstimator:
    '''Reverse search for a block based on the timestamp'''
    def __init__(self, blockRate=53, tolerance=100 ):
        self.blockRate = blockRate
        self.tolerance = tolerance
        self.prevBlockHeight = None
        self.maxIterations = 10
        self.iterations = 0
        self.SERVER_URL = SERVER_URL
        self.error = 999999
        pass

    def getBlock(self, height=None):
        '''returns topmost block if height is not provided'''
        if height is None:
            return requests.get(f"{self.SERVER_URL}/ledger/list/blocks?limit=1").json()
        return requests.get(f"{self.SERVER_URL}/ledger/get/block?height={height}").json()

    # a function that returns the block height based on the timestamp
    def estimateBlockFromTimestamp(self, timestamp, lastBlockHeight=None, lastBlockTimestamp=None):
        # inputs > timestamp , errorFactor, toleranceFactor and blockRate to estimate the block height
        # perform error correction if block is not found
        if lastBlockTimestamp is None or lastBlockHeight is None:
            latestBlockResponse = self.getBlock()
            lastBlockTimestamp = latestBlockResponse['result'][0]['timestamp']
            lastBlockHeight = latestBlockResponse['result'][0]['height']
        timeDiff = lastBlockTimestamp - timestamp
        noOfBlocks = timeDiff // self.blockRate
        estimatedBlock = lastBlockHeight - noOfBlocks  # blockRate
        return estimatedBlock

    # create a dictionary with checkpoints and their corresponding block heights and timestamps
    # checkpoints = {}
    def reduceError(self, error, timestamp, eb, tsActual):
        if(abs(error) >= self.tolerance):
            self.prevBlockHeight = eb
            # start estimating from the last block
            eb = self.estimateBlockFromTimestamp(
                timestamp, lastBlockHeight=eb, lastBlockTimestamp=tsActual)
            print("curr eb", eb)
            error = tsActual - timestamp
            tsActual = self.getBlock(eb)["result"]["timestamp"]
            print("new error", error)
            self.error = error

            # break if max iterations reached
            self.iterations += 1
            if(self.iterations > self.maxIterations):
                print("iterations exceeded")
                return eb

            eb = self.reduceError(error, timestamp, eb, tsActual)
        return eb

    def findBlockFromTimestamp(self, tsInput):
        self.iterations = 0
        eb = self.estimateBlockFromTimestamp(tsInput)
        tsActual = self.getBlock(eb)["result"]["timestamp"]
        error = tsActual - tsInput
        acceptedBlock = self.reduceError(error, tsInput, eb, tsActual)
        # print(f"prevBlockHeight: {self.prevBlockHeight}")
        # return mean of the block heights (sometimes blockRate is very low for consecutive blocks )
        meanBlock = (acceptedBlock + self.prevBlockHeight)//2
        print(f"acceptedBlock: {meanBlock}")
        return meanBlock, self.error
