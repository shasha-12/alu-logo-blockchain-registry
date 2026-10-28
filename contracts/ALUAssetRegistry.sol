// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";

/**
 * @title ALUAssetRegistry
 * @author ALU Blockchain and Applications
 * @notice Registers the official African Leadership University logo as a
 *         unique ERC-721 NFT and stores a SHA-256 fingerprint of the file
 *         so anyone can later check whether a copy of the logo is authentic.
 *
 * @dev Why ERC-721? Each logo file is unique. Two different files must never
 *      be treated as interchangeable, which is exactly what a non-fungible
 *      token represents. The contract extends OpenZeppelin's audited ERC-721
 *      implementation so minting, ownership, and transfers follow the
 *      standard that wallets and marketplaces already understand.
 */
contract ALUAssetRegistry is ERC721 {
    /**
     * @notice Permanent registration record for one digital asset.
     * @param name Human-readable asset name, e.g. "ALU Official Logo".
     * @param fileType MIME type or extension, e.g. "image/png".
     * @param contentHash SHA-256 digest of the exact file bytes, stored as bytes32.
     * @param registrant Wallet that called registerAsset() and received the NFT.
     * @param timestamp Unix time at which the asset was registered on-chain.
     */
    struct AssetMetadata {
        string name;
        string fileType;
        bytes32 contentHash;
        address registrant;
        uint256 timestamp;
    }

    /// @dev Token IDs start at 1 so that ID 0 can never be confused with "unset".
    uint256 private _nextTokenId;

    /// @notice tokenId => registration details. Anyone can look this up.
    mapping(uint256 => AssetMetadata) public assets;

    /// @notice contentHash => true once that exact file has been registered.
    /// @dev Used to reject duplicate registrations of the same logo file.
    mapping(bytes32 => bool) public registeredHashes;

    /**
     * @notice Emitted when a new asset is minted and recorded.
     * @param tokenId Newly assigned NFT identifier.
     * @param name Asset name supplied by the registrant.
     * @param contentHash SHA-256 fingerprint stored on-chain.
     * @param registrant Address that received the NFT.
     * @param timestamp Block timestamp of the registration.
     */
    event AssetRegistered(
        uint256 indexed tokenId,
        string name,
        bytes32 indexed contentHash,
        address indexed registrant,
        uint256 timestamp
    );

    constructor() ERC721("ALU Official Logo", "ALUL") {
        _nextTokenId = 1;
    }

    /**
     * @notice Register a new digital asset and mint an NFT to the caller.
     * @dev Reverts if `contentHash` has already been used so the same file
     *      cannot be claimed twice. The hash is the fingerprint of the file
     *      itself, not of the file name, so renaming the logo cannot bypass
     *      this check.
     * @param name Display name of the asset.
     * @param fileType File type, for example "image/png".
     * @param contentHash SHA-256 hash of the file, passed as a 32-byte value.
     * @return tokenId The newly minted token identifier.
     */
    function registerAsset(
        string memory name,
        string memory fileType,
        bytes32 contentHash
    ) public returns (uint256 tokenId) {
        require(bytes(name).length != 0, "Asset name cannot be empty");
        require(bytes(fileType).length != 0, "File type cannot be empty");
        require(contentHash != bytes32(0), "Content hash cannot be empty");
        require(
            !registeredHashes[contentHash],
            "Asset already registered: duplicate content hash"
        );

        tokenId = _nextTokenId;
        unchecked {
            _nextTokenId = tokenId + 1;
        }

        // Mint the NFT to the caller. _safeMint checks that a contract
        // recipient can receive ERC-721 tokens.
        _safeMint(msg.sender, tokenId);

        assets[tokenId] = AssetMetadata({
            name: name,
            fileType: fileType,
            contentHash: contentHash,
            registrant: msg.sender,
            timestamp: block.timestamp
        });

        registeredHashes[contentHash] = true;

        emit AssetRegistered(
            tokenId,
            name,
            contentHash,
            msg.sender,
            block.timestamp
        );
    }

    /**
     * @notice Compare a caller-supplied SHA-256 hash against the hash stored
     *         for a registered token.
     * @dev This is a `view` function. It only reads state, so calling it
     *      off-chain (for example from a dApp or `eth_call`) costs no gas.
     * @param tokenId The registered NFT to check against.
     * @param contentHash The SHA-256 hash of the file the caller currently has.
     * @return isAuthentic True when the hashes match.
     * @return message "Logo is authentic." or "Warning: logo does not match."
     */
    function verifyLogoIntegrity(
        uint256 tokenId,
        bytes32 contentHash
    ) public view returns (bool isAuthentic, string memory message) {
        _requireOwned(tokenId);

        if (assets[tokenId].contentHash == contentHash) {
            return (true, "Logo is authentic.");
        }

        return (false, "Warning: logo does not match.");
    }

    /**
     * @notice Return the full registration record for a token ID.
     * @dev Anyone can call this at any time. The data cannot be edited after
     *      registration because the contract exposes no setter that overwrites
     *      `assets[tokenId]`.
     * @param tokenId The NFT whose metadata should be returned.
     * @return The AssetMetadata struct stored for that token.
     */
    function getAsset(
        uint256 tokenId
    ) public view returns (AssetMetadata memory) {
        _requireOwned(tokenId);
        return assets[tokenId];
    }
}
