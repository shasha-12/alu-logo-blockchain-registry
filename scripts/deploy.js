/**
 * Deployment script for the ALU logo protection system.
 *
 * 1. Deploy ALUAssetRegistry (ERC-721).
 * 2. Immediately register the official ALU logo using its real SHA-256 hash.
 * 3. Deploy ALULogoToken (ERC-20) and mint the full 1,000,000 ALUT supply
 *    to the deployer, who represents the original logo owner.
 *
 * Usage:
 *   npx hardhat run scripts/deploy.js
 *   npx hardhat run scripts/deploy.js --network localhost
 */
const hre = require("hardhat");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

function hashLogoFile() {
  const logoPath = path.join(__dirname, "..", "alu-logo.png");
  if (!fs.existsSync(logoPath)) {
    throw new Error(`ALU logo file not found at ${logoPath}`);
  }
  const digest = crypto.createHash("sha256").update(fs.readFileSync(logoPath)).digest("hex");
  return { logoPath, contentHash: "0x" + digest };
}

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const { logoPath, contentHash } = hashLogoFile();

  console.log("============================================================");
  console.log("ALU Logo Protection — deployment");
  console.log("============================================================");
  console.log("Deployer / logo owner:", deployer.address);
  console.log("Logo file:            ", logoPath);
  console.log("SHA-256 content hash: ", contentHash);
  console.log("");

  const Registry = await hre.ethers.getContractFactory("ALUAssetRegistry");
  const registry = await Registry.deploy();
  await registry.waitForDeployment();
  const registryAddress = await registry.getAddress();
  console.log("ALUAssetRegistry deployed to:", registryAddress);

  const tx = await registry.registerAsset(
    "ALU Official Logo",
    "image/png",
    contentHash
  );
  const receipt = await tx.wait();

  const registeredEvent = receipt.logs
    .map((log) => {
      try {
        return registry.interface.parseLog(log);
      } catch {
        return null;
      }
    })
    .find((parsed) => parsed && parsed.name === "AssetRegistered");

  const tokenId = registeredEvent ? registeredEvent.args.tokenId : 1n;
  console.log("ALU logo registered as token ID:", tokenId.toString());
  console.log("Registration tx hash:          ", receipt.hash);

  const Token = await hre.ethers.getContractFactory("ALULogoToken");
  const token = await Token.deploy(deployer.address);
  await token.waitForDeployment();
  const tokenAddress = await token.getAddress();

  const ownerBalance = await token.balanceOf(deployer.address);
  console.log("ALULogoToken deployed to:      ", tokenAddress);
  console.log(
    "ALUT minted to logo owner:     ",
    hre.ethers.formatUnits(ownerBalance, 18),
    "ALUT"
  );
  console.log("============================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
