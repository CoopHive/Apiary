cd ..
apiary start-buy --config-path ./config/buyer_naive.json --job-path ./jobs/docker/convert.Dockerfile --job-input-volume-path ./jobs/input/papers --job-input-variables 'marker' --tokens-data '["ERC20", "0x81f8f0bb1cB2A06649E51913A151F0E7Ef6FA321", 10]'
