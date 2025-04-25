import arxiv

paper = next(arxiv.Client().results(arxiv.Search(id_list=["1605.08386v1"])))
# Download the archive to the PWD with a default filename.
paper.download_source()
# Download the archive to the PWD with a custom filename.
paper.download_source(filename="downloaded-paper.tar.gz")
# Download the archive to a specified directory with a custom filename.
paper.download_source(dirpath="./mydir", filename="downloaded-paper.tar.gz")

