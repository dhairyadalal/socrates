#!/usr/bin/env perl

# File    : makeglossaries
# Author  : Nicola Talbot
# Version : 1.8 (2009/11/03)
# Description: simple Perl script that calls makeindex or xindy.
# Intended for use with "glossaries.sty" (saves having to remember
# all the various switches)

# This file is distributed as part of the glossaries LaTeX package.
# Copyright 2007 Nicola L.C. Talbot
# This work may be distributed and/or modified under the
# conditions of the LaTeX Project Public License, either version 1.3
# of this license or any later version.
# The latest version of this license is in
#   http://www.latex-project.org/lppl.txt
# and version 1.3 or later is part of all distributions of LaTeX
# version 2005/12/01 or later.
#
# This work has the LPPL maintenance status `maintained'.
#
# The Current Maintainer of this work is Nicola Talbot.

# This work consists of the files glossaries.dtx and glossaries.ins 
# and the derived files glossaries.sty, mfirstuc.sty,
# glossary-hypernav.sty, glossary-list.sty, glossary-long.sty,
# glossary-super.sty, glossaries.perl.
# Also makeglossaries and makeglossaries.

my $version="1.7 (2009-09-23)";

# History:
# v1.8 (2009-11-03) :
#   * Create an empty output file if the input file is empty
#     without calling xindy/makeindex
# v1.7 (2009-09-23) :
#   * Issue warning rather than error when empty/non existant file 
#     checks fail
# v1.6 (2009-05-24) :
#   * main glossary no longer automatically added
#     (only added if information in aux file)
#   * if file extension is specified, check added to ensure it
#     corresponds to a known glossary extension.
#   * added file existance test and file empty test
# v1.5 (2008-12-26) :
#   * added support for xindy
#   * picks up ordering information from aux file
# v1.4 (2008-05-10) :
#   * added support for filenames with spaces.
# v1.3 (2008-03-08) :
#   * changed first line from /usr/bin/perl -w to /usr/bin/env perl
#     (Thanks to Karl Berry for suggesting this.)
# v1.2 (2008-03-02) :
#   * added support for --help and --version
#   * improved error handling
# v1.1 (2008-02-13) :
#   * added -w and strict
#   * added check to ensure .tex file not passed to makeglossaries
#
# v1.0 (2007-05-10) : Initial release.

use Getopt::Std;
use strict;
use vars qw($opt_q $opt_t $opt_o $opt_s $opt_p $opt_g $opt_c $opt_r
   $opt_l $opt_i $opt_L $opt_n $opt_C);


$Getopt::Std::STANDARD_HELP_VERSION = 1;

# v1.5 added -L <lang> for xindy (but language can be specified in 
# .tex file)
# v1.5 added -n (print the command that would be issued but
# don't actually run the command)
getopts('s:o:t:p:L:C:ilqrcgn');

