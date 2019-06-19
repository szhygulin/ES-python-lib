import docker
import time
import re

client = docker.from_env()
containers = client.containers.list(all)
current_epoch = 0
balances = []
sleep_time = 2
central_company_price = [0]
open_orders = {}

def initiate():
    for x in containers:
        if x.name == "chaincode":
            command = """sh -c '''go build''' """
            res=x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-dollar")
            #print("\n")
            #print(res)
            #time.sleep(10)
            command = """sh -c "CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=USDAsset:0 ./es-dollar" """
            res=x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-dollar", detach=True)
            #print("\n")
            #print(res)
            print("ES_dollar initiated")
            command = """sh -c "go build" """
            res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-energy")
            #print("\n")
            #print(res)
            #time.sleep(10)
            command = """sh -c "CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=EnergyAsset:0 ./es-energy" """
            res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-energy", detach=True)
            #print("\n")
            #print(res)
            print("ES_energy initiated")
            command = """sh -c "go build" """
            res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-exchange")
            #print("\n")
            #print(res)
            # time.sleep(10)
            command = """sh -c "CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=Exchange:0 ./es-exchange" """
            res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-exchange", detach=True)
            #print("\n")
            #print(res)
            print("ES_exchange initiated")
    for x in containers:
        if x.name == "cli":
            command = """peer chaincode install -p chaincodedev/chaincode/es-dollar -n USDAsset -v 0"""
            res=x.exec_run(command)
            #print("\n")
            #print(res)
            command = """peer chaincode instantiate -n USDAsset -v 0 -c '{"Args":[]}' -C myc"""
            res=x.exec_run(command)
            #print("\n")
            #print(res)
            print("USD asset instantiated")
            command = """peer chaincode install -p chaincodedev/chaincode/es-energy -n EnergyAsset -v 0"""
            res = x.exec_run(command)
            #print("\n")
            #print(res)
            command = """peer chaincode instantiate -n EnergyAsset -v 0 -c '{"Args":[]}' -C myc"""
            res = x.exec_run(command)
            #print("\n")
            #print(res)
            print("Energy asset instantiated")
            command = """peer chaincode install -p chaincodedev/chaincode/es-exchange -n Exchange -v 0"""
            res = x.exec_run(command)
            #print("\n")
            #print(res)
            command = """peer chaincode instantiate -n Exchange -v 0 -c '{"Args":[]}' -C myc"""
            res = x.exec_run(command)
            #print("\n")
            #print(res)
            time.sleep(sleep_time*3)
            print("Exchange instantiated")
            command = """peer chaincode invoke -n EnergyAsset 0 -c '{"Args":["set", "centralCompany", "999999"]}' -C myc"""
            res=x.exec_run(command)
            #print(res,"\n")
            command = """peer chaincode invoke -n USDAsset 0 -c '{"Args":["set", "centralCompany", "0"]}' -C myc"""
            res=x.exec_run(command)
            #print(res, "\n")
            time.sleep(sleep_time * 3)
            print("central company initiated")


def setUserBalance(user_id, asset_name, amount=0):
    for x in containers:
        if x.name == "cli":
            a1 = """peer chaincode invoke -n """
            a2 = asset_name + """ -c '{"Args":["set", \""""
            a3 = user_id + """\", \"""" + str(amount) + """\"]}' -C myc"""
            command = a1 + a2 + a3
            print(command)
            res = x.exec_run(command)
            time.sleep(2*sleep_time)
            #print("\n")
            #print(res)

def transferAsset(sender_id, recipient_id, asset_name, amount):
    for x in containers:
        if x.name == "cli":
            a1 = """peer chaincode invoke -n """ + asset_name + """ -c '{"Args":["send", \""""
            a2 = sender_id + """\", \"""" + recipient_id + """\", \"""" + str(amount) + """\"]}' -C myc"""
            command = a1 + a2
            print(command)
            res = x.exec_run(command)
            #print("\n")
            #print(res)

def trade(energy_seller_id, energy_buyer_id, energy_amount, usd_amount):
    for x in containers:
        if x.name == "cli":
            a1 = """peer chaincode invoke -n Exchange -c '{"Args":["exchange", \"""" + energy_buyer_id + """\", \""""
            a2 = str(usd_amount) + """\", \"""" + energy_seller_id + """\", \"""" + str(energy_amount) + """\"]}' -C myc"""
            command = a1 + a2
            print(command)
            res = x.exec_run(command)
            #print("\n")
            time.sleep(2*sleep_time)
            #print(res)

def getUserBalances(user_id, epoch=current_epoch):
    for x in containers:
        if x.name == "cli":
            if epoch == current_epoch:
                command1 = """peer chaincode query -n USDAsset -c '{"Args":["query",\"""" + user_id + """\"]}' -C myc"""
                command2 = """peer chaincode query -n EnergyAsset -c '{"Args":["query",\"""" + user_id + """\"]}' -C myc"""
                print(command1)
                print(command2)
                res = x.exec_run(command1)
                if res.exit_code != 0:
                    usd_balance = 0
                else:
                    usd_output = str(res.output).split("\\n")
                    usd_balance = int(usd_output[-2])
                res = x.exec_run(command2)
                if res.exit_code != 0:
                    energy_balance = 0
                else:
                    energy_output = str(res.output).split("\\n")
                    energy_balance = int(energy_output[-2])
                return [usd_balance, energy_balance]
            else:
                return balances[epoch][user_id]

