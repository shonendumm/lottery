1. Users can enter lottery with ETH based on a USD fee
2. Admin will choose when lottery is over
3. Lottery will select a random winner

### Notes

Currently, only works on rinkeby network.
For mainnet-fork network, will need to input respective addresses in brownie-config.

### To run, use terminal command:

brownie run scripts/deployLottery.py --network rinkeby
