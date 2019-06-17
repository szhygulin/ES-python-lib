import docker
import time

client = docker.from_env()
containers = client.containers.list(all)

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
            time.sleep(5)
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
            time.sleep(5)
            print(res)
            command = """peer chaincode invoke -n Exchange -c '{"Args":["exchange", "test1", "1", "test2", "1"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            time.sleep(5)
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

def setUserBalance(user_id, asset_name, amount=0):
    for x in containers:
        if x.name == "cli":
            a1 = """peer chaincode invoke -n """
            a2 = asset_name + """ -c '{"Args":["set", \""""
            a3 = user_id + """\", \"""" + str(amount) + """\"]}' -C myc"""
            command = a1 + a2 + a3
            print(command)
            res = x.exec_run(command)
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


if __name__ == '__main__':
    #initiate()
    setUserBalance("user", "USDAsset", 10)
    transferAsset("user", "user2", "USDAsset", 2)
