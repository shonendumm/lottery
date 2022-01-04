from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, network, config
import time


#  https://youtu.be/M576WGiDBdQ?t=26019
    # when deploying Lottery, we need all these info:
    # address _priceFeedAddress, address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyhash

    # https://youtu.be/M576WGiDBdQ?t=26864
    # Continue above in getting the info for deploying lottery contract

    # https://youtu.be/M576WGiDBdQ?t=27274
    #  successfully deployed! And I found my error!

    # https://youtu.be/M576WGiDBdQ?t=27684
    # funding link token to the lottery contract to call randomness

    # https://youtu.be/M576WGiDBdQ?t=28106
    # writing tests for when running on development local ganache chain
    # because we don't have a chainlink node to return the randomness call

# https://youtu.be/M576WGiDBdQ?t=30053
# Chainlink mix


def deploy_lottery():
    # account = get_account("testWallet")
    account = get_account()
   
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address, # price feed address
        get_contract("vrf_coordinator").address, # vrf coordinator address
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"], {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False)
        )
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("Lottery is started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You've entered the lottery!")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # in the Lottery.sol, need to fund with link token to call requestrandomness
    # so we need to fund this contract first, then end the lottery
    # since funding the contract is a common function, we can add it to helpful scripts
    tx = fund_with_link(lottery.address) # the other parameters are default values
    tx.wait(1) # to wait for tx to fund through first
    ending_transaction = lottery.endLottery({"from": account}) # call contract's function
    ending_transaction.wait(1)
    time.sleep(180) # wait for node to finish the transactions and update on recent winner
    print(f"{lottery.recentWinner()} is the winner!")

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()

# deploy using default network (development), which will be local ganache-cli with mocks:
# brownie run scripts/deployLottery.py