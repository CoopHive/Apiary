cd ..
apiary start-buy --config-path ./config/buyer_naive.json --job-path ./jobs/docker/cowsay.Dockerfile --job-input-variables 'Paying with ERC20, ERC721 or a generic combination of the two for Compute jobs is very nice!' --tokens-data '["ERC20", "0x81f8f0bb1cB2A06649E51913A151F0E7Ef6FA321", 10]'