unless ($#ARGV == 0)
{
   die "makeglossaries: Need exactly one file argument.\nUse `makeglossaries --help' for help.\n";
}

# define known extensions

# v1.6: removed adding main glossary here as there's no guarantee
# that it's been used. If it has been used, the information will
# be picked up later in the aux file
my %exttype = (
#   main => {in=>'glo', out=>'gls', 'log'=>'glg'},
 );

# v1.5 define require languages for xindy

my %language = ();
my %codepage = ();

my $ext = '';
my $name = $ARGV[0];

# modified this to make sure users don't try passing the
# tex file:
if (length($ARGV[0]) > 3 and substr($ARGV[0],-4,1) eq ".")
{
  $name = substr($ARGV[0],0,length($ARGV[0])-4);

  $ext = substr($ARGV[0],-3,3);

  if (lc($ext) eq 'tex')
  {
     die("Don't pass the tex file to makeglossaries:\n"
        ."either omit the extension to make all the glossaries, "
        ."or specify one of the glossary files, e.g. $name.glo, to "
        ."make just that glossary.\n")
  }
}

my $istfile = "";

# should letter ordering be used? (v1.5 added)

my $letterordering = defined($opt_l);

# check aux file for other glossary types
# and for ist file name

if (open AUXFILE, "$name.aux")
{
   while (<AUXFILE>)
   {
      if (m/\\\@newglossary\s*\{(.*)\}{(.*)}{(.*)}{(.*)}/)
      {
         $exttype{$1}{'log'} = $2;
         $exttype{$1}{'out'} = $3;
         $exttype{$1}{'in'}  = $4;

         unless ($opt_q)
         {
            print "added glossary type '$1' ($2,$3,$4)\n";
         }
      }

      if (m/\\\@istfilename\s*{([^}]*)}/)
      {
         $istfile = $1;

         # check if double quotes were added to \jobname
         $istfile=~s/^"(.*)"\.ist$/$1.ist/;
      }

      # v1.5 added
      if (m/\\\@xdylanguage\s*{([^}]+)}{([^}]*)}/)
      {
         $language{$1} = $2;
      }

      # v1.5 added
      if (m/\\\@gls\@codepage\s*{([^}]+)}{([^}]*)}/)
      {
         $codepage{$1} = $2;
      }

      # v1.5 added
      # Allow -l switch to override specification in aux file
      unless (defined($opt_l))
      {
         if (m/\\\@glsorder\s*{([^}]+)}/)
         {
            my $ordering = $1;

            if ($ordering eq "word")
            {
               $letterordering = 0;
            }
            elsif ($ordering eq "letter")
            {
               $letterordering = 1;
            }
            else
            {
               print STDERR
                 "Unknown ordering '$letterordering'\n",
                 "Assuming word ordering\n";
               $letterordering = 0;
            }
         }
      }
   }

   close AUXFILE;
}
else
{
   print STDERR "Unable to open $name.aux: $!\n";
}

# has the style file been specified?
unless ($istfile)
{
   die "No \\\@istfilename found in '$name.aux'.\n",
       "Did your LaTeX run fail?\n",
       "Did your LaTeX run produce any output?\n",
       "Did you remember to use \\makeglossaries?\n";
}

# v1.5 save the general xindy switches

my $xdyopts = '';

unless ($opt_L eq "")
{
  $xdyopts .= " -L $opt_L";
}

# save all the general makeindex switches

my $mkidxopts = '';

if ($opt_i)
{
   $mkidxopts .= " -i";
}

if ($letterordering)
{
   $mkidxopts .= " -l";
   $xdyopts .= " -M ord/letorder";
}

if ($opt_q)
{
   $mkidxopts .= " -q";
   $xdyopts .= " -q";
}

if ($opt_r)
{
   $mkidxopts .= " -r";
}

if ($opt_c)
{
   $mkidxopts .= " -c";
}

if ($opt_g)
{
   $mkidxopts .= " -g";
}

unless ($opt_p eq "")
{
   $mkidxopts .= " -p $opt_p";
}

unless ($opt_s eq "")
{
   $istfile = $opt_s;
}

# Use xindy if style file ends with .xdy otherwise use makeindex

my $usexindy = $istfile=~m/\.xdy\Z/;