def burnEnergy(user_id, amount):
    for x in containers:
        if x.name == "cli":
            a1 = """peer chaincode invoke -n EnergyAsset -c '{"Args":["burn", \"""" + user_id + """\", \""""
            a2 = str(amount) + """\"]}' -C myc"""
            command = a1 + a2
            print(command)
            res = x.exec_run(command)
            #print("\n")
            time.sleep(2 * sleep_time)
            #print(res)

def generateEnergy(user_id, amount):
    for x in containers:
        if x.name == "cli":
            a1 = """peer chaincode invoke -n EnergyAsset -c '{"Args":["generate", \"""" + user_id + """\", \""""
            a2 = str(amount) + """\"]}' -C myc"""
            command = a1 + a2
            print(command)
            res = x.exec_run(command)
            #print("\n")
            time.sleep(2 * sleep_time)
            #print(res)

def getTotalBalances(epoch=current_epoch):
    for x in containers:
        if x.name == "cli":
            if epoch == current_epoch:
                command1 = """peer chaincode invoke -n USDAsset -c '{"Args":["keys"]}' -C myc"""
                command2 = """peer chaincode invoke -n EnergyAsset -c '{"Args":["keys"]}' -C myc"""
                print(command1)
                print(command2)
                regex = """result: status:200 payload:\".*\""""
                res = x.exec_run(command1)
                #print(res.output)
                if res.exit_code != 0:
                    usd_ids = []
                else:
                    usd_ids_str = re.findall(regex, str(res.output))[0]
                    usd_ids = usd_ids_str.split("""\\\\\"""")
                    del usd_ids[::2]
                    #print(usd_ids)
                res = x.exec_run(command2)
                #print(res.output)
                if res.exit_code != 0:
                    energy_ids = []
                else:
                    energy_ids_str = re.findall(regex, str(res.output))[0]
                    energy_ids = energy_ids_str.split("""\\\\\"""")
                    del energy_ids[::2]
                    #print(energy_ids)
                balances_return = {}
                #print("usd_ids, energy_ids", usd_ids, energy_ids)
                for x in usd_ids or x in energy_ids:
                    balances_return[x] = getUserBalances(x)
                return balances_return
            else:
                return balances[epoch]

def getCentralCompanyPrice(epoch=current_epoch):
    return central_company_price[epoch]

def setPriceLevel(price):
    central_company_price[current_epoch] = price

def openOrder(user_id, energy_amount, usd_amount):
    open_orders[user_id] = [energy_amount, usd_amount]

def cancelOrder(user_id):
    del open_orders[user_id]

def getOpenOrders():
    return open_orders

def buyFromCentralCompany(buyer_id, amount):
    print("cc_price", central_company_price[current_epoch])
    usd_amount = int(central_company_price[current_epoch]*amount)
    trade("centralCompany", buyer_id, amount, usd_amount)
    generateEnergy("centralCompany", amount)

def buyWithMarketOrder(user_id, energy_amount):
    if open_orders == {}:
        buyFromCentralCompany(user_id, energy_amount)
    else:
        prices = []
        for x in open_orders:
            prices.append([open_orders[x][1] / open_orders[x][0], x])
        sorted_prices = sorted(prices, key=lambda y: y[0])
        p = sorted_prices[0][0]
        print(sorted_prices)
        while p <= central_company_price[current_epoch] and energy_amount > 0:
            amount = min(energy_amount, open_orders[sorted_prices[0][1]][0])
            energy_amount -= amount
            trade(sorted_prices[0][1], user_id, amount, int(amount*sorted_prices[0][0]))
            #print(getTotalBalances())
            open_order_ene = open_orders[sorted_prices[0][1]][0]
            cancelOrder(sorted_prices[0][1])
            if amount < open_order_ene:
                ene_to_sell = open_order_ene - amount
                openOrder(sorted_prices[1], ene_to_sell, int(sorted_prices[0][0]*ene_to_sell))
            del sorted_prices[0]
            if sorted_prices == []:
                p = 9999999
            else:
                p = sorted_prices[0][0]
        if energy_amount > 0:
            buyFromCentralCompany(user_id, energy_amount)
    time.sleep(sleep_time*3)

def nextEpoch():
    global current_epoch
    balances.append(getTotalBalances())
    central_company_price.append(central_company_price[current_epoch])
    current_epoch += 1

def test():
    setPriceLevel(1)
    print(getUserBalances("centralCompany"))
    setUserBalance("test1", "USDAsset", 10)
    setUserBalance("test2", "USDAsset", 10)
    setUserBalance("test3", "USDAsset", 100)
    setUserBalance("test2", "EnergyAsset", 10)
    print(getTotalBalances())
    transferAsset("test2", "test1", "EnergyAsset", 3)
    print(getTotalBalances())
    nextEpoch()
    print("current_epoch", current_epoch)
    setPriceLevel(2)
    print(getTotalBalances(0))
    openOrder("test2", 4, 4)
    openOrder("test1", 3, 6)
    print(open_orders)
    buyWithMarketOrder("test3", 8)
    print("current_epoch", current_epoch)
    print("balances", balances)
    print(getTotalBalances())
    buyFromCentralCompany("test3", 3)
    print(getTotalBalances())



if __name__ == '__main__':
    initiate()
    test()