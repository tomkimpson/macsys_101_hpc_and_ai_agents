# Pinned: '@latest' makes npx hit the registry on every run, which stalls.
MARP    := npx --yes @marp-team/marp-cli@4.5.0 --html
SRC     := slides.md
PDF     := slides.pdf
HTML    := slides.html
PPTX    := slides.pptx

.PHONY: pdf html pptx watch clean

pdf:
	$(MARP) $(SRC) --pdf --allow-local-files -o $(PDF)

html:
	$(MARP) $(SRC) --html --allow-local-files -o $(HTML)

pptx:
	$(MARP) $(SRC) --pptx --allow-local-files -o $(PPTX)

watch:
	$(MARP) $(SRC) --server --allow-local-files

clean:
	rm -f $(PDF) $(HTML) $(PPTX)
