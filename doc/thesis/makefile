DOCUMENT="thesis"

all: $(DOCUMENT).pdf

pdf: $(DOCUMENT).pdf

$(DOCUMENT).pdf: clean
	pdflatex $(DOCUMENT)
	# bibtex $(DOCUMENT)
	pdflatex $(DOCUMENT)
	pdflatex $(DOCUMENT)
	-rm -f *.log $(DOCUMENT).blg $(DOCUMENT).bbl $(DOCUMENT).toc *.aux $(DOCUMENT).out $(DOCUMENT).lof
	-rm -f *~

clean:
	-rm -f *.log $(DOCUMENT).blg $(DOCUMENT).bbl $(DOCUMENT).toc *.aux $(DOCUMENT).out $(DOCUMENT).lof
	-rm -f *~
	-rm -f $(DOCUMENT).dvi $(DOCUMENT).pdf