if ($ext ne '')
{
   # an extension has been specified, so only process
   # the specified file

   # v1.6 %thistype is no longer given a default value
   my %thistype;

   my $thislang = "";
   my $thiscodepage = "";

   foreach my $type (keys %exttype)
   {
      if ($exttype{$type}{'in'} eq $ext)
      {
         %thistype = %{$exttype{$type}};

         $thislang = $language{$type};

         $thiscodepage = $codepage{$type};

         last;
      }
   }

   # v1.6 If %thistype hasn't been defined, then the given
   # extension doesn't correspond to any known glossary type

   unless (defined %thistype)
   {
      die "The file extension '$ext' doesn't correspond to any\n",
          "known glossary extension. Try running makeglossaries\n",
          "without an extension, e.g. makeglossaries \"$name\".\n";
   }

   my $outfile;

   if ($opt_o eq "")
   {
      $outfile = "$name.$thistype{out}";
   }
   else
   {
      $outfile = $opt_o;
   }

   my $transcript;

   if ($opt_t eq "")
   {
      $transcript = "$name.$thistype{'log'}";
   }
   else
   {
      $transcript = $opt_t;
   }

   if ($usexindy)
   {
      &xindy("$name.$ext", $outfile, $transcript,$istfile,
        $thislang, $thiscodepage, $xdyopts, $opt_q, $opt_n);
   }
   else
   {
      &makeindex("$name.$ext",$outfile,$transcript,$istfile,
                 $mkidxopts,$opt_q, $opt_n);
   }
}
else
{
   # no file extension specified so process all glossary types

   foreach my $type (keys %exttype)
   {
      my %thistype = %{$exttype{$type}};

      my $inputfile = "$name.$thistype{in}";

      my $outfile;

      if ($opt_o eq "")
      {
         $outfile = "$name.$thistype{out}";
      }
      else
      {
         $outfile = $opt_o;
      }

      # v1.7 print warnings to STDOUT instead of STDERR

      # v1.6 added file existance test
      unless (-e $inputfile)
      {
         print "Warning: File '$inputfile' doesn't exist.\n",
             "*** Skipping glossary '$type'. ***\n";
         next;
      }

      unless (-r $inputfile)
      {
         print "Warning: No read access for '$inputfile' $!\n",
             "*** Skipping glossary '$type'. ***\n";
         next;
      }

      # v1.6 added file empty test
      if (-z $inputfile)
      {
         print "Warning: File '$inputfile' is empty.\n",
             "Have you used any entries defined in glossary '$type'?\n";

         # create an empty output file and move on to the next glossary

         if (open OFD, ">$outfile")
         {
            print OFD "\\null\n";
            close OFD;
         }
         else
         {
            print STDERR "Unable to create '$outfile' $!\n";
         }

         next;
      }

      my $transcript;

      if ($opt_t eq "")
      {
         $transcript = "$name.$thistype{'log'}";
      }
      else
      {
        $transcript = $opt_t;
      }

      if ($usexindy)
      {
         &xindy($inputfile,$outfile,$transcript,$istfile,
                $language{$type},$codepage{$type},
                $xdyopts,$opt_q,$opt_n);
      }
      else
      {
         &makeindex($inputfile,$outfile,$transcript,
                    $istfile,$mkidxopts,$opt_q,$opt_n);
      }
   }
}

sub makeindex{
   my($in,$out,$trans,$ist,$rest,$quiet,$dontexec) = @_;
   my($name,$cmdstr,$buffer,$n,$i,$j);
   my(@stuff,@item);

   $cmdstr = "$rest -s \"$ist\" -t \"$trans\" -o \"$out\" \"$in\"";

   unless ($quiet)
   {
      print "makeindex $cmdstr\n";
   }

   unless ($dontexec)
   {
      open STATUS, "makeindex $cmdstr 2>&1 |"
         or die "Can't fork: $!\n";

      my $status = '';

      while (<STATUS>)
      {
         $status .= $_;
      }

      close STATUS;

      if ($?)
      {
         my $errno = $?;

         if (open LOGFILE, ">>$trans")
         {
            print LOGFILE "\n$status";
            close LOGFILE;
         }
         else
         {
            print STDERR "Unable to open '$trans' $!\n";
         }

         die "Call to makeindex failed (errno=$errno):\n", $status;
      }

      print $status;
   }
}

