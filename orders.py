import time

from consts import orderCartAddr, minBoxValue, txFee
from helpers import getUnspentBoxesByAddress, getSaleBoxByNFT, getRoyaltyInfo, treeToAddress, boxIdToBinary, \
    encodeCollNfts, encodeLong, encodeLongArray, encodeInt, signTx

import traceback

def attemptRefund(box, buyer, value, maxTxFee):
    transactionToSign = \
    {
        "requests": [
            {
                "address": buyer,
                "value": value - maxTxFee,
                "assets": [
                ],
                "registers": {
                }
            }
        ],
        "fee": maxTxFee,
        "inputsRaw":
            [boxIdToBinary(box["boxId"])],
        "dataInputsRaw":
            []
    }

    print(transactionToSign)
    print("Signing Refund", transactionToSign)
    txId = signTx(transactionToSign)
    print()
    print(txId)
    print()


def processOrderCart(box):
    initialNfts = box["additionalRegisters"]["R4"]["renderedValue"]
    initialPrices = box["additionalRegisters"]["R5"]["renderedValue"]
    initialBuyer = box["additionalRegisters"]["R6"]["renderedValue"]
    initialMaxTxFee = int(box["additionalRegisters"]["R7"]["renderedValue"])
    buyerAddr = treeToAddress(initialBuyer)
    if attemptRefund(box, buyerAddr, box['value'], initialMaxTxFee):
        print("HI FAILURE")
    print(initialNfts)
    nfts = initialNfts[1:-1].split(",")
    prices = initialPrices[1:-1].split(",")
    items = list(zip(nfts, prices))
    print(items)
    currBox = box
    for item in items:
        currNfts = currBox["additionalRegisters"]["R4"]["renderedValue"][1:-1].split(",")
        currPrices = currBox["additionalRegisters"]["R5"]["renderedValue"][1:-1].split(",")
        targetNft = item[0]
        targetPrice = int(item[1])
        targetNftIndex = currNfts.index(item[0])
        saleBox = getSaleBoxByNFT(targetNft, targetPrice)
        if box == -1:
            continue
        currBoxValue = int(currBox["value"])
        finalBoxValue = currBoxValue - targetPrice - initialMaxTxFee
        royaltyInfo = getRoyaltyInfo(targetNft)
        seller = saleBox["additionalRegisters"]["R5"]["renderedValue"]
        sellerAddr = treeToAddress(seller)
        sellerValue = targetPrice * (98 - royaltyInfo["percentage"]) / 100
        shValue = targetPrice * 0.02
        currIntPrices = [eval(i) for i in prices]
        del currNfts[targetNftIndex]
        del currIntPrices[targetNftIndex]

        print("values")
        print(currBoxValue)
        print(targetPrice)
        print(sellerAddr)
        print(shValue)
        print(minBoxValue)
        print(finalBoxValue)
        print(minBoxValue)

        transactionToSign = \
            {
                "requests": [
                    {
                        "address": sellerAddr,
                        "value": int(sellerValue),
                        "assets": [
                        ],
                        "registers": {
                            "R4": "0e20" + saleBox["boxId"]
                        }
                    },
                    {
                        "address": "9h9ssEYyHaosFg6BjZRRr2zxzdPPvdb7Gt7FA8x7N9492nUjpsd",
                        "value": int(shValue),
                        "assets": [
                        ],
                        "registers": {
                        }
                    },
                    {
                        "address": buyerAddr,
                        "value": minBoxValue,
                        "assets": [
                        ],
                        "registers": {
                        }
                    },
                    {
                        "address": orderCartAddr,
                        "value": int(finalBoxValue),
                        "assets": [
                        ],
                        "registers": {
                            "R4": encodeCollNfts(currNfts),
                            "R5": encodeLongArray(currIntPrices),
                            "R6": box["additionalRegisters"]["R6"]["serializedValue"],
                            "R7": box["additionalRegisters"]["R7"]["serializedValue"],
                            "R8": box["additionalRegisters"]["R8"]["serializedValue"],
                        }
                    },
                    {
                        "address": buyerAddr,
                        "value": minBoxValue,
                        "assets": [
                            {
                                "tokenId": targetNft,
                                "amount": 1
                            }
                        ],
                        "registers": {
                            "R4": encodeInt(targetNftIndex)
                        }
                    }
                ],
                "fee": txFee,
                "inputsRaw":
                    [boxIdToBinary(box["boxId"]), boxIdToBinary(saleBox["boxId"])],
                "dataInputsRaw":
                    []
            }
        print("roys")
        print(royaltyInfo)
        if royaltyInfo["percentage"] != 0:
            transactionToSign["requests"][2]["address"] = royaltyInfo["address"]
            transactionToSign["requests"][2]["value"] = int(royaltyInfo["percentage"] * targetPrice / 100)
        print(transactionToSign)
        print("Signing Transaction", transactionToSign)
        txId = signTx(transactionToSign)
        print()
        print(txId)
        print()
        break




def orderCartJob():
    print("Begin Order Cart Job")
    foundBoxes = getUnspentBoxesByAddress(orderCartAddr)
    print("Found", len(foundBoxes), "boxes")
    if len(foundBoxes) > 0:
        for box in foundBoxes:
            try:
                print("Order Cart Txid", box["transactionId"])
                processOrderCart(box)
            except Exception:
                print("Program Crash!" + "\n")
                print(traceback.format_exc())
                print("\nProgram Crash!")
    return
