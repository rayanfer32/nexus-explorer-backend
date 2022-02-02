import os
import json
import time
from datetime import datetime
import requests

os.system("clear")

SERVER = os.getenv("SERVER_URL")

# https://github.com/Nexusoft/LLL-TAO/blob/merging/docs/API/LEDGER.MD#listblocks

def getLatestBlockHeight():
    resp = requests.get(f"{SERVER}/system/get/info")
    # print(resp.json())
    return resp.json()["result"]["blocks"]


def fetchResponse(height=None):
    '''
    Accounting for current blockRate which is about 60 ~ 70 Blocks/Hr
    fetch 100 blocks to process as a step1
    '''
    if height is None:
        topBlock = getLatestBlockHeight()
        mod100block = topBlock - (topBlock % 100)
        height = mod100block

    print(f"fetch at {height=}")
    # page=1 will return previous(older) blocks /
    # no page param will fetch newer blocks
    _url = f"{SERVER}/ledger/list/blocks?"
    _params = f"verbose=summary&limit=100&height={height}&page=1"
    resp = requests.get(_url + _params)
    return resp.json()


def saveResponse(resp):
    # save resp to file
    with open("resp.json", "w") as f:
        # f.write(str(resp.json()))
        json.dump(resp, f)


def loadResponse():
    with open("resp.json",) as f:
        respJ = json.load(f)
        return respJ


def contractsPerBlock(block):
    totalContractsQty = 0
    try:
        for tx in block["tx"]:
            if tx["type"].find("legacy") > -1:
                contractsQty = len(tx["outputs"])
            else:
                contractsQty = len(tx["contracts"])
            totalContractsQty += contractsQty
    except Exception as e:
        print(e)
        # print(block)
    return totalContractsQty


def process(respJ, timestamps, dateStamps, contracts):
    elapsedTime = 0
    elapsedDelta = 0
    lastTimestamp = respJ["result"][0]["timestamp"]
    blocksProcessed = 0
    callbackBlock = 0
    for block in respJ["result"]:
        # print(block["height"])
        ts = block["timestamp"]
        dateStamp = block["date"]
        timestamps.append(ts)
        dateStamps.append(dateStamp)
        elapsedDelta = lastTimestamp - ts
        elapsedTime += elapsedDelta
        lastTimestamp = ts

        blocksProcessed += 1
        contracts.append(contractsPerBlock(block))
        if(elapsedTime >= 3600):
            callbackBlock = block["height"]
            callbackBlock = int(callbackBlock) - 1
            print(f"calback block: {callbackBlock}")
            break

    blocksTime = timestamps[0] - timestamps[-1]
    hms = time.strftime('%H:%M:%S', time.gmtime(blocksTime))
    print(f"Processed {blocksProcessed} blocks  in : {hms}")
    print(f"Found {sum(contracts)} Contracts")

    return callbackBlock, sum(contracts), timestamps[30]


def getBlockAtStartingHour():
    # latestBlock = getLatestBlockHeight()
    lastBlocksJson = requests.get(
        f"{SERVER}/ledger/list/blocks?verbose=summary&limit=100").json()
    lastBlocksJson = lastBlocksJson["result"]
    for block in lastBlocksJson:
        blockTime = block["timestamp"]
        dateObj = datetime.fromtimestamp(blockTime)
        print(dateObj.strftime('%H:%M:%S'))
        if dateObj.minute <= 1:
            return block["height"]


# blockAtHour = getBlockAtStartingHour()
# print(f"{blockAtHour=}")
def getChartData(hours: int = 1, exportFilename: str = None):
    timestamps = []  # block timestamps
    dateStamps = []  # block dateStamps
    contracts = []  # cumulative of all the txs inside a block

    blockAtStartHour = fetchResponse(getBlockAtStartingHour())
    cbBlock, _contracts, tstp = process(
        blockAtStartHour, timestamps, dateStamps, contracts)
    # find transactions in last 24h
    for hour in range(hours-1):  # 1h
        print(f"hour: {hour}")
        res = fetchResponse(cbBlock)
        cbBlock, _contracts, tstp = process(
            res, timestamps, dateStamps, contracts)

    # reverse the graph data as the data was fetched in reverse order
    timestamps.reverse()
    dateStamps.reverse()
    contracts.reverse()
    graphingData = {
        # "timestamps": timestamps,
        "datestamps": dateStamps,
        "contracts": contracts,
    }

    if exportFilename is not None:
        with open(exportFilename, "w") as out:
            json.dump(graphingData, out)

    return graphingData


if __name__ == "__main__":
    getChartData(2, ".backend/test.json")
