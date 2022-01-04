# USD 3895.54
# price of $50 usd = 0.0128 eth
# 12800000000000000 wei for $50 usd
from brownie import Lottery, accounts, config, network, exceptions
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link, get_contract
from web3 import Web3
from scripts.deployLottery import deploy_lottery
import pytest

# def deploy_lottery():
#     pass

# def main():
#     deploy_lottery()

def test_get_entrance_fee():
    # Unit integration test for local environment
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # arrange
    lottery = deploy_lottery()
    # act
    entrance_fee = lottery.getEntranceFee()
    # assert
    # if mocks starting price is 2000 usd / eth
    # and usdEntryFee = 50 usd which is 50/2000 eth (0.025 eth)
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    assert expected_entrance_fee == entrance_fee

def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # arrange
    lottery = deploy_lottery()
    # because it should raise an exception when we try to enter:
    # act/assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee() })

def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # assert
    assert lottery.players(0) == account

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # act
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    # assert
    # since the enum is at 2
    assert lottery.lottery_state() == 2 

def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})

    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})

    fund_with_link(lottery)
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    
    transaction = lottery.endLottery({"from": account})
    # get request_id info by using events emitted from the contract during endLottery()
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    # mocking a response from the chainlink node, e.g. VRFCoordinator
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address, {"from": account})
    # 77 % 3 remainder is 0, hence account is the winner
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery



# def test_get_entrance_fee():
#     print("hello test")
#     account = accounts[0]
#     lottery = Lottery.deploy(config["networks"][network.show_active()]["eth_usd_price_feed"], {"from": account})
#     print(f"lottery is {lottery.address}")
#     entranceFee = lottery.getEntranceFee()
#     print(f"Fee is {entranceFee}")
#     # assert lottery.getEntranceFee() > 12000000000000000
#     assert lottery.getEntranceFee() > Web3.toWei(0.010, "ether")
#     assert lottery.getEntranceFee() < Web3.toWei(0.014, "ether")

