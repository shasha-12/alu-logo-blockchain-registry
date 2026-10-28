// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ALULogoToken
 * @author ALU Blockchain and Applications
 * @notice ERC-20 token that represents fractional ownership shares of the
 *         official ALU logo after it has been registered as an NFT.
 *
 * @dev Tokenisation means taking a unique asset (the ALU logo NFT) and
 *      issuing interchangeable shares of its economic / governance rights.
 *      Those shares are fungible: 1 ALUT is always equal to any other ALUT,
 *      which is why ERC-20 is the correct standard here, while the logo
 *      file itself stays unique under ERC-721.
 *
 *      The total supply is fixed at 1,000,000 ALUT (with 18 decimals, so
 *      1_000_000 * 10^18 base units). All tokens are minted to the original
 *      logo owner at deployment. New tokens can never be minted afterwards.
 */
contract ALULogoToken is ERC20, Ownable {
    /// @notice Human-readable total supply: 1,000,000 ALUT.
    uint256 public constant INITIAL_SUPPLY = 1_000_000 * 10 ** 18;

    /**
     * @param logoOwner Wallet that currently owns the registered logo NFT.
     *        Receives the full 1,000,000 ALUT supply and becomes the
     *        Ownable owner who may later call distributeShares().
     */
    constructor(address logoOwner) ERC20("ALU Logo Token", "ALUT") Ownable(logoOwner) {
        require(logoOwner != address(0), "Logo owner cannot be the zero address");
        _mint(logoOwner, INITIAL_SUPPLY);
    }

    /**
     * @notice Transfer ownership shares from the original owner to a stakeholder.
     * @dev Restricted with OpenZeppelin's `onlyOwner` modifier so that only
     *      ALU (the logo owner) can issue shares from the treasury balance.
     *      `amount` is expressed in base units (18 decimals). To send 100,000
     *      ALUT pass 100000 * 10^18, or in ethers.js: ethers.parseUnits("100000", 18).
     * @param recipient Wallet that will receive the shares.
     * @param amount Number of ALUT base units to transfer.
     */
    function distributeShares(address recipient, uint256 amount) external onlyOwner {
        require(recipient != address(0), "Recipient cannot be the zero address");
        require(amount > 0, "Amount must be greater than zero");
        _transfer(owner(), recipient, amount);
    }

    /**
     * @notice Whole-number ownership percentage of `account`.
     * @dev Calculated as balance * 100 / totalSupply(). Solidity integer
     *      division truncates remainders, so 100,000 ALUT out of 1,000,000
     *      returns 10, and 500,000 ALUT returns 50.
     * @param account Wallet to inspect.
     * @return percentage Ownership share in the range 0–100.
     */
    function ownershipPercentage(address account) public view returns (uint256 percentage) {
        uint256 supply = totalSupply();
        if (supply == 0) {
            return 0;
        }
        percentage = (balanceOf(account) * 100) / supply;
    }
}
