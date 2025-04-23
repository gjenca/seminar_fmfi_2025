default: derived1.pdf lleft.pdf

.PRECIOUS: %.eps %.tex

%.pdf: %.eps
	epstopdf $(*F).eps

%.eps: %.ps
	ps2eps $(*F).ps -f -l

%.ps: %.dvi
	dvips -o $@ $(*F).dvi

%.dvi: %.tex
	latex --interaction=nonstopmode $(*F)

%.tex: %.py graphs.tex cdiagram.py cdutils.py
	python3 $(*F).py > $@

