%%
% This file provides settings for format of harvard ALM thesis
% Based on report, it configures these basic settings:
% - margins
% - line and paragraph spacing
% - titles
% - table of contents
% - bibliography
%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{harvardalmthesis}[2009/07/01]


%  Thesis looks like report
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
\ProcessOptions
\LoadClass[12pt]{report}


%------------------------------------------------------------
% MARGINS

% (left,right,top,bottom) = (1.5, 1, 1, 1)
% no header
\usepackage[left=1.5in,right=1in,top=1in,bottom=1in,includefoot,nohead]{geometry}

%------------------------------------------------------------
% LINE AND PARAGRAPH SPACING

% double spacing by default
\usepackage{setspace}
\doublespacing


% PARAGRAPH
\usepackage{indentfirst}

% new paragraphs indented 0.5in
\parindent 0.5in

% with no additional spacing between paragraphs


%------------------------------------------------------------
% TITLES

\usepackage{titlesec}
\usepackage{titletoc}

% chater title, large font, phv, center-aligned
\titleformat{\chapter}[block]
{\normalfont\Large\fontfamily{phv}\fontseries{m}\selectfont\filcenter}
{\chaptertitlename\space\thechapter:}
{10pt}
{}

% section, normal font, phv, center-aligned
\titleformat{\section}[block]
{\normalfont\fontfamily{phv}\fontseries{m}\selectfont\filcenter}
{\thesection.}
{10pt}
{}

% subsection, normal font, phv, left-aligned
\titleformat{\subsection}[block]
{\normalfont\fontfamily{phv}\fontseries{m}\selectfont\filright}
{\thesubsection}
{10pt}
{}


% subsubsection, with period after, normal font, phv, left-aligned
\usepackage{soul}
\newcommand{\periodafter}[2]{#1{#2}.}
\titleformat{\subsubsection}[runin]
{\normalfont\fontfamily{ptm}\fontseries{m}\selectfont\filright}
{}
{0pt}  % no subsection header, no need for extra space
{\periodafter{\ul}}
\titlespacing{\subsubsection}{\parindent}{0pt}{1ex plus .2ex minus .1ex}

% ------------------------------------------------------------
% TABLE OF CONTENTS

%\renewcommand\contentsname{Table of Contents}

%%% Control the fonts and formatting used in the table of contents.
\usepackage[titles]{tocloft}

%\cftsetindents{figure}{1.5em}{3em}
%\cftsetindents{table}{1.5em}{3em}
%\renewcommand{\@numwidth}{1em}

% for listing
%%\def\l@lstlisting#1#2{\@dottedtocline{1}{1.5em}{3em}{#1}{#2}}

%% list of equations
\newcommand{\listequationsname}{List of Equations}

%------------------------------------------------------------
% BIBLIOGRAPHY


\usepackage{natbib}


%------------------------------------------------------------


