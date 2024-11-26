FROM python:3.9-slim
RUN pip install --no-cache-dir lighthouseweb3
COPY run_chunker.py run_embedder.py ./

# Specify cid of pdf previously uploaded from buyer to ipfs. 
# This is hardcoded in the docker image.
# pdf_ipfs_cid =

CMD ["bash", "-c", "python -c 'from lighthouseweb3 import Lighthouse; import os; lh = Lighthouse(); lh.download(\"pdf_ipfs_cid\")' && python run_chunker.py && python run_embedder.py"]

# run_chunker and run_embedder here are given as scripts, assuming they automatically find the pdf downloaded from IPFS.
# Ideally you should make the pdf-to-markdown a function with an API like this:
# CMD ["bash", "-c", "python -c 'from lighthouseweb3 import Lighthouse; import os; lh = Lighthouse(); lh.download(\"pdf_ipfs_cid\")' && pdf_to_markdown('path_to_input.pdf'=str, converter=conv1, chunker=chunk2, embedder=emb1)"]

# Something like this:
# pdf_to_markdown(path_to_input=str, converter=Enumerate[conv1, conv2,....], chunker=Enumerate[chunk1, chunk2,...], embedder=Enumerate[emb1, emb2])"

# So it is responsibility of the buyer to upload a pdf to ipfs
# it is responsibility of the dockerfile to download pdf from ipfs.
# the markdown output will be uploaded to ipfs as a string to be read and parsed by the buyer.