sub xindy{
   my($in,$out,$trans,$ist,$language,$codepage,$rest,$quiet,
     $dontexec) = @_;
   my($cmdstr, $langparam, $main);
   my($module);

   $module = $ist;
   $module=~s/\.xdy\Z//;

   # map babel names to xindy names
   if ($language eq "frenchb")
   {
      $language = "french";
   }
   elsif ($language=~/^n?germanb?$/)
   {
      $language = "german";
   }
   elsif ($language eq "magyar")
   {
      $language = "hungarian";
   }
   elsif ($language eq "lsorbian")
   {
      $language = "lower-sorbian";
   }
   elsif ($language eq "norsk")
   {
      $language = "norwegian";
   }
   elsif ($language eq "portuges")
   {
      $language = "portuguese";
   }
   elsif ($language eq "russianb")
   {
      $language = "russian";
   }
   elsif ($language eq "slovene")
   {
      $language = "slovenian";
   }
   elsif ($language eq "ukraineb")
   {
      $language = "ukrainian";
   }
   elsif ($language eq "usorbian")
   {
      $language = "upper-sorbian";
   }

   if ($language)
   {
     $langparam = "-L $language";
   }
   else
   {
     $langparam = "";
   }

   # most languages work with xindy's default codepage, but
   # some don't, so if the codepage isn't specific, check
   # the known cases that will generate an error
   # and supply a default. (For all other cases, it's up to the 
   # user to supply a codepage.)

   if ($codepage eq '')
   {
      if ($language eq 'dutch')
      {
         $codepage = "ij-as-ij";
      }
      elsif ($language eq 'german')
      {
         $codepage = "din";
      }
      elsif ($language eq 'gypsy')
      {
         $codepage = "northrussian";
      }
      elsif ($language eq 'hausa')
      {
         $codepage = "utf";
      }
      elsif ($language eq 'klingon')
      {
         $codepage = "utf";
      }
      elsif ($language eq 'latin')
      {
         $codepage = "utf";
      }
      elsif ($language eq 'mongolian')
      {
         $codepage = "cyrillic";
      }
      elsif ($language eq 'slovak')
      {
         $codepage = "small";
      }
      elsif ($language eq 'spanish')
      {
         $codepage = "modern";
      }
      elsif ($language eq 'vietnamese')
      {
         $codepage = "utf";
      }
   }

   my $codepageparam = "";

   if ($codepage)
   {
      $codepageparam = "-C $codepage";
   }

   $main = join(' ',
      "-I xindy",
      "-M \"$module\"",
      "-t \"$trans\"",
      "-o \"$out\"",
      "\"$in\"");

   $cmdstr = join(' ', $rest, $langparam, $codepageparam, $main);

   unless ($quiet)
   {
      print "xindy $cmdstr\n";
   }

   unless ($dontexec)
   {
      open STATUS, "xindy $cmdstr 2>&1 |" or die "Can't fork: $!\n";

      my $status = '';
      my $warnings = "";
      my $retry ="";

      while (<STATUS>)
      {
         $status .= $_;

         $warnings .= $_ if /WARNING:/;
      }

      close STATUS;

      if ($status=~/Cannot locate xindy module for language ([^\s]+) in codepage ([^\s]+)/)
      {
         $cmdstr = join(' ', $rest, $langparam, $main);

         unless ($quiet)
         {
            my $message = "$&\nRetrying using default codepage.\n";

            print STDERR $message;

            $retry .= $message;

            print "xindy $cmdstr\n";
         }

         open STATUS, "xindy $cmdstr 2>&1 |" 
           or die "Can't fork: $!\n";

         $status = '';

         while (<STATUS>)
         {
            $status .= $_;
         }

         close STATUS;
      }

      if ($status=~/Cannot locate xindy module for language ([^\s]+)/
       and $1 ne 'general')
      {
         $cmdstr = join(' ', $rest, "-L general", $main);

         unless ($quiet)
         {
            my $message = "$&\nRetrying with -L general\n";

            print STDERR $message;
            $retry .= $message;

            print "xindy $cmdstr\n";
         }

         open STATUS, "xindy $cmdstr 2>&1 |" 
           or die "Can't fork: $!\n";

         $status = '';

         while (<STATUS>)
         {
            $status .= $_;
         }

         close STATUS;
      }

      if ($?)
      {
         my $errno = $?;

         if (open LOGFILE, ">>$trans")
         {
            print LOGFILE "\n$status";
            close LOGFILE;
         }
         else
         {
            print STDERR "Unable to open '$trans' $!\n";
         }

         if ($language)
         {
            die "Call to xindy failed (errno=$errno):\n", $status;
         }
         else
         {
            # If the language hasn't been set, then it may be
            # because the document doesn't contain
            # \printglossaries/\printglossary or it may be
            # because the user has a customized style file that
            # contains the language settings.

            die "Call to xindy failed (errno=$errno):\n", $status,
             "\n\nNo language detected.",
             "\nHave you remembered to use \\printglossary\n",
             "or \\printglossaries in your document?\n\n";
         }
      }

      print $status;

      if (open LOGFILE, ">>$trans")
      {
         print LOGFILE "\n$warnings";

         if ($retry)
         {
            print LOGFILE "\nmakeglossaries messages:\n\n", $retry;
         }

         close LOGFILE;
      }
      else
      {
         print STDERR "Unable to open '$trans' $!\n";
      }

   }
}

