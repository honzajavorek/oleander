DOCUMENT=thesis
CLASS_DIR=../fithesis

all: $(DOCUMENT).pdf

pdf: $(DOCUMENT).pdf

$(DOCUMENT).pdf: clean
	( \
		TEXINPUTS=.:./images:${CLASS_DIR}:${TEXINPUTS:-:} && \
		export TEXINPUTS && \
	 	pdflatex $(DOCUMENT) && \
	 	bibtex $(DOCUMENT) && \
	 	pdflatex $(DOCUMENT) && \
	 	pdflatex $(DOCUMENT) \
	)
	-rm -f *.log $(DOCUMENT).blg $(DOCUMENT).bbl $(DOCUMENT).toc *.aux $(DOCUMENT).out $(DOCUMENT).lof $(DOCUMENT).lot
	-rm -f *~

clean:
	-rm -f *.log $(DOCUMENT).blg $(DOCUMENT).bbl $(DOCUMENT).toc *.aux $(DOCUMENT).out $(DOCUMENT).lof $(DOCUMENT).lot
	-rm -f *~
	-rm -f $(DOCUMENT).dvi $(DOCUMENT).pdf

