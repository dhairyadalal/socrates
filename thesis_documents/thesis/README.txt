
This directory contains a template that might be helpful for writing a
master thesis for Harvard Extension School in Latex. It tries to
follow the specifications outlined in 'A Guide to the ALM
Thesis'. Note that the specifications might be updated, please review
them carefully. 

I developed and used it for my thesis in Information Technology in
2009.  I received helpful inputs from Dr. Jeff Parker.  The chapter
organization and included texts are only to demonstrate certain
effects in Latex; yours could be very different.

'harvardext-thesis-example.pdf' is an example result PDF.

'harvardalmthesis.cls' contains some of the overall requirements
like margins, spacing and sections' title.

'settings.tex' contains personal customizations like graphics, math,
algorithm/code listing, and glossary.

'main.tex' is the master file.

The main command to run latex to generate PDF is:

 pdflatex  --shell-escape  "\nonstopmode\input{main.tex}"

The result PDF is 'main.pdf'.


best of luck,
Huy Nguyen

--------------------------------------------------------------------------------

The temp files are: *.aux *.bbl *.blg *.dvi *.equ *.glg *.glo *.gls *.ist *.loa *.lof *.log *.lol *.lot *.out *.toc *.synctex.gz auto

Here is a sequence of commands to include the glossary with page
references:

 pdflatex  --shell-escape  "\nonstopmode\input{main.tex}"
 makeindex -s main.ist -t main.glg -o main.gls main.glo
 ./makeglossaries.pl main
 pdflatex  --shell-escape  "\nonstopmode\input{main.tex}"
 pdflatex  --shell-escape  "\nonstopmode\input{main.tex}"

Here is a sequence of commands to include bibliography with references:

 pdflatex  --shell-escape  "\nonstopmode\input{main.tex}"
 bibtex main
 pdflatex  --shell-escape  "\nonstopmode\input{main.tex}"
 pdflatex  --shell-escape  "\nonstopmode\input{main.tex}"


Here is a list of all files in this folder:
.
|-- README.txt
|-- abstract.tex
|-- acknowledgment.tex
|-- code
|   `-- java
|       |-- SampleSetAction.java
|       `-- sampleSet.xhtml
|-- code.tex
|-- code_java.tex
|-- conclusion.tex
|-- design.tex
|-- development.tex
|-- diagrams
|   |-- Architecture2.dot
|   |-- Architecture2.pdf
|   |-- Architecture2.png
|   |-- System.pdf
|   `-- System.svg
|-- glossary.tex
|-- harvardalmthesis.cls
|-- harvardext-thesis-example.pdf
|-- implement.tex
|-- intro.tex
|-- lcs.tex
|-- main.bib
|-- main.pdf
|-- main.tex
|-- makeglossaries
|-- makeglossaries.bat.txt
|-- makeglossaries.pl
|-- requirements.tex
|-- sequence.tex
|-- settings.tex
|-- src
|   `-- main
|       `-- java
|           `-- com
|               `-- myapp
|                   `-- magi
|                       `-- account
|                           `-- business
|                               |-- AccountManager.java
|                               `-- AccountManagerBean.java
`-- title.tex

11 directories, 34 files

