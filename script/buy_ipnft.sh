cd ..
apiary start-buy --config-path ./config/buyer_naive.json --job-path ./jobs/docker/cowsay.Dockerfile --job-input-variables 'Paying with ERC20, ERC721 or a generic combination of the two for Compute jobs is very nice!' --tokens-data '["ERC721", "0xcaD88677CA87a7815728C72D74B4ff4982d54Fc1", 44]'
