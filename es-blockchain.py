import docker
import time

def initiate():
    client = docker.from_env()
    containers = client.containers.list(all)
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
            command = """sh -c "peer chaincode install -p chaincodedev/chaincode/es-dollar -n USDAsset -v 0" """
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode instantiate -n USDAsset -v 0 -c \'{\"Args\":[\"a\",\"10\"]}\' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            print("USD asset instantiated")
            command = """sh -c "peer chaincode install -p chaincodedev/chaincode/es-energy -n EnergyAsset -v 0" """
            res = x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode instantiate -n EnergyAsset -v 0 -c '{"Args":["b","10"]}' -C myc"""
            res = x.exec_run(command)
            print("\n")
            print(res)
            print("Energy asset instantiated")
            command = """sh -c "peer chaincode install -p chaincodedev/chaincode/es-exchange -n Exchange -v 0" """
            res = x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode instantiate -n USDAsset -v 0 -c '{"Args":[]}' -C myc"""
            res = x.exec_run(command)
            print("\n")
            print(res)
            print("Exchange instantiated")
            ## Test
            command = """peer chaincode invoke -n Exchange -c '{"Args":["exchange", "a", "1", "b", "1"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n USDAsset -c '{"Args":["query","a"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n USDAsset -c '{"Args":["query","b"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n EnergyAsset -c '{"Args":["query","a"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            command = """peer chaincode query -n EnergyAsset -c '{"Args":["query","b"]}' -C myc"""
            res=x.exec_run(command)
            print("\n")
            print(res)
            print("Test successful")

if __name__ == '__main__':
    initiate()
