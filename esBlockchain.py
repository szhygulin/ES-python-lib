import docker
import time
import re
import requests
import json


class blockchain:
    client = docker.from_env()
    containers = client.containers.list(all)
    for x in containers:
        print(x.name)
    balances = []
    sleep_time = 0.005
    central_company_price = [0]
    open_orders = {}
    current_epoch = 0

    def __init__(self, ip_address):
        self.current_epoch = 0
        self.ip_address = ip_address

    def buildChaincodes(self):
        temp_data = {'current_epoch': self.current_epoch}
        result = requests.post(self.ip_address, json=temp_data)
        for x in self.containers:
            if x.name == "orderer.example.com":
                command = """sh -c '''go build''' """
                res=x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-dollar")
                #print(res)
                command = """sh -c "CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=USDAsset:0 ./es-dollar" """
                res=x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-dollar", detach=True)
                #print(res)
                print("ES_dollar initiated")
                command = """sh -c "go build" """
                res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-energy")
                command = """sh -c "CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=EnergyAsset:0 ./es-energy" """
                res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-energy", detach=True)
                print("ES_energy initiated")
                command = """sh -c "go build" """
                res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-exchange")
                command = """sh -c "CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=Exchange:0 ./es-exchange" """
                res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-exchange", detach=True)
                print("ES_exchange initiated")

    def setChaincodes(self):
        temp_data = {'current_epoch': self.current_epoch}
        result = requests.post(self.ip_address, json=temp_data)
        for x in self.containers:
            if x.name == "cli":
                command = """peer chaincode install -p chaincode/go/es-dollar -n USDAsset -v 0"""
                res=x.exec_run(command)
                print(res)
                command = """peer chaincode instantiate -o orderer.example.com:7050 -n USDAsset -v 0 -c '{"Args":[]}' -C mychannel"""
                res=x.exec_run(command)
                print(res)
                print("USD asset instantiated")
                command = """peer chaincode install -p chaincode/go/es-energy -n EnergyAsset -v 0"""
                res = x.exec_run(command)
                print(res)
                command = """peer chaincode instantiate -o orderer.example.com:7050 -n EnergyAsset -v 0 -c '{"Args":[]}' -C mychannel"""
                res = x.exec_run(command)
                print(res)
                print("Energy asset instantiated")
                command = """peer chaincode install -p chaincode/go/es-exchange -n Exchange -v 0"""
                res = x.exec_run(command)
                print(res)
                command = """peer chaincode instantiate -o orderer.example.com:7050 -n Exchange -v 0 -c '{"Args":[]}' -C mychannel"""
                res = x.exec_run(command)
                print(res)
                time.sleep(self.sleep_time*3)
                print("Exchange instantiated")

    def createCentralCompany(self):
        for x in self.containers:
            if x.name == "cli":
                command = """peer chaincode invoke -n EnergyAsset 0 -c '{"Args":["set", "centralCompany", "999999"]}' -C mychannel"""
                res=x.exec_run(command)
                command = """peer chaincode invoke -n USDAsset 0 -c '{"Args":["set", "centralCompany", "0"]}' -C mychannel"""
                res=x.exec_run(command)
                time.sleep(self.sleep_time * 3)
                print("central company initiated")


    def setUserBalance(self, user_id, asset_name, amount=0):
        for x in self.containers:
            if x.name == "cli":
                a1 = """peer chaincode invoke -n """
                a2 = asset_name + """ -c '{"Args":["set", \""""
                a3 = user_id + """\", \"""" + str(amount) + """\"]}' -C mychannel"""
                command = a1 + a2 + a3
                #print(command)
                res = x.exec_run(command)
                #print(res)
                time.sleep(2*self.sleep_time)

    def transferAsset(self, sender_id, recipient_id, asset_name, amount):
        for x in self.containers:
            if x.name == "cli":
                a1 = """peer chaincode invoke -n """ + asset_name + """ -c '{"Args":["send", \""""
                a2 = sender_id + """\", \"""" + recipient_id + """\", \"""" + str(amount) + """\"]}' -C mychannel"""
                command = a1 + a2
                #print(command)
                res = x.exec_run(command)

    def trade(self, energy_seller_id, energy_buyer_id, energy_amount, usd_amount):
        for x in self.containers:
            if x.name == "cli":
                a1 = """peer chaincode invoke -n Exchange -c '{"Args":["exchange", \"""" + energy_buyer_id + """\", \""""
                a2 = str(usd_amount) + """\", \"""" + energy_seller_id + """\", \"""" + str(energy_amount) + """\"]}' -C mychannel"""
                command = a1 + a2
                #print(command)
                res = x.exec_run(command)
                time.sleep(2*self.sleep_time)

    def getUserBalances(self, user_id, epoch):
        for x in self.containers:
            if x.name == "cli":
                if epoch == self.current_epoch:
                    command1 = """peer chaincode query -n USDAsset -c '{"Args":["query",\"""" + user_id + """\"]}' -C mychannel"""
                    command2 = """peer chaincode query -n EnergyAsset -c '{"Args":["query",\"""" + user_id + """\"]}' -C mychannel"""
                    #print(command1)
                    #print(command2)
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
                    return self.balances[epoch][user_id]

    def burnEnergy(self, user_id, amount):
        for x in self.containers:
            if x.name == "cli":
                a1 = """peer chaincode invoke -n EnergyAsset -c '{"Args":["burn", \"""" + user_id + """\", \""""
                a2 = str(amount) + """\"]}' -C mychannel"""
                command = a1 + a2
                #print(command)
                res = x.exec_run(command)
                time.sleep(2 * self.sleep_time)

    def generateEnergy(self, user_id, amount):
        for x in self.containers:
            if x.name == "cli":
                a1 = """peer chaincode invoke -n EnergyAsset -c '{"Args":["generate", \"""" + user_id + """\", \""""
                a2 = str(amount) + """\"]}' -C mychannel"""
                command = a1 + a2
                #print(command)
                res = x.exec_run(command)
                time.sleep(2 * self.sleep_time)

    def getTotalBalances(self, epoch):
        for x in self.containers:
            if x.name == "cli":
                if epoch == self.current_epoch:
                    command1 = """peer chaincode invoke -n USDAsset -c '{"Args":["keys"]}' -C mychannel"""
                    command2 = """peer chaincode invoke -n EnergyAsset -c '{"Args":["keys"]}' -C mychannel"""
                    #print(command1)
                    #print(command2)
                    regex = """result: status:200 payload:\".*\""""
                    res = x.exec_run(command1)
                    if res.exit_code != 0:
                        usd_ids = []
                    else:
                        usd_ids_str = re.findall(regex, str(res.output))[0]
                        usd_ids = usd_ids_str.split("""\\\\\"""")
                        del usd_ids[::2]
                    res = x.exec_run(command2)
                    if res.exit_code != 0:
                        energy_ids = []
                    else:
                        energy_ids_str = re.findall(regex, str(res.output))[0]
                        energy_ids = energy_ids_str.split("""\\\\\"""")
                        del energy_ids[::2]
                    balances_return = {}
                    #print(usd_ids, energy_ids)
                    for x in usd_ids or x in energy_ids:
                        balances_return[x] = self.getUserBalances(x,self.current_epoch)
                    print(balances_return)
                    return balances_return
                else:
                    #print("trigger", epoch)
                    return self.balances[epoch]

    def getCentralCompanyPrice(self, epoch):
        #return self.central_company_price[epoch]
        response = requests.get(self.ip_address, data="cc_price")
        # print('getOpenOrders')
        # print(response.status_code)
        # print(response.content)
        string = response.content.decode('utf-8')
        json_obj = json.loads(string)
        # print(json_obj)
        return json_obj["cc_price"]

    def setPriceLevel(self, price):
        data = {'cc_price': price}
        print("setpricelevel")
        result = requests.post(self.ip_address, json=data)
        self.central_company_price[self.current_epoch] = price
        #print(result)

    def openOrder(self, user_id, energy_amount, usd_amount):
        data = {}
        data["user_id"] = user_id
        data["energy"] = energy_amount
        data["usd"] = usd_amount
        result = requests.post(self.ip_address, json=data)
        #print(result.content)
        #self.open_orders[user_id] = [energy_amount, usd_amount]

    def cancelOrder(self, user_id):
        data = {}
        data["user_id"] = user_id
        requests.delete(self.ip_address, json=data)

    def getOpenOrders(self):
        response = requests.get(self.ip_address)
        #print('getOpenOrders')
        #print(response.status_code)
        #print(response.content)
        string = response.content.decode('utf-8')
        #print("string", string)
        json_obj = json.loads(string)
        #print(json_obj)
        return json_obj['orders']
        #return self.open_orders

    def buyFromCentralCompany(self, buyer_id, amount):
        #print("cc_price", self.central_company_price[self.current_epoch])
        usd_amount = int(self.central_company_price[self.current_epoch]*amount)
        self.trade("centralCompany", buyer_id, amount, usd_amount)
        self.generateEnergy("centralCompany", amount)

    def buyWithMarketOrder(self, user_id, energy_amount):
        self.open_orders = self.getOpenOrders()
        if self.open_orders == {}:
            self.buyFromCentralCompany(user_id, energy_amount)
        else:
            prices = []
            for x in self.open_orders:
                prices.append([self.open_orders[x][1] / self.open_orders[x][0], x])
            sorted_prices = sorted(prices, key=lambda y: y[0])
            p = sorted_prices[0][0]
            #print(sorted_prices)
            while p < self.central_company_price[self.current_epoch] and energy_amount > 0:
                #print('price', p)
                #print('energy to buy', energy_amount)
                amount = min(energy_amount, self.open_orders[sorted_prices[0][1]][0])
                energy_amount -= amount
                self.trade(sorted_prices[0][1], user_id, amount, int(amount*sorted_prices[0][0]))
                open_order_ene = self.open_orders[sorted_prices[0][1]][0]
                self.cancelOrder(sorted_prices[0][1])
                ## open order with lover amount, if not fully fulfilled
                self.open_orders = self.getOpenOrders()
                #print(self.open_orders)
                if amount < open_order_ene:
                    ene_to_sell = open_order_ene - amount
                    self.openOrder(sorted_prices[0][1], ene_to_sell, int(sorted_prices[0][0]*ene_to_sell))
                    self.open_orders=self.getOpenOrders()
                #print(self.open_orders)
                del sorted_prices[0]
                if sorted_prices == []:
                    p = 9999999
                else:
                    p = sorted_prices[0][0]
            if energy_amount > 0:
                self.buyFromCentralCompany(user_id, energy_amount)
        time.sleep(self.sleep_time*3)

    def getCurrentEpoch(self):
        response = requests.get(self.ip_address)
        # print('getOpenOrders')
        # print(response.status_code)
        # print(response.content)
        string = response.content.decode('utf-8')
        #print("string", string)
        json_obj = json.loads(string)
        print(json_obj)
        return json_obj['current_epoch']
        # return self.open_orders

    def voteNextEpoch(self):
        self.balances.append(self.getTotalBalances(self.current_epoch))
        self.central_company_price.append(self.central_company_price[self.current_epoch])
        self.current_epoch += 1
        data = {'current_epoch_vote': self.current_epoch}
        print("votecurrentepoch, ", self.current_epoch)
        result = requests.post(self.ip_address, json=data)

    def getNextEpochVotes(self):
        response = requests.get(self.ip_address)
        # print('getOpenOrders')
        # print(response.status_code)
        # print(response.content)
        string = response.content.decode('utf-8')
        #print("string", string)
        json_obj = json.loads(string)
        # print(json_obj)
        return json_obj['current_epoch_votes']

    def nextEpoch(self):
        self.balances.append(self.getTotalBalances(self.current_epoch))
        self.central_company_price.append(self.central_company_price[self.current_epoch])
        self.current_epoch += 1
        data = {'current_epoch': self.current_epoch}
        print("setcurrentepoch, ", self.current_epoch)
        result = requests.post(self.ip_address, json=data)

    def test(self):
        self.setPriceLevel(1)
        print(self.getUserBalances("centralCompany", epoch=self.current_epoch))
        self.setUserBalance("test1", "USDAsset", 10)
        self.setUserBalance("test2", "USDAsset", 10)
        self.setUserBalance("test3", "USDAsset", 100)
        self.setUserBalance("test2", "EnergyAsset", 10)
        print(self.getTotalBalances(epoch=self.current_epoch))
        self.transferAsset("test2", "test1", "EnergyAsset", 3)
        print(self.getTotalBalances(epoch=self.current_epoch))
        self.nextEpoch()
        print("Current_epoch", self.getCurrentEpoch())
        print("current_epoch", self.current_epoch)
        self.setPriceLevel(2)
        print(self.getTotalBalances(0))
        self.openOrder("test2", 4, 4)
        self.openOrder("test1", 3, 6)
        #time.sleep(self.sleep_time * 3)
        print("open orders", self.getOpenOrders())
        self.buyWithMarketOrder("test3", 8)
        print("Current_epoch", self.getCurrentEpoch())
        print("balances", self.balances)
        print(self.getTotalBalances(epoch=self.current_epoch))
        self.buyFromCentralCompany("test3", 3)
        print(self.getTotalBalances(epoch=self.current_epoch))

    def shutdown(self):
        for x in self.containers:
            x.kill()



if __name__ == '__main__':
    bch=blockchain('http://127.0.0.1:8000')
    #bch.openOrder("test2", 4, 4)
    #bch.openOrder("test1", 3, 6)
    #print("open orders", bch.getOpenOrders())
    bch.setChaincodes()
    bch.createCentralCompany()
    bch.test()
    #bch.shutdown()
