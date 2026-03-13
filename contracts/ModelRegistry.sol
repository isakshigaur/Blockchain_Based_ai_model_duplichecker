// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

/// @title ModelRegistry
/// @notice Stores MD5 hashes of AI model artifacts to provide on-chain proof of ownership.
contract ModelRegistry {
    struct ModelRecord {
        address owner;
        string name;
        string ipfsCid;
        uint256 registeredAt;
    }

    mapping(bytes16 => ModelRecord) private records;

    event ModelRegistered(bytes16 indexed hash, address indexed owner, string name, string ipfsCid);

    /// @notice Returns true if the hash already exists in the registry.
    function isRegistered(bytes16 hash) external view returns (bool) {
        return records[hash].owner != address(0);
    }

    /// @notice Registers a new model hash. Fails if the hash already exists.
    /// @param hash MD5 fingerprint of the model artifact.
    /// @param name Human-readable model name or description.
    /// @param ipfsCid Optional IPFS CID pointing to the model or metadata.
    function registerModel(bytes16 hash, string calldata name, string calldata ipfsCid) external {
        require(records[hash].owner == address(0), "Model already registered");

        records[hash] = ModelRecord({
            owner: msg.sender,
            name: name,
            ipfsCid: ipfsCid,
            registeredAt: block.timestamp
        });

        emit ModelRegistered(hash, msg.sender, name, ipfsCid);
    }

    /// @notice Returns full metadata for a given hash.
    function getRecord(bytes16 hash) external view returns (ModelRecord memory) {
        require(records[hash].owner != address(0), "Model not found");
        return records[hash];
    }
}

