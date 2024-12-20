BUYER='0x002189E2F82ac8FBF19e2Dc279d19E07eCE12cfb'
SELLER='0x1C53Ec481419daA436B47B2c916Fa3766C6Da9Fc'

VITA=0x81f8f0bb1cB2A06649E51913A151F0E7Ef6FA321
NEURON=0xab814ce69E15F6B9660A3B184c0B0C97B9394A6b
ATH=0xA4fFdf3208F46898CE063e25c1C43056FA754739
RSC=0xD101dCC414F310268c37eEb4cD376CcFA507F571
GROW=0x761A3557184cbC07b7493da0661c41177b2f97fA
CRYO=0xf4308b0263723b121056938c2172868E408079D0
LAKE=0xF9Ca9523E5b5A42C3018C62B084Db8543478C400
HAIR=0x9Ce115f0341ae5daBC8B477b74E83db2018A6f42
GLW_BETA=0xf4fbC617A5733EAAF9af08E1Ab816B103388d8B6
AXGT=0xDd66781D0E9a08D4FBb5eC7BAc80B691BE27F21D
NOBL=0x88b9f5c66342eBaf661b3E2836B807C8cb1B3195
WEL=0x1E762e1FAc176bbB341656035daf5601b1C69Be5
IPNFT=0xcaD88677CA87a7815728C72D74B4ff4982d54Fc1

# Define arrays for tokens and holders
SYMBOLS=("VITA" "NEURON" "ATH" "RSC" "GROW" "CRYO" "LAKE" "HAIR" "AXGT" "NOBL" "WEL" "IPNFT")
TOKENS=($VITA $NEURON $ATH $RSC $GROW $CRYO $LAKE $HAIR $AXGT $NOBL $WEL $IPNFT)

# Loop through tokens and holders
for i in ${!TOKENS[@]}; do
  TOKEN=${TOKENS[$i]}
  SYMBOL=${SYMBOLS[$i]}

  for RECEIVER in $BUYER $SELLER; do
    # Check the balance of the receiver
    BALANCE=$(cast call "$TOKEN" "balanceOf(address)(uint256)" "$RECEIVER" --rpc-url "$RPC_URL")
    echo "Token: $SYMBOL, Wallet: $RECEIVER, Balance: $BALANCE"
  done
done
