# ALU Logo Protection on Ethereum

**Repository:** https://github.com/shasha-12/alu-logo-blockchain-registry


This project registers the official African Leadership University (ALU) logo on a local Ethereum blockchain and then tokenises ownership of that logo into tradable shares.

`ALUAssetRegistry` is an ERC-721 (NFT) contract. It mints a unique token for the logo and permanently stores a SHA-256 fingerprint of the image file. Anyone can later hash a logo file they have and call `verifyLogoIntegrity()` to see whether it is the authentic original or a modified copy.

`ALULogoToken` is an ERC-20 contract. After the logo exists as an NFT, this contract issues 1,000,000 interchangeable ALUT tokens that represent ownership shares of the logo. The original owner receives the full supply at deployment and can later call `distributeShares()` to send portions to faculty, students, or administration.

The two contracts are related but separate: the NFT proves *which file* is the official logo and *who registered it*; the ERC-20 tokens represent *how ownership of that asset is split*.

## Official ALU logo SHA-256

The registered file is `alu-logo.png`, downloaded from ALU's official Naissance site (`naissance.alueducation.com/images/assets/alulogo.png`).

```
SHA-256:  ceddec61dafedd84ad1a1a0d43e26de0a84ad71493a4c21b3405adbc6ec191db
bytes32:  0xceddec61dafedd84ad1a1a0d43e26de0a84ad71493a4c21b3405adbc6ec191db
```

Anyone can independently verify this by running:

```bash
shasum -a 256 alu-logo.png
# or
node scripts/hash-logo.js
```

If even one pixel of the image is changed, the hash will be completely different and `verifyLogoIntegrity()` will return `"Warning: logo does not match."`

## Versions

| Tool | Version |
|------|---------|
| Node.js | 24.22.0 |
| npm | 11.19.1 |
| Hardhat | 2.29.1 |
| Solidity | 0.8.24 (EVM: Cancun) |
| OpenZeppelin Contracts | 5.6.1 |
| Ethers.js | 6.17.0 |

## How to run

### 1. Install dependencies

You need [Node.js](https://nodejs.org/) 18 or later.

```bash
cd "blockchain and applications_assignment"
npm install
```

### 2. Compile the contracts

```bash
npx hardhat compile
```

### 3. Run the automated tests

Eight tests cover registration, duplicate rejection, integrity checks, metadata lookup, token supply, share distribution, and ownership percentage:

```bash
npx hardhat test
```

Expected result: `8 passing`.

### 4. Start a local blockchain and deploy

In one terminal:

```bash
npx hardhat node
```

Hardhat prints 20 test wallet addresses, each funded with 10,000 fake ETH. Leave this process running.

In a second terminal:

```bash
npx hardhat run scripts/deploy.js --network localhost
```

The deploy script:

1. Deploys `ALUAssetRegistry`
2. Hashes `alu-logo.png` and calls `registerAsset()` so the official logo is token ID 1
3. Deploys `ALULogoToken`, minting 1,000,000 ALUT to the deployer

You can also deploy against Hardhat's in-memory network (no separate node) with:

```bash
npx hardhat run scripts/deploy.js
```

### 5. Generate the logo hash on its own

```bash
npm run hash
```

## Project layout

```
contracts/ALUAssetRegistry.sol   ERC-721 logo registry
contracts/ALULogoToken.sol       ERC-20 ownership shares
scripts/deploy.js                Deploys both contracts and registers the logo
scripts/hash-logo.js             Prints the SHA-256 of alu-logo.png
test/ALUAssetRegistry.test.js    Eight automated tests
alu-logo.png                     Official ALU logo used for the hash
hardhat.config.js                Solidity 0.8.24 / Hardhat configuration
Project_Report.pdf               Written report for Questions 1 and 2
```

## Problems encountered and how they were resolved

1. **OpenZeppelin 5.6.1 uses the Cancun `mcopy` opcode.** Compiling with Hardhat's default EVM target failed with `DeclarationError: Function "mcopy" not found`. Setting `evmVersion: "cancun"` in `hardhat.config.js` resolved it.

2. **The main ALU website is behind Cloudflare.** A direct download from `alueducation.com` was blocked. The official wordmark was instead taken from ALU's own Naissance site, which serves `alulogo.png`. The SHA-256 in this README is the hash of that file.

3. **`npm install` hit a one-off `ECONNRESET`.** Retrying the install completed normally.

## Next assignment

These contracts are written to be reused by a dApp. The registry exposes `registerAsset`, `verifyLogoIntegrity`, and `getAsset`. The token exposes `distributeShares` and `ownershipPercentage`. Events (`AssetRegistered`, `Transfer`) can be indexed from a frontend.
