import json
import requests
from consts import nodeUrl, headers, orderCartAddr
import time


def unlockWallet():
    print(requests.post(nodeUrl+ "/wallet/unlock", json ={"pass":headers["api_key"]}, headers=headers))


def getRequest(url, headers={}):
    res = requests.get(url, headers)
    timeout = 0
    while res.status_code != 200 and timeout < 5:
        time.sleep(5)
        res = requests.get(url, headers)
        timeout += 1
    if res.status_code == 404:
        return 404
    return res

def getSaleBoxByNFT(nft, price):
    res = getRequest("https://api.ergoplatform.com/api/v1/boxes/unspent/byTokenId/"+ nft+ "?limit=100")
    if res == -1:
        return -1
    res = json.loads(res.text)
    for box in res["items"]:
        if "R4" in box["additionalRegisters"] and box["additionalRegisters"]['R4']['sigmaType'] == 'SLong' and int(box["additionalRegisters"]["R4"]["renderedValue"]) == price and box["ergoTree"] == "1012040604000e208e7def26c2cd62ab1afe57957239e942f7c08c693126a66358a3f85028f7b7b50564040005d00f04020e240008cd035afd0501f6f5c1c9fb9ed5afc84fbc02825c0c7c3f65970fa3e3d9c8c6abc5460500040004880e040401010400040004020e240008cd035afd0501f6f5c1c9fb9ed5afc84fbc02825c0c7c3f65970fa3e3d9c8c6abc546040095ed91b1a5730094cbc2b2a47301007302d804d601e4c6a70663d602c672010404d603e4c6a70405d6049d72037303d195e67202d804d605b2a5730400d606e47202d6079d9c72037e7206057305d608b2a57306009683070192c17205999972037204720793c27205e4c6a7050e93e4c67205040ec5a792c17208720493c27208730795eded947207730891720673098f7206730ad801d609b2a5730b00ed92c17209720793c27209c27201730c93c572018cb2db6308a7730d0001d802d605b2a5730e00d606b2a5730f009683060192c17205997203720493c27205e4c6a7050e93e4c67205040ec5a792c17206720493c27206731093c572018cb2db6308a773110001cde4c6a70707":
            return box
    print("Returning value")


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

def getBoxFromTx(tx):
    res = json.loads(getRequest("http://127.0.0.1:9053/transactions/unconfirmed?limit=100&offset=0").text)
    for item in res:
        if item["id"] == tx:
            for box in item["outputs"]:
                if box["ergoTree"] == "10090404040604080402040004020400040004029591b1a57300d809d601b2a5730100d602e4c6a7041ad603dc0c1d720201e4c6a70511d604b2a5730200d605e4c672040404d606b27203720500d607e4c6a70705d608e4c6a7060ed609e4c67201041ad1edededededed93c27201c2a7939a9ac172018c7206027207c1a7eded93e4c67201060e720893e4c672010705720793e4c6a70805e4c672010805939ab172097303b1720293dc0c1d720901e4c672010511b3b4720373047205b472039a72057305b1720393c272047208938cb2db63087204730600018c720601d801d601b2a5730700d1ededed93c27201e4c6a7060e92c1720199c1a7e4c6a7070593b1a47308927ea305e4c6a70805":
                    return box



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



