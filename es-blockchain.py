import docker
import time
import re

client = docker.from_env()
containers = client.containers.list(all)
current_epoch = 0
balances = []
sleep_time = 5

def initiate():
    for x in containers:
        if x.name == "chaincode":
            command = """sh -c '''go build''' """
            res=x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-dollar")
            print("\n")
            print(res)
            #time.sleep(10)
            command = """sh -c "CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=USDAsset:0 ./es-dollar" """
            res=x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-dollar", detach=True)
            print("\n")
            print(res)
            print("ES_dollar initiated")
            command = """sh -c "go build" """
            res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-energy")
            print("\n")
            print(res)
            #time.sleep(10)
            command = """sh -c "CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=EnergyAsset:0 ./es-energy" """
            res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-energy", detach=True)
            print("\n")
            print(res)
            print("ES_energy initiated")
            command = """sh -c "go build" """
            res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-exchange")
            print("\n")
            print(res)
            # time.sleep(10)
            command = """sh -c "CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=Exchange:0 ./es-exchange" """
            res = x.exec_run(command, workdir="/opt/gopath/src/chaincode/es-exchange", detach=True)
            print("\n")
            print(res)
            print("ES_exchange initiated")
    for x in containers:
        if x.name == "cli":
            command = """peer chaincode install -p chaincodedev/chaincode/es-dollar -n USDAsset -v 0"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode instantiate -n USDAsset -v 0 -c '{"Args":[]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            print("USD asset instantiated")
            command = """peer chaincode install -p chaincodedev/chaincode/es-energy -n EnergyAsset -v 0"""
            res = x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode instantiate -n EnergyAsset -v 0 -c '{"Args":[]}' -C myc"""
            res = x.exec_run(command)
            print("\n")
            print(res)
            print("Energy asset instantiated")
            command = """peer chaincode install -p chaincodedev/chaincode/es-exchange -n Exchange -v 0"""
            res = x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode instantiate -n Exchange -v 0 -c '{"Args":[]}' -C myc"""
            res = x.exec_run(command)
            print("\n")
            print(res)
            time.sleep(sleep_time)
            print("Exchange instantiated")

def test():
    for x in containers:
        if x.name == "cli":
            command = """peer chaincode invoke -n USDAsset -c '{"Args":["set", "test1", "10"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode invoke -n EnergyAsset -c '{"Args":["set", "test2", "10"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            time.sleep(sleep_time)
            print(res)
            command = """peer chaincode invoke -n Exchange -c '{"Args":["exchange", "test1", "1", "test2", "1"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            time.sleep(sleep_time)
            command = """peer chaincode query -n USDAsset -c '{"Args":["query","test1"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n USDAsset -c '{"Args":["query","test2"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n EnergyAsset -c '{"Args":["query","test1"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n EnergyAsset -c '{"Args":["query","test2"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            print("Test successful")

def small_test():
    for x in containers:
        if x.name == "cli":
            #command = """peer chaincode invoke -n Exchange -c '{"Args":["exchange", "test1", "1", "test2", "1"]}' -C myc"""
            #res = x.exec_run(command)
            #print("\n")
            #print(res)
            command = """peer chaincode query -n USDAsset -c '{"Args":["query","test1"]}' -C myc"""
            res = x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n USDAsset -c '{"Args":["query","test2"]}' -C myc"""
            res = x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n EnergyAsset -c '{"Args":["query","test1"]}' -C myc"""
            res = x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n EnergyAsset -c '{"Args":["query","test2"]}' -C myc"""
            res = x.exec_run(command)
            print("\n")
            print(res)

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
            print("\n")
            print(res)

def transferAsset(sender_id, recipient_id, asset_name, amount):
    for x in containers:
        if x.name == "cli":
            a1 = """peer chaincode invoke -n """ + asset_name + """ -c '{"Args":["send", \""""
            a2 = sender_id + """\", \"""" + recipient_id + """\", \"""" + str(amount) + """\"]}' -C myc"""
            command = a1 + a2
            print(command)
            res = x.exec_run(command)
            print("\n")
            print(res)

def trade(energy_seller_id, energy_buyer_id, energy_amount, usd_amount):
    for x in containers:
        if x.name == "cli":
            a1 = """peer chaincode invoke -n Exchange -c '{"Args":["exchange", \"""" + energy_buyer_id + """\", \""""
            a2 = str(usd_amount) + """\", \"""" + energy_seller_id + """\", \"""" + str(energy_amount) + """\"]}' -C myc"""
            command = a1 + a2
            print(command)
            res = x.exec_run(command)
            print("\n")
            time.sleep(2*sleep_time)
            print(res)

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
            print("\n")
            time.sleep(2 * sleep_time)
            print(res)

def generateEnergy(user_id, amount):
    for x in containers:
        if x.name == "cli":
            a1 = """peer chaincode invoke -n EnergyAsset -c '{"Args":["generate", \"""" + user_id + """\", \""""
            a2 = str(amount) + """\"]}' -C myc"""
            command = a1 + a2
            print(command)
            res = x.exec_run(command)
            print("\n")
            time.sleep(2 * sleep_time)
            print(res)

def getTotalBalances(epoch=current_epoch):
    for x in containers:
        if x.name == "cli":
            if epoch == current_epoch:
                command1 = """peer chaincode invoke -n USDAsset -c '{"Args":["keys"]}' -C myc"""
                command2 = """peer chaincode invoke -n EnergyAsset -c '{"Args":["keys"]}' -C myc"""
                print(command1)
                print(command2)
                regex = """payload.*"""
                res = x.exec_run(command1)
                print(res.output)
                if res.exit_code != 0:
                    usd_ids = []
                else:
                    usd_ids_str = re.findall(regex, str(res.output))
                    print(usd_ids_str)
                    usd_ids = list(usd_ids_str)
                print(usd_ids)
                #res = x.exec_run(command2)
                #if res.exit_code != 0:
                #    energy_balance = 0
                #else:
                #    energy_output = str(res.output).split("\\n")
                #    energy_balance = int(energy_output[-2])
                return 0
                #return [usd_balance, energy_balance]
            else:
                return balances[epoch]


def nextEpoch():
    current_epoch += 1
    balances.append({})

if __name__ == '__main__':
    #initiate()
    setUserBalance("test1", "USDAsset", 10)
    setUserBalance("test2", "EnergyAsset", 10)
    #trade("test2", "test1", 1, 1)
    print("\n")
    #print(getUserBalances("test2"))
    #burnEnergy("test2", 2)
    #print(getUserBalances("test2"))
    #generateEnergy("test2", 20)
    print(getTotalBalances())