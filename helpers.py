import json
import requests
from consts import nodeUrl, headers
import time


def unlockWallet():
    print(requests.post(nodeUrl+ "/wallet/unlock", json ={"pass":headers["api_key"]}, headers=headers))


def getRequest(url, headers={}):
    res = requests.get(url, headers)
    timeout = 0
    while res.status_code != 200 and timeout < 5:
        time.sleep(10)
        res = requests.get(url, headers)
        timeout += 1
    if res.status_code == 404:
        return 404
    return res

def getSaleBoxByNFT(nft, price):
    res = getRequest("https://api.ergoplatform.com/api/v1/boxes/unspent/byTokenId/"+ nft)
    if res == -1:
        return -1
    res = json.loads(res.text)
    for box in res["items"]:
        if "R4" in box["additionalRegisters"] and box["additionalRegisters"]['R4']['sigmaType'] == 'SLong' and int(box["additionalRegisters"]["R4"]["renderedValue"]) == price:
            return box


def getRoyaltyInfo(nftId):
    res = getRequest("https://api.ergoplatform.com/api/v1/boxes/"+ nftId)
    res = json.loads(res.text)
    percentage = 0
    if "R4" in res["additionalRegisters"] and res["additionalRegisters"]["R4"]["sigmaType"] == "SInt":
        percentage = int(res["additionalRegisters"]["R4"]["renderedValue"]) / 10
    address = res["address"]
    return {
        "percentage": percentage,
        "address": address
    }


def getCurrentHeight():
    return json.loads(getRequest(nodeUrl + "/blocks/lastHeaders/1").text)[0]['height']


def getUnspentBoxesByAddress(addr):
    return json.loads(getRequest("https://api.ergoplatform.com/api/v1/boxes/unspent/byAddress/"+addr).text)['items']


def treeToAddress(addr):
    return json.loads(getRequest(nodeUrl + "/utils/ergoTreeToAddress/" + addr).text)["address"]

def boxIdToBinary(boxId):
    return json.loads(getRequest(nodeUrl + "/utxo/withPool/byIdBinary/" + boxId).text)["bytes"]

def signTx(tx):
    res = requests.post(nodeUrl + "/wallet/transaction/send", json=tx,
                               headers=headers)
    print(res.text)
    if res.status_code != 200:
        return -1
    return json.loads(res.text)


def getBoxFromId(boxId):
    resp = getRequest("http://127.0.0.1:9053/utxo/byId/"+boxId)
    if resp == 404:
        return 404
    res = json.loads(resp.text)
    return res



def zigzag(i: int):
    return (i >> 31) ^ (i << 1)


def vlq(i: int):
    ret = []
    while i != 0:
        b = i & 0x7F
        i >>= 7
        if i > 0:
            b |= 0x80
        ret.append(b)
    return ret


def encodeLong(n: int):
    if n == 0:
        return "0500"
    z = zigzag(n)
    v = vlq(z)
    r = '05' + ''.join(['{0:02x}'.format(i) for i in v])
    return r


def encodeInt(n: int):
    if n == 0:
        return "0400"
    z = zigzag(n)
    v = vlq(z)
    r = '04' + ''.join(['{0:02x}'.format(i) for i in v])
    return r


def badEncodeLong(n: int):
    z = zigzag(n)
    v = vlq(z)
    r = ''.join(['{0:02x}'.format(i) for i in v])
    return r

def encodeLongTuple(arr):
    res = "11" + '{0:02x}'.format(len(arr))
    for long in arr:
        res += badEncodeLong(long)
    return res

def encodeCollNfts(nfts):
    reg = "1a" + format(len(nfts),'02x')
    for nft in nfts:
        reg += "20" + nft
    return reg



def encodeLongArray(prices):
    reg = "11" + format(len(prices),'02x')
    for price in prices:
        reg += encodeLong(price)[2:]
    return reg