sub HELP_MESSAGE{
   print "\nSyntax : makeglossaries [options] <filename>\n\n";
   print "For use with the glossaries package to pass relevant\n";
   print "files to makeindex or xindy\n\n";
   print "<filename>\tBase name of glossary file(s). This should\n";
   print "\t\tbe the name of your main LaTeX document without any\n";
   print "\t\textension.\n";
   print "\n General Options:\n";
   print "-o <gls>\tUse <gls> as the output file.\n";
   print "-q\t\tQuiet mode\n";
   print "-s <sty>\tEmploy <sty> as the style file\n";
   print "-t <log>\tEmploy <log> as the transcript file\n";

   print "\n Xindy Options:\n";
   print "-L <language>\tUse <language>.\n";

   print "\n Makeindex Options:\n";
   print "-c\t\tCompress intermediate blanks\n";
   print "-g\t\tEmploy German word ordering\n";
   print "-l\t\tLetter ordering\n";   
   print "-p <num>\tSet the starting page number to be <num>\n";
   print "-r\t\tDisable implicit page range formation\n";
   print "\nSee makeindex documentation for further details on these ";
   print "options\n";
}

sub VERSION_MESSAGE{
   print "Makeglossaries Version $version\n";
   print "Copyright (C) 2007 Nicola L C Talbot\n";
   print "This material is subject to the LaTeX Project Public License.\n";
}

1;

=head1 NAME

makeglossaries  - Calls makeindex/xindy for LaTeX documents using glossaries package

=head1 SYNOPSIS

B<makeglossaries> [B<-o> I<file>] [B<-q>] [B<-s> I<file>]
[B<-t> I<file>] [B<-L> I<language>] [B<-c>] [B<-g>] [B<-l>]
[B<-p> I<num>] [B<-r>] [B<--version>] [B<--help>] I<filename>

=head1 DESCRIPTION

B<makeglossaries> is designed for use with LaTeX documents that
use the glossaries package. The mandatory argument I<filename> should
be the name of the LaTeX document without the .tex extension. 
B<makeglossaries> will read the auxiliary file to determine whether
B<makeindex> or B<xindy> should be called. All the information
required to be passed to the relevant indexing application should
also be contained in the auxiliary file, but may be overridden by
the option arguments to B<makeglossaries>.

=head1 OPTIONS

=over 4

=item B<-q>

Quiet mode. Reduces chatter to standard output.

=item B<-o> I<file>

Use I<file> as the output file. (Only suitable for documents 
containing a single glossary, otherwise each glossary will be
overridden.)

=item B<-s> I<file>

Use I<file> as the style file. Note that if you use this option,
you need to know whether B<makeindex> or B<xindy> will be called, as
they have different style files.

=item B<-t> I<file>

Use I<file> as the transcript file.

=item B<-L> I<language>

This option only has an effect if B<xindy> is called. Sets the
language. See B<xindy> documentation for further details.

=item B<-c>

Compress intermediate blanks (B<makeindex> only).

=item B<-g>

Employ German word ordering (B<makeindex> only).

=item B<-l>

Letter ordering (B<makeindex> only).

=item B<-p> I<num>

Sets the starting page number to be I<num> (B<makeindex> only).

=item B<-r>

Disable implicit page range formation (B<makeindex> only).

=item B<--version>

Prints version number and exits.

=item B<--help>

Prints help message and exits.

=back

=head1 REQUIRES

Perl, Getopt::Std, and makeindex or xindy (depending on glossaries
package options).

=head1 LICENSE

This is free software distributed under the LaTeX Project Public 
License. There is NO WARRANTY.
See L<http://www.latex-project.org/lppl.txt> for details.

=head1 AUTHOR

Nicola L. C. Talbot,
L<http://theoval.cmp.uea.ac.uk/~nlct/>

=head1 RECOMMENDED READING

The glossaries manual:

	texdoc glossaries

=cut
