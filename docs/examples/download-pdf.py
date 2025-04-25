import arxiv

paper = next(arxiv.Client().results(arxiv.Search(id_list=["1605.08386v1"])))
# Download the PDF to the PWD with a default filename.
paper.download_pdf()
# Download the PDF to the PWD with a custom filename.
paper.download_pdf(filename="downloaded-paper.pdf")
# Download the PDF to a specified directory with a custom filename.
paper.download_pdf(dirpath="./mydir", filename="downloaded-paper.pdf")
