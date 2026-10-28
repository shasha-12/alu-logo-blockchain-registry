/**
 * Automated tests for ALUAssetRegistry (ERC-721) and ALULogoToken (ERC-20).
 *
 * The assignment requires eight scenarios:
 *   1. The ALU logo registers successfully and returns a token ID
 *   2. Registering the same hash a second time is rejected
 *   3. verifyLogoIntegrity() returns true for the correct hash
 *   4. verifyLogoIntegrity() returns false for an incorrect hash
 *   5. getAsset() returns the correct name and file type
 *   6. 1,000,000 ALUT are minted to the logo owner on deployment
 *   7. distributeShares() transfers tokens to a recipient
 *   8. ownershipPercentage() returns the correct percentage
 */
const { expect } = require("chai");
const { ethers } = require("hardhat");
const { anyValue } = require("@nomicfoundation/hardhat-chai-matchers/withArgs");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const LOGO_PATH = path.join(__dirname, "..", "alu-logo.png");
const LOGO_NAME = "ALU Official Logo";
const LOGO_TYPE = "image/png";
const TOTAL_SUPPLY = ethers.parseUnits("1000000", 18);

function sha256File(filePath) {
  const digest = crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
  return "0x" + digest;
}

function randomHash() {
  return ethers.hexlify(ethers.randomBytes(32));
}

describe("ALUAssetRegistry", function () {
  let registry;
  let owner;
  let other;
  let logoHash;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();
    logoHash = sha256File(LOGO_PATH);

    const Registry = await ethers.getContractFactory("ALUAssetRegistry");
    registry = await Registry.deploy();
    await registry.waitForDeployment();
  });

  it("registers the ALU logo successfully and returns a token ID", async function () {
    const returnedId = await registry.registerAsset.staticCall(
      LOGO_NAME,
      LOGO_TYPE,
      logoHash
    );
    expect(returnedId).to.equal(1n);

    const tx = await registry.registerAsset(LOGO_NAME, LOGO_TYPE, logoHash);
    await expect(tx)
      .to.emit(registry, "AssetRegistered")
      .withArgs(1, LOGO_NAME, logoHash, owner.address, anyValue);

    expect(await registry.ownerOf(1)).to.equal(owner.address);
    expect(await registry.registeredHashes(logoHash)).to.equal(true);
  });

  it("rejects a second registration of the same content hash", async function () {
    await registry.registerAsset(LOGO_NAME, LOGO_TYPE, logoHash);

    await expect(
      registry.connect(other).registerAsset("Fake ALU Logo", LOGO_TYPE, logoHash)
    ).to.be.revertedWith("Asset already registered: duplicate content hash");
  });

  it("verifyLogoIntegrity() returns true when the correct hash is supplied", async function () {
    await registry.registerAsset(LOGO_NAME, LOGO_TYPE, logoHash);

    const result = await registry.verifyLogoIntegrity(1, logoHash);
    expect(result.isAuthentic).to.equal(true);
    expect(result.message).to.equal("Logo is authentic.");
  });

  it("verifyLogoIntegrity() returns false when an incorrect hash is supplied", async function () {
    await registry.registerAsset(LOGO_NAME, LOGO_TYPE, logoHash);

    const result = await registry.verifyLogoIntegrity(1, randomHash());
    expect(result.isAuthentic).to.equal(false);
    expect(result.message).to.equal("Warning: logo does not match.");
  });

  it("getAsset() returns the correct asset name and file type for a registered token", async function () {
    await registry.registerAsset(LOGO_NAME, LOGO_TYPE, logoHash);

    const asset = await registry.getAsset(1);
    expect(asset.name).to.equal(LOGO_NAME);
    expect(asset.fileType).to.equal(LOGO_TYPE);
    expect(asset.contentHash).to.equal(logoHash);
    expect(asset.registrant).to.equal(owner.address);
    expect(asset.timestamp).to.be.greaterThan(0n);
  });
});

describe("ALULogoToken", function () {
  let token;
  let owner;
  let faculty;
  let student;

  beforeEach(async function () {
    [owner, faculty, student] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("ALULogoToken");
    token = await Token.deploy(owner.address);
    await token.waitForDeployment();
  });

  it("mints the full supply of 1,000,000 ALUT tokens to the logo owner on deployment", async function () {
    expect(await token.name()).to.equal("ALU Logo Token");
    expect(await token.symbol()).to.equal("ALUT");
    expect(await token.totalSupply()).to.equal(TOTAL_SUPPLY);
    expect(await token.balanceOf(owner.address)).to.equal(TOTAL_SUPPLY);
    expect(await token.owner()).to.equal(owner.address);
  });

  it("distributeShares() correctly transfers the specified number of tokens to a recipient", async function () {
    const amount = ethers.parseUnits("100000", 18);

    await expect(token.distributeShares(faculty.address, amount))
      .to.emit(token, "Transfer")
      .withArgs(owner.address, faculty.address, amount);

    expect(await token.balanceOf(faculty.address)).to.equal(amount);
    expect(await token.balanceOf(owner.address)).to.equal(TOTAL_SUPPLY - amount);

    await expect(
      token.connect(faculty).distributeShares(student.address, amount)
    ).to.be.revertedWithCustomError(token, "OwnableUnauthorizedAccount");

    await expect(
      token.distributeShares(student.address, 0)
    ).to.be.revertedWith("Amount must be greater than zero");
  });

  it("ownershipPercentage() returns the correct percentage for a known token balance", async function () {
    const half = ethers.parseUnits("500000", 18);
    const tenth = ethers.parseUnits("100000", 18);

    await token.distributeShares(faculty.address, half);
    await token.distributeShares(student.address, tenth);

    expect(await token.ownershipPercentage(faculty.address)).to.equal(50n);
    expect(await token.ownershipPercentage(student.address)).to.equal(10n);
    expect(await token.ownershipPercentage(owner.address)).to.equal(40n);
  });
});

