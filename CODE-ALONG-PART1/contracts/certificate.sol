// SPDX-License-Identifier: Toronto
pragma solidity ^0.8.1;

    import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol";    
    import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
    import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol";
    
    contract Certificate is ERC721Enumerable, Ownable {
        using Strings for uint256;     
        
        mapping (uint256 => string) private _tokenURIs;

        constructor(string memory _name, string memory _symbol)
            ERC721(_name, _symbol)
        {}
        
        function _setTokenURI(uint256 tokenId, string memory _tokenURI) internal {
            require(_exists(tokenId), "Token does not exist to add URI");
            _tokenURIs[tokenId] = _tokenURI;
        }

        function mint(address recipient, string memory nftURI) external onlyOwner() {
            uint256 tokenId = totalSupply();
            _mint(recipient, tokenId);
            _setTokenURI(tokenId, nftURI);
        }
      
        function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
            require(_exists(tokenId), "Token does not exist");

            string memory _tokenURI = _tokenURIs[tokenId];
            //string memory base = _baseURI(); //Note: Some contracts use the internal baseURI function - we aren't here
 
            return _tokenURI;
        }        


    }