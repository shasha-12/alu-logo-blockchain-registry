require("@nomicfoundation/hardhat-toolbox");

/**
 * Hardhat configuration for the ALU logo registry project.
 *
 * Solidity 0.8.24 is used because it is a stable compiler that is fully
 * compatible with OpenZeppelin Contracts v5.
 *
 * The built-in `hardhat` network is an in-memory local blockchain used by
 * `npx hardhat test`. The `localhost` network is used when you start a
 * persistent node with `npx hardhat node` and then deploy to it.
 *
 * To deploy to the Ethereum Sepolia testnet later, add a `sepolia` entry
 * with a RPC URL and a funded private key stored in environment variables.
 * Never commit private keys to git.
 */
/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      evmVersion: "cancun",
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {},
    localhost: {
      url: "http://127.0.0.1:8545",
    },
  },
  mocha: {
    timeout: 40000,
  },
};
