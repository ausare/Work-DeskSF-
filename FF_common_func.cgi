#!/Users/scripting/perl5/perlbrew/perls/perl-5.24.0/bin/Perl
##########################################
#
#	by Larry Gonyea
#      TMS
#   Common functions used by many scripts for the Features Editor Site.
#
#############################
#use lib "/opt/local/lib/perl5/site_perl/5.8.9";
#use lib "/Users/scripting/perl5/perlbrew/perls/perl-5.22.0/lib/5.22.0";
use Time::Local;
use Net::FTP;
use Mail::Send;
use MIME::Lite;
use Tie::File;
use Text::Wrapper;
use XML::LibXML;
use utf8;
use File::Copy;
#use encoding 'UTF-8';
#use lib '/Users/scripting/perl5/perlbrew/perls/perl-5.22.0/lib/site_perl/5.22.0';
#use Image::ExifTool;
require("FF_web_elements.cgi");

my $scriptloginID = "scripting";
my $scriptloginPWD = "alaska";
my $pathUNIX;
my $baseFEfolder = "/Library/WebServer/CGI-Executables/FE2";
my $FeatFolder = "/Library/WebServer/FF2";
my $PhotoDir = "/Library/WebServer/Documents/Images/";

my ($ThisIP,$systemType) = getHomeAddress();

#Called to get the base directories to Features and Feature scripts.
sub getFilesLocal {
my $CGIscriptslocal = "/Library/WebServer/CGI-Executables/FE2";
my $FeatureFilesLocal = "/Library/WebServer/FF2";
return($CGIscriptslocal,$FeatureFilesLocal)
}

##Dictate what Special Features are live. We can have more than one live. Each Special section should be separated by a comma.
sub getSpecialsInfo {
my $currentSpecial = "Halloween 2016";
return($currentSpecial);
}

#Determines home machine web browser address. $ThisIP should be change to change all other scripts to direct links correctly.
## $systemOn dictates how scripts react to certain steps. Development is used to prevent filtering to live. Live is used to make everything work in a live environment.
sub getHomeAddress {
#For Pagserver:
#my $ThisIP = "http://163.193.245.179:81";
#my $systemOn = "Live";
#New Development machine
#my $ThisIP = "163.194.106.173";
#my $systemOn = "Development";
#my $systemOn = "Live";
#For PagserverR:
my $ThisIP = "featuremanager.tmsgf.trb";
my $systemOn = "Live";

return($ThisIP,$systemOn);
}

# basic logic that creates a array. every line in a file becomes a list item. Filters out blank lines.
sub arrayFile {
## Need one param. Full file path
## This filters out blank lines.
my @fileArray;
my $thisFile = $_[0];
open FH,"<$thisFile";
my @fileSplit = <FH>;
close FH;
		foreach my $line (@fileSplit) {
		if ($line ne "") {
			chomp($line);
			push (@fileArray,$line);
		}
		}
return(@fileArray);
}


sub checkFileforText {
## this routine checks a file for a line of text. this is not case sensitive. Returns a TRUE or FALSE value.
## text must match the entire line.
## param 1: text to match
## param 2: file to check.

my $SearchText = lc($_[0]);
my $filetoCheck = $_[1];
my $ReturnVal = "FALSE";
## list live features here. Any other features will be marked as TEST on return.
my @lineArray = arrayFile("$filetoCheck");
foreach my $thisLine (@lineArray) {
	$thisLine = lc($thisLine);
	if ($thisLine eq $SearchText) {
		$ReturnVal = "TRUE";
	}
return($ReturnVal);
}


}

### Not currently used ###
# Used to create list of writers to be used through site.
sub getWriters {
my @writerlist = ("Jay Bobbin", "George Dickie", "John Crook",  "Taylor Michaels", "Michael Korb");
return(@writerlist);
}

### Not Currently used ###
# make a dropdown list of writers from the getWriters subroutine.
sub makeWriterDropdown {
my $defWriter = $_[0];
my @writerlist = getWriters();
my $optionslist = "";
		foreach my $writer (@writerlist) {
			if ($writer eq $defWriter) {
				$optionslist = ("$optionslist<option value=\"$writer\" selected>$writer</option>\n");
			} else {
				$optionslist = ("$optionslist<option value=\"$writer\">$writer</option>\n");
			}
		}
return($optionslist);
}

### Not Currently used ###
# create a list of copyright options.
sub getcopywrights {
my @copywrites = ("Zap2It,Gracenote");
return(@copywrites);
}

# create a list of steps features can be in.
sub getstatelist {
my @steplist = ("In Progress","Copy Edit","Final Read","Filtered");
return(@steplist);
}

#makes the drop down list of steps features can be in.
sub makeStateDropdown {
my $currentStat = $_[0];
my @statelist = getstatelist();
my $optionslist = "";
		foreach my $states (@statelist) {
			my $choiceList = $states;
			if ($choiceList eq "Filtered") {
				$choiceList = "Filter";
			}
			if ($states eq $currentStat) {
				$optionslist = ("$optionslist<option value=\"$states\" selected>$choiceList</option>\n");
			} else {
				$optionslist = ("$optionslist<option value=\"$states\">$choiceList</option>\n");
			}
		}
return($optionslist);
}

#Make a radio button list of steps a feature can be in. This list is used in the Editor to submit what step the feature will move to.
sub makeStateRadio {
my $currentStat = $_[0];
my @statelist = getstatelist();
my $optionslist = "";
		foreach my $states (@statelist) {
			my $choiceList = $states;
			if ($choiceList eq "Filtered") {
				$choiceList = "Filter";
			}
			if (($currentStat eq "new") || ($currentStat eq "autoGen")) {
				$currentStat = "In Progress";
			}

			if ($states eq $currentStat) {
				$optionslist = ("$optionslist<div class=SidebarRadio><input type=\"radio\" form=\"Mover\" name=\"newstate\" value=\"$states\" checked>$states</div>");
			} else {
				$optionslist = ("$optionslist<div class=SidebarRadio><input type=\"radio\" form=\"Mover\" name=\"newstate\" value=\"$states\">$states<br></div>");
			}
		}
return($optionslist);
}

# Opens the TMP file from the templates folder and returns the list of field names. (The first field in the | seperated line)
sub getTmpNameList {
my @returnlist;
my $tmpfile = $_[0];
open TH,"<",$tmpfile or die $!;
my @fieldlists = <TH>;
close TH;
	foreach $line (@fieldlists) {
		if ($line ne "") {
			@splitList = split('\|',$line);
			my $colToAdd = $splitList[0];
			push (@returnlist,$colToAdd);
		}
	}
return(@returnlist);
}


#split multiple paragraphs so that we get correct quote replacements.
#If a new paragraph continues a quote, the previous paragraph has no closing quotes, but the next paragraph requires opening quotes.
# The order of the search and replace is very important so that we are converting the correct quotes at the correct time.

sub convertQuotes {
	my $returnText = "";
	my $tmpline = $_[0];
	my $problems;
		my @allrecords = split('\<\/p\>',$tmpline);
		foreach my $paraGraph (@allrecords) { #switch every other html " (&quot;) with the `` or ''
			utf8::decode($paraGraph);
			$paraGraph =~ s/\&lsquo;\&lsquo;/\"/g;
			$paraGraph =~ s/\&rsquo;\&rsquo;/\"/g;
			$paraGraph =~ s/\&ldquo;/\"/g;
			$paraGraph =~ s/\&rdquo;/\"/g;
			$paraGraph =~ s/\&quot;/\"/g;
			$paraGraph =~ s/\&#39;/\'/g;
			#$paraGraph =~ s/\’/\'/g;			
			#$paraGraph =~ s/\x{201C}/\"/g;			
			#$paraGraph =~ s/\x{201D}/\"/g;			
## Search for titles in single quotes and change the opening single quote into a back tick.
			$paraGraph =~ s/\<p>//g;
			while ($paraGraph =~ m/ \'\w/g) { #as long as there's a html quote replace them.
 		 		$paraGraph =~ s/ \'/ \`/;
			}
			# Used for headlines that begin with a title. Turn first single quote to a back tick
			if ($paraGraph =~ m/^\'\w/) {
			 	$paraGraph =~ s/\'/\`/;
			}
			# Used for titles in single quotes within double quotes
			if ($paraGraph =~ m/\(\'\w/) {
			 	$paraGraph =~ s/\(\'/\(\`/;
			}
			while ($paraGraph =~ m/\"/g) { #as long as there's a html quote replace them.
 		 		$paraGraph =~ s/\"/``/;
 		 		$paraGraph =~ s/\"/\'\'/;
			}			$returnText = "$returnText<p>$paraGraph</p>\n";
		}

			my @quotesNumber = ($returnText =~ /\"/g);
			my $count = @quotesNumber;
			if ($count % 2 == 1) {
			 my $problems = "$problems\nPossible missing double quote.";
			}


	return($returnText);
} #end sub convertQuotes

# Gets specific exif data from a photo and returns it.
sub getPhotoExif {
my $photoInfo = $_[0];
use Image::ExifTool;
my $exifTool = new Image::ExifTool;
###  Use for directories of files when needed
#	opendir(TMPDIR, $photoDir);
#	my @photoList = readdir TMPDIR;
#	closedir(TMPDIR);
#	foreach (@photoList) {
#	if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
#		next;
#	} else {
#	}
	my $info = $exifTool->ImageInfo("$photoInfo");
		my $name_value = $exifTool->GetValue('FileName');
		my $caption_value = $exifTool->GetValue('Caption-Abstract');
		my $res_value = $exifTool->GetValue('XResolution');
		my $dimensions_value = $exifTool->GetValue('ImageSize');
		my $colorMode = $exifTool->GetValue('ColorMode');
#name,caption,resolution,dimensions,colormode
return($name_value,$caption_value,$res_value,$dimensions_value,$colorMode);
}

# Not currently used by any scripts. Could prove to be helpful in the future.
sub convertQuotesToHTML {
	my $returnText = "";
	my $tmpline = $_[0];
	my $problems;
		my @allrecords = split('\<\/p\>',$tmpline);
			while ($tmpline =~ m/ \``\w/g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/ \`\`/ \&ldquo;/;
			}
			while ($tmpline =~ m/ \"\w /g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/ \"/ \&ldquo;/;
			}
			while ($tmpline =~ m/ &quot;\w/g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/ &quot;/ \&ldquo;/;
			}
			while ($tmpline =~ m/\w\" /g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/\" / \&rdquo;/;
			}
			while ($tmpline =~ m/&quot; /g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/&quot; / \&rdquo; /;
			}
			while ($tmpline =~ m/ \`\w/g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/ \`/ \&lsquo;/;
			}
			while ($tmpline =~ m/\w\' /g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/\' / \&rsquo;/;
			}
			while ($tmpline =~ m/\w\&#39;s /g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/\'/\&rsquo;/;
			}
			while ($tmpline =~ m/\w\&#39;d /g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/\'/\&rsquo;/;
			}
			while ($tmpline =~ m/\w\'s /g) { #as long as there's a html quote replace them.
 		 		$tmpline =~ s/\'/\&rsquo;/;
			}


	return($tmpline);
} #end sub convertQuotes

# converts known html markup found in text and ckeditor fields and converts them to the Merl Markup equivalant.
# ckeditor fields will be in html coding for special characters
# text fields will be in utf-8
# if the markup is unnecessary, it removes it.
# It replaces the closing </p> with a </p>|| so that we can easily separate paragraphs later on.

sub	htmltomerlMarkup {
	my $tmpline = $_[0];
	my $qswitch = "start";
	#utf8::encode($tmpline);
	my %htmlTOmerl = (
	"\<strong\>" => "\<1\>",
	"\<\/strong\>" => "\<2\>",
	"\&lsquo;" => "\`",
	"\&shy;" => "",
	"ʻ" => "\`",
	"‘" => "\`",
	"\&quot;" => "\"",
	"\&ldquo;" => "\"",
	"“" => "``",
	"\&rsquo;" => "\'",
	"’" => "\'",
	"\&rdquo;" => "\"",
	"”" => "''",
	"\&amp;" => "\&",
	"\&nbsp;" => " ",
	"\&iexcl;" => "\"!",
	"¡" => "\"!",
	"£" => "\"~~L",
	"\&pound;" => "\"~~L",
	"\&copy;" => "\<9\>",
	"©" => "\<9\>",
	"¿" => "\"?",
	"\&iquest;" => "\"?",
	"\&Agrave;" => "\"`A",
	"À" => "\"`A",
	"\&Aacute;" => "\"'A",
	"Á" => "\"'A",
	"\&Acirc;" => "\"^A",
	"Â" => "\"^A",
	"\&Atilde;" => "\"~~A",
	"Ã" => "\"~~A",
	"\&Auml;" => "\":A",
	"Ä" => "\":A",
	"\&Aring;" => "",
	"Å" => "",
	"\&AElig;" => "\"'A",
	"Æ" => "\"'A",
	"\&Ccedil;" => "\",C",
	"Ç" => "\",C",
	"\&Egrave;" => "\"`E",
	"È" => "\"`E",
	"\&Eacute;" => "\"'E",
	"É" => "\"'E",
	"\&Ecirc;" => "\"^E",
	"Ê" => "\"^E",
	"\&Egrave;" => "\"`E",
	"È" => "\"`E",
	"\&Euml;" => "\":E",
	"Ë" => "\":E",
	"\&Igrave;" => "\"`I",
	"Ì" => "\"`I",
	"\&Iacute;" => "\"'I",
	"Í" => "\"'I",
	"\&Icirc;" => "\"^I",
	"Î" => "\"^I",
	"\&Iuml;" => "\":I",
	"Ï" => "\":I",
	"\&Ntilde;" => "\"~~N",
	"Ñ" => "\"~~N",
	"\&Ograve;" => "\"`O",
	"Ò" => "\"`O",
	"\&Oacute;" => "\"'O",
	"Ó" => "\"'O",
	"\&Ocirc;" => "\"^O",
	"Ô" => "\"^O",
	"\&Ouml;" => "\":O",
	"Ö" => "\":O",
	"\&Ugrave;" => "\"`U",
	"Ù" => "\"`U",
	"\&Uacute;" => "\"'U",
	"Ú" => "\"'U",
	"\&Ugrave;" => "\"`U",
	"Ù" => "\"`U",
	"\&Ucirc;" => "\"^U",
	"Û" => "\"^U",
	"\&Uuml;" => "\":U",
	"Ü" => "\":U",
	"\&Yacute;" => "\":Y",
	"Ý" => "\":Y",
	"\&agrave;" => "\"`a",
	"à" => "\"`a",
	"\&aacute;" => "\"'a",
	"á" => "\"'a",
	"\&acirc;" => "\"^a",
	"â" => "\"^a",
	"\&atilde;" => "\"~~a",
	"ã" => "\"~~a",
	"\&auml;" => "\":a",
	"ä" => "\":a",
	"\&ccedil;" => "\",c",
	"ç" => "\",c",
	"\&egrave;" => "\"`e",
	"è" => "\"`e",
	"\&eacute;" => "\"'e",
	"é" => "\"'e",
	"\&ecirc;" => "\"^e",
	"ê" => "\"^e",
	"\&euml;" => "\":e",
	"ë" => "\":e",
	"\&igrave;" => "\"`i",
	"ì" => "\"`i",
	"\&iacute;" => "\"'i",
	"í" => "\"'i",
	"\&icirc;" => "\"^i",
	"î" => "\"^i",
	"\&iuml;" => "\":i",
	"ï" => "\":i",
	"\&ntilde;" => "\"~~n",
	"ñ" => "\"~~n",
	"\&ograve;" => "\"`o",
	"ò" => "\"`o",
	"\&oacute;" => "\"'o",
	"ó" => "\"'o",
	"\&ocirc;" => "\"^o",
	"ô" => "\"^o",
	"\&otilde;" => "\"~~o",
	"õ" => "\"~~o",
	"\&ouml;" => "\":o",
	"ö" => "\":o",
	"\&ugrave;" => "\"`u",
	"ù" => "\"`u",
	"\&uacute;" => "\"'u",
	"ú" => "\"'u",
	"\&ucirc;" => "\"^u",
	"û" => "\"^u",
	"\&uuml;" => "\":u",
	"ü" => "\":u",
	"\&yacute;" => "\"'y",
	"ý" => "\"'y",
	"\&yuml;" => "\":y",
	"ÿ" => "\":y",
	"\&ndash;" => "--",
	"\<em\>" => "\<7\>",
	"\</em\>" => "\<8\>",
	"&bull;" => "\<10\>",
	"•" => "\<10\>",
	"&reg;" => "\<13\>",
	"®" => "\<13\>",
	"\&#39;" => "\'",
	"\ʼ" => "\'",
	"\&hellip;" => "\.\.\.",
	"\…" => "\.\.\.",
	#"\&mdash;" => "\-\-",
	"\&mdash;" => "--",
	"\–" => "--",
	"\—" => "--",
	"\<span style=\"(.*)\"\>" => "",
	"\<span style=``(.*)\'\'\>" => "",
	"\<strong style=\"(.*)\"\>" => "",
	"\<p style=``(.*)right(.*)''\>" => "",
	"\<p style=``(.*)justify(.*)''\>" => "",
	"\<\/span\>" => "",
# other substitutions not relating to text formatting
	# replaces trademark symbol with splat.
	"Celebrity Scoop" => "Celebrity Scoop\*",
	"Sports Stumpers" => "Sports Stumpers\*",
	);
	while ( my ($key, $value) = each %htmlTOmerl ) {
		$tmpline =~ s/$key/$value/g;
	}

	while ($tmpline =~ m/\<p style=``(.*)center(.*)''\>/g) {
			$tmpline =~ s/\<p style=``(.*)center(.*)''\>/<3>/;
			#$tmpline =~ s/\<\/p\>/\<\/p>\<4>/;
			$tmpline =~ s/\<\/p\>\s/<4>\<\/p\>/;
	}

	if ($tmpline =~ m/\<p\>/g) {
		$tmpline =~ s/\<p>//g;
		$tmpline =~ s/\<\/p\>\s+/||/g;
		$tmpline =~ s/\<\/p\>//g;
	}
		$tmpline =~ s/#/\<11\>/g;
		$tmpline =~ s/[^[:ascii:]]//g;
return($tmpline);
}

#  This is used to search and replace text based on a filter file.
#  the filter files should contain the search for and replace with a pipe (|) between.
#  Each search/replace should be on a separate line.
sub runFilter {
my $useFilter = $_[0];
my $tmpline = $_[1];
#print "Filter is $useFilter\n";
if ($useFilter eq "cpstyle") {
	my $thisFilter = "/Library/WebServer/CGI-Executables/FE2/filters/cpconvert.txt";
	#print "Using filter $thisFilter\n";
}
my %filterList = hashAFile($thisFilter);
my $hashCount = scalar(keys %filterList);
#print "Key count is $hashCount\n";
while ( my ($key, $value) = each %filterList ) {
	print "switching $key to $value\n";
	$tmpline =~ s/$key/$value/g;
}
return($tmpline);

}
## convertToCPStyle not used at this time. Converting it to funFilter for a generic self maintained fileter system
sub convertToCPStyle {
	#my %cpconvert = hashAfile();
	my $tmpline = $_[0];
	my %goToCPStyle = (
	"neighbor" => "neighbour",
	"favor" => "favour",
	"favorite" => "favourite",
	"savor" => "savour",
	"rumor" => "rumour",
	"humor" => "humour",
	"centre" => "center",
	"kilometer" => "kilometre",
	"paycheck" => "paychecque",
	"defense" => "defence",
	"license" => "licence",
	"labor" => "labour",
	"entree" => "entrée",
	"Entree" => "Entrée",
	"fiance" => "fiancé",
	"Fiance" => "Fiancé",
	"Beyonce" => "Beyoncé",
	"Michael Buble" => "Michael Bublé",
	"Tea Leoni" => "Téa Leoni",
	"World War II" => "Second World War",
	"World War I" => "First World War",	);
	while ( my ($key, $value) = each %goToCPStyle ) {
	$tmpline =~ s/$key/$value/g;
	}
return($tmpline);

}

# sub routine to take merl markup found in the template an convert it to HTMl for the
#   preview screen when the feature is displayed on the web page after saving.
sub getMerltoHtmlMark {
my @returnlist;
my $markup = "";
my $markdown = "";
my $tmpfile = $_[0];
my $fieldname = $_[1];
open TH,"<",$tmpfile or die $!;
my @fieldlists = <TH>;
close TH;
	foreach $line (@fieldlists) {
			@splitList = split('\|',$line);
			my $namefield = $splitList[0];
			my $markupfield = $splitList[2];
			#print "Name: $namefield compared to $fieldname\n";
			if ($namefield eq $fieldname) {
				if ($markupfield =~ m/\<1\>/) { #check for bold
					$markup = "$markup<b>";
				}
				if ($markupfield =~ m/\<3\>/) {
					$markup = "$markup<center>";
					$markdown = "$markdown</center>";
				}
				if ($markupfield =~ m/\<5\>/) {
					$markup = "$markup<italic>";
					$markdown = "$markdown</italic>";
				}
				if ($markupfield =~ m/\<9\>/) {
					$markup = "$markup&#169;";
				}
				if ($markupfield =~ m/\<2\>/) {
					$markup = "$markup</b>";
				}
				if ($markupfield =~ m/\<4\>/) {
					$markup = "$markup</center>";
				}
				if ($markupfield =~ m/\<6\>/) {
					$markup = "$markup</italic>";
				}
				if ($markupfield =~ m/\<7\>/) {
					$markup = "$markup<b><italic>";
				}
				if ($markupfield =~ m/\<8\>/) {
					$markup = "$markup</b></italic>";
				}
				 #print "$namefield matches $fieldname correct markup is $markupfield\n";
				$colToAdd = $markupfield;
			}
		}
return($markup);
}
# returns the Merl markup value found in the TMP file based on the given fieldname field.
sub getTmpColValue {
my @returnlist;
my $colToAdd = "";
my $tmpfile = $_[0];
my $fieldname = $_[1];
open TH,"<",$tmpfile or die $!;
my @fieldlists = <TH>;
close TH;
	foreach $line (@fieldlists) {
			@splitList = split('\|',$line);
			my $namefield = $splitList[0];
			my $markupfield = $splitList[2];
			if ($namefield eq $fieldname) {
				$colToAdd = $markupfield;
			}
		}
return($colToAdd);
}

# Returns the list of all values in a TMP file based on the fieldname given to the subroutine.
sub getTMPLinevalues {
# gets an array of the values from feature template file.
# requires 2 arguments full tmp file path and field name
# returns all values from the line matching the field name in an array. Array values listed
# [0] = field name
# [1] = text field type
# [2] = merlmarkup
# [3] = default text
# [4] = optional field marker indicated by "Opt"
my @returnlist;
my $colToAdd = "";
my $tmpfile = $_[0];
my $fieldname = $_[1];
open TH,"<",$tmpfile or die $!;
my @fieldlists = <TH>;
close TH;
	foreach $line (@fieldlists) {
			@splitList = split('\|',$line);
			my $namefield = $splitList[0];
			if ($namefield eq $fieldname) {
				@returnlist = @splitList;
			}
		}
return(@returnlist);
}

### Not currently used ###
sub fieldValidator {
# requires arguments: ("warn or fail","text to validate", "default text value from template", "optional field from template"
my $valError = "False";
my $WarnFound = 0;
my $ErrFound = 0;
my $valText = $_[0];
chomp($defText);
chomp($optField);
chomp($valText);
return($valError);
}

### should be using the .spc files now for live/test determination.
## this routine should change to get hash and value for a feature.
sub checkFeatForTest {
	my $storyCall = $_[0];
	my $liveList = "$baseFEfolder/liveFeatList.txt";
	my $FeatStatus = checkFileforText($storyCall,$liveList);
	if ($FeatStatus eq "TRUE") {
		$FeatStatus = "LIVE";
	} else {
		$FeatStatus = "TEST";
	}
return($FeatStatus);
}

sub showSpecialFeats { #usage showfeatureheader
my ($look,$feel,$specialName) = @_;

#my @featureslist = getSpecialStarted($specialName);
my $CardStep;
my ($week1,$week2,$week3,$week4,$week5,$week6,$week7) = getweeks();
my @allbaseweeks = ($week1,$week2,$week3,$week4,$week5,$week6,$week7);
#my @allbaseweeks = ($week2,$week3,$week4,$week5);
my $baseFolder = "$FeatFolder/$specialName";
my @stepoptions = getstatelist();
my $STvalue;
my %steptovalue;
#my @featureslist = getFeatStarted();
my $weekNumbers = @allbaseweeks;
############## Optional information based upon the input of filters
#	showFeatmanoptions("search",$mysearch);
#	showFeatmanoptions("step",$step);
#	showFeatmanoptions("week",$weekof);
#	showFeatmanoptions("all","all");
#	$progStatus = "Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>";
my @valuesteps = ("In Progress","Copy Edit","Final Read","Filtered");
foreach $hashStep (@valuesteps) {
	$STvalue++;
	$steptovalue{$hashStep} = $STvalue;
}
my $maxValue = $STvalue;


if ($look eq 'all') {
	my @featureslist = getSpecialStarted($specialName);
	#print "Features started for $specialName are \n @featureslist\n";
	my $sWeek = $specialName;
#	foreach my $sWeek (@allbaseweeks) {
#		foreach my $steps (@stepoptions) {
			ClosedDIV("class","CardCatHead","Features $sWeek");
			#### Get all the features not started and have available to show if requested
					my @deadlines = getSpecialsNS($specialName);
					#print "Deadlines are <br> @deadlines";
					foreach $thisdl (@deadlines) {
						#print "$thisdl<br>";
						my @deadlineparts = split('\|',$thisdl);
						my $dlStatus = $deadlineparts[0];
						my $dlName = $deadlineparts[1];
						my $dlDay = $deadlineparts[2];
						my $dlTime = $deadlineparts[3];
						my $dlState = $deadlineparts[4];
						my $lLink = $deadlineparts[5];
						my $file_time = $deadlineparts[6];
						my @getTMPname = split('\.',$dlName);
						my $tmp = "$baseFEfolder/templates $specialName/${getTMPname[0]}.tmp";
						my @StatusParts = split(' - ',$dlStatus);
						if ($dlStatus eq "Not Started") {
								$progStatus = "Not Started";
								$valStat = "0";
								$NotStartTally++;
								$divHead = "DLHeadNS";
					#		if ($dlDay eq "Today") {
					#			$col1Info = "<b>$dlName</b> <hr>Due: ${dlDay} at $dlTime";
					#		} else {
					#			$col1Info = "<b>$dlName</b> <hr>Due: ${dlDay}s at $dlTime";
					#		}
							$actionButton = "<form method=\"get\" action=\"http://$ThisIP/cgi-bin/FE2/specials_editor.cgi\"><input type=\"hidden\" name=\"specialName\" value=\"$specialName\"><input type=\"hidden\" name=\"story\" value=\"$dlName\"><input type=\"hidden\" name=\"status\" value=\"new\"><input type=\"submit\" value=\"Start $dlName\"></form>\n";
							#@notStartedCol = (@notStartedCol,"$progStatus|$valStat|$divHead|$col1Info|$actionButton");
							OpenDIV("class","ContentCardNS");
							ClosedDIV("class","ContentCardHead","$dlName");
							ClosedDIV("class","ContentCardBody","Not Started<br><progress value=\"0\"max =\"5\">Step 0 of 5</progress>");
							ClosedDIV("class","ContentCardFooter","$actionButton");
							EndDIV();
						}
					}
			#### END     Get all the features not started and have available to show if requested
			my $count = 0;
			foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				if ($lFile ne "") {
					my @filesplit = split(/\./,$lFile);
					my $nametmp = $filesplit[0];
					my $tmp = "./templates $specialName/${nametmp}.tmp";
					my $spc = "./specs $specialName/${nametmp}.spc";
					my %FeatSpecs = hashAFile($spc);
					$count++;
					my $FeatStatus = $FeatSpecs{'status'};
					#checkFeatForTest($nametmp);
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
						$CardStep = "Complete!";
						OpenDIV("class","ContentCardComplete");
					} else {
						$CardStep = $lStep;
						OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","$lFile","($FeatStatus) $thisWriter Last Modified: $file_time");
					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					ClosedDIV("class","ContentCardFooter","<form method=\"get\" action=\"http://$ThisIP/cgi-bin/FE2/specials_editor.cgi\"><input type=\"hidden\" name=\"specialName\" value=\"$specialName\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();
				} #end remove empty
			}#end @featureslist
				#}
#		}#end @stepoptions
				#if ($count == 0) {
				#	ClosedDIV("class","ContentInfo","No features found for the week of $sWeek");
				#}
	$weekNumbers--;
#	} #end @allbaseweeks
			#ClosedDIV("class","CardCatHead","$count Features found for week of $sWeek");

} #end default value

if ($look eq 'search')  {
	my @featureslist = getFeatStarted();
	#foreach my $sWeek (@allbaseweeks) {
	#ClosedDIV("class","ContentBoxHead","Feature week of $sWeek");
			#foreach my $featline (@featureslist) {
			#print "$featline\n<br>";
			#}
			ClosedDIV("class","ContentBoxPlain","Search results for text - $feel");
		foreach my $sWeek (@allbaseweeks) {
					 my $count = 0;
			ClosedDIV("class","CardCatHead","Results for the week of $sWeek");
		foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				if (($lFile ne "") && ($sWeek eq $lWeek)) {
				#print "File location: $lLink \n<br>";
					use Tie::File;
					tie my @records, 'Tie::File', $lLink;
					my $all_lines = join "\n",@records;
					#			print "$lFile - \n<br> $all_lines\n<br>";
					untie @records;
					my $uc_all_lines = uc($all_lines);
					#			print "$lFile - \n<br> $uc_all_lines\n<br>";
					my $uc_feel = uc($feel);
					# print "searching for $uc_feel\n";
					if ($uc_all_lines =~ m/$uc_feel/) {
						$count++;
						my $thisWriter = findAuthor($lLink);
						if ($lStep eq "Filtered") {
						$CardStep = "Complete!";
						OpenDIV("class","ContentCardComplete");
						} else {
						$CardStep = $lStep;
						OpenDIV("class","ContentCard");
						}
						ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

						ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
						ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
						EndDIV();
					} #end search for matching text
			}#end @featureslist
				} #end if (($lFile ne "") && ($sWeek eq $lWeek))
					if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<p>No features match for this week.</p>");
					}
				} #end @allbaseweeks

} #end text search

if ($look eq 'feature')  {
	my @featureslist = getFeatStarted();
	my $count = 0;
			foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				my @featname = split ('\.',$lFile);
				if ($featname[0] =~ m/$feel/i) {
					$count++;
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();
					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","<b>$lStep</b> <br> Last modified: <b>$file_time</b> <br>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist
					if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<h2><center>No features found.<c/enter></h2>");
					}
} #end text search

### Step search
#########################
if ($look eq 'step')  {

	my @featureslist = getFeatStarted();
			foreach my $feat (@featureslist) {
				#ClosedDIV("class","ContentBoxFull","Checking $feel for MMMM $feat MMMM");
				#print "</div>";
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				my @fileSplits = split('\.',$lFile);
				my $templateUSe = "$fileSplits[0].tmp";
				my $tmp = "./templates/$templateUSe";
				if ($lStep eq $feel) {
					$count++;
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();

					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","<b>$lStep</b> <br> Last modified: <b>$file_time</b><br>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist
					if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<h2><center>No features found.</center></h2>");
					}

} #end step search

if ($look eq 'stepweek')  {

my ($thisstep,$thisweek) = split ('\|',$feel);

	my @featureslist = getFeatStarted();
			foreach my $feat (@featureslist) {
				#ClosedDIV("class","ContentBoxFull","Checking $feel for MMMM $feat MMMM");
				#print "</div>";
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				if (($lStep eq $thisstep) && ($lWeek eq $thisweek)) {
					$count++;
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();

					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","<b>$lStep</b> <br> Last modified: <b>$file_time</b><br>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist
					if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<h2><center>No features found.</center></h2>");
					}

} #end step search

### week search
#########################

if ($look eq 'weekof') {
	my @featureslist = getFeatStarted();
	#ClosedDIV("class","ContentBoxHead","Features week of $feel");
#=begin test
					my $weekNumbers;
					#my ($week1,$week2,$week3,$week4,$week5,$week6) = getweeks();
					my @allWeeks = getweeks();
					my $weekcounter = 5;
					foreach (@allWeeks) {
						if ($_ eq $feel) {
							$weekNumbers = $weekcounter;
							#print "Week is $_<br> Counter is at $weekNumbers<br>";
						} else {
							$weekcounter--;
						}
					}
					my @deadlines = getFeatNS($weekNumbers);
					foreach $thisdl (@deadlines) {
					#print "$thisdl<br>";
						my @deadlineparts = split('\|',$thisdl);
						my $dlStatus = $deadlineparts[0];
						my $dlName = $deadlineparts[1];
						my $dlDay = $deadlineparts[2];
						my $dlTime = $deadlineparts[3];
						my $dlState = $deadlineparts[4];
						my $lLink = $deadlineparts[5];
						my $file_time = $deadlineparts[6];
						my @getTMPname = split('\.',$dlName);
						my $tmp = "./templates/${getTMPname[0]}.tmp";
						my @StatusParts = split(' - ',$dlStatus);
						if ($dlStatus eq "Not Started") {
								$progStatus = "Not Started";
								$valStat = "0";
								$NotStartTally++;
								$divHead = "DLHeadNS";
							if ($dlDay eq "Today") {
								$col1Info = "<b>$dlName</b> <hr>Due: ${dlDay} at $dlTime";
							} else {
								$col1Info = "<b>$dlName</b> <hr>Due: ${dlDay}s at $dlTime";
							}
							$actionButton = "<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"story\" value=\"$dlName\"><input type=\"hidden\" name=\"status\" value=\"new\"><input type=\"submit\" value=\"Start $dlName\"></form>\n";
							#@notStartedCol = (@notStartedCol,"$progStatus|$valStat|$divHead|$col1Info|$actionButton");
							OpenDIV("class","ContentCardNS");
							ClosedDIV("class","ContentCardHead","$dlName");
							ClosedDIV("class","ContentCardBody","Not Started");
							ClosedDIV("class","ContentCardFooter","$actionButton");
							EndDIV();
						}
					}

#=cut section
#		foreach my $steps (@stepoptions) {
			foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
#				if (($lStep eq $steps) && ($lWeek == $feel)) {
				if (($lWeek eq $feel) && ($feat ne "")) {
					$count++;
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();

					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","$lStep last modified $file_time <br>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist

#		} #end @stepoptions
				#if ($count == 0){
				#	ClosedDIV("class","ContentBoxFull","<h2><center>No features found.</center></h2>");
				#}

} #end week value

if ($look eq 'writer') {
	my @featureslist = getFeatStarted();
		foreach my $steps (@stepoptions) {
			foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
					$count++;
					my $thisWriter = findAuthor($lLink);
				if (($lStep eq $steps) && ($thisWriter =~ /$feel/)) {

					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");
					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();

					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","<b>$lStep</b> <br> Last modified: <b>$file_time</b>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist
		} #end @writeroptions
			if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<h2><center>No features found.</center></h2>");
			}

} #end week value

}#End Sub

### This routine is used to show a list of features on the Featureman main web page based on 2 parameters.
## parameter 1 should be the type of filter. This defaults to all but can currently filer step, week, feature name, etc
### parameter 2 narrows down parameter 1 more by showing only matching features based on both parameter 1 & 2 together.
### for example showFeatmanoptions(step,in progress) will show all feature in the step of in progress.
sub getSpecialsNS {
			my $special_name = $_[0];
			my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
			my @daysOfWeek = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
			my $todayDay = $daysOfWeek[$f_weekDay];
			my @deadlineList;
			my @featlist;
			#my $weeksToAdjust = $_[0];
			#if ($weeksToAdjust eq '') {$weeksToAdjust = 0;}
			my $dlcheckfolder = "$baseFEfolder/templates $special_name/";
			#print "Templates are in $dlcheckfolder<br>";
			my @featDeadlines;
			#my @allbaseweeks = getweeks();
			my $week;
			my @featlist = getSpecialStarted($special_name);
			#print 	"@featlist";
			#$_|$week|$step|$baseFolder/$week/$step/$_|$file_modTime
		if (-d $dlcheckfolder) {
			opendir(DLDIR, $dlcheckfolder);
			my @dlfiles = readdir DLDIR;
			closedir(DLDIR);
			foreach (@dlfiles) {
				if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
					next;
				} else {
					my @fileParts = split('\.',$_);
					my $poststatus = "Not Complete";
					#my %featSpec = hashAFile("$dlcheckfolder$_");
					my $featName = $fileParts[0];
					my $spec_ext = "spe";
					#my $daydue = $featSpec{'dueday'};
					#my $dlduetime = $featSpec{'duetime'};
					#my $weeksToAdd = $featSpec{'dueweek'};
					#my $offsetWeeks = $weeksToAdjust;
					#my $dayweek = getweeksout($offsetWeeks);
					#print "ADDING: ${featName}.${spec_ext}\n";
					if ($featName ne '') {
						@featDeadlines = (@featDeadlines,"${featName}.${spec_ext}");
					}
				}  #END (($_ =~ /^\./m) || ($_ eq "") || (!defined($_)))
		 	} #END foreach (@dlfiles)
		} #END if (-d $dlcheckfolder)
		 	my $thisFeature;
		 	my @dlParts;
		 	my $dlName;
		 	my $dlweek;
		 	my $dldueday;
		 	my $dlduetime;
		 	my $Foundit;
		 	my $dlstatus;
		 		my @parts;
		 		my $feature;
		 		my $featstep;

		foreach my $featstarted (@featDeadlines) {
		 	$thisFeature;
		 	#print "Looking for $featstarted<br>";
		 	@dlParts = split('\|',$featstarted);
		 	$dlName = $dlParts[0];
		 	#$dlweek = $dlParts[1];
		 	#$dldueday = $dlParts[2];

		 	#	if ("$dldueday" eq "$todayDay") {
			#		$dldueday = "Today";
			#	}

		 	#$dlduetime = $dlParts[3];
		 	#		my $duehour = substr($dlduetime,0,2);
			#		my $duemins = substr($dlduetime,2);
			#$dlduetime = "$duehour:$duemins";
		 	$Foundit = "FALSE";
		 	$dlstatus = "Not Started";

			foreach my $thisFeature (@featlist) {
		 		@parts = split('\|',$thisFeature);
		 		$feature = $parts[0];
		 		$featstep = $parts[2];
		 		$featlink = $parts[3];
		 		$featmod = $parts[4];
		 			#print "$feature is in $featstep at $featlink $featmod<br>";
=begin list
			[0] = filename
			[1] = week of (mdd)
			[2] = step
			[3] = location
			[4] = file last modified	#"$_|$week|$step|$baseFolder/$week/$step/$_|$file_modTime"
=cut list

				#print "this feature is $feature in $featstep <br>started feature is $dlName for $dlduetime\n\n";
		 		if (($dlName eq $feature) && ($featstep eq "Filtered")) {
		 			$Foundit = "TRUE";
		 			my $dlstatus = "Complete";
		 			#print "Found a Feature: $dlstatus|$thisFeature|$dldueday|$dlduetime|$featstep\n";
					@deadlineList = (@deadlineList,"$dlstatus|$feature|$dldueday|$dlduetime|$featstep|$featlink|$featmod");
		 		}
		 		if (($dlName eq $feature) && ($featstep ne "Filtered")) {
		 			$Foundit = "TRUE";
	 				my $dlstatus = "Started - $featstep";
		 			#print "Found a Feature: $dlstatus|$thisFeature|$dldueday|$dlduetime|$featstep\n";
		 			@deadlineList = (@deadlineList,"$dlstatus|$feature|$dldueday|$dlduetime|$featstep|$featlink|$featmod");
		 		} #END

		 	}	#END foreach $thisFeature (@featlist)
			 if ($Foundit ne "TRUE") {
		 		#print "Didn't find a Feature: Not Started|$dlName<br>";
				@deadlineList = (@deadlineList,"Not Started|$dlName|$dldueday|$dlduetime|Not Started|$featlink|$featmod");
			 }
	} #END of foreach $featstarted (@featDeadlines)
		@deadlineList = sort @deadlineList;
return(@deadlineList);
}

sub showFeatmanoptions { #usage showfeatureheader

my @featureslist = getFeatStarted();

my ($look,$feel) = @_;
my $CardStep;
my ($week1,$week2,$week3,$week4,$week5,$week6,$week7) = getweeks();
my @allbaseweeks = ($week1,$week2,$week3,$week4,$week5,$week6,$week7);
#my @allbaseweeks = ($week2,$week3,$week4,$week5);
my $baseFolder = "$FeatFolder/";
my $liveList = "$baseFEfolder/liveFeatList.txt";
my @stepoptions = getstatelist();
my $STvalue;
my %steptovalue;
#my @featureslist = getFeatStarted();
my $weekNumbers = @allbaseweeks;
############## Optional information based upon the input of filters
#	showFeatmanoptions("search",$mysearch);
#	showFeatmanoptions("step",$step);
#	showFeatmanoptions("week",$weekof);
#	showFeatmanoptions("all","all");
#	$progStatus = "Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>";
my @valuesteps = ("In Progress","Copy Edit","Final Read","Filtered");
foreach $hashStep (@valuesteps) {
	$STvalue++;
	$steptovalue{$hashStep} = $STvalue;
}
my $maxValue = $STvalue;


if ($look eq 'all') {

	my @featureslist = getFeatStarted();

	foreach my $sWeek (@allbaseweeks) {
#		foreach my $steps (@stepoptions) {
			ClosedDIV("class","CardCatHead","Features for the week of $sWeek");
			#### Get all the features not started and have available to show if requested
					my @deadlines = getFeatNS($weekNumbers);
					foreach $thisdl (@deadlines) {
					#print "$thisdl<br>";
						my @deadlineparts = split('\|',$thisdl);
						my $dlStatus = $deadlineparts[0];
						my $dlName = $deadlineparts[1];
						my $dlDay = $deadlineparts[2];
						my $dlTime = $deadlineparts[3];
						my $dlState = $deadlineparts[4];
						my $lLink = $deadlineparts[5];
						my $file_time = $deadlineparts[6];
						my @getTMPname = split('\.',$dlName);
						my $tmp = "./templates/${getTMPname[0]}.tmp";
						my @StatusParts = split(' - ',$dlStatus);
						if ($dlStatus eq "Not Started") {
								$progStatus = "Not Started";
								$valStat = "0";
								$NotStartTally++;
								$divHead = "DLHeadNS";
							if ($dlDay eq "Today") {
								$col1Info = "<b>$dlName</b> <hr>Due: ${dlDay} at $dlTime";
							} else {
								$col1Info = "<b>$dlName</b> <hr>Due: ${dlDay}s at $dlTime";
							}
							$actionButton = "<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"story\" value=\"$dlName\"><input type=\"hidden\" name=\"status\" value=\"new\"><input type=\"submit\" value=\"Start $dlName\"></form>\n";
							#@notStartedCol = (@notStartedCol,"$progStatus|$valStat|$divHead|$col1Info|$actionButton");
							OpenDIV("class","ContentCardNS");
							ClosedDIV("class","ContentCardHead","$dlName");
							ClosedDIV("class","ContentCardBody","Not Started");
							ClosedDIV("class","ContentCardFooter","$actionButton");
							EndDIV();
						}
					}
			#### END     Get all the features not started and have available to show if requested
			my $count = 0;
			foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				if (($lFile ne "") && ($sWeek eq $lWeek)) {
					my @filesplit = split(/\./,$lFile);
					my $nametmp = $filesplit[0];
					my $tmp = "./templates/${nametmp}.tmp";
					my $spc = "./specs/${nametmp}.spc";
					my %FeatSpecs = hashAFile($spc);
					$count++;
					my $FeatStatus = $FeatSpecs{'status'};
					#checkFeatForTest($nametmp);
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
						$CardStep = "Complete!";
						OpenDIV("class","ContentCardComplete");
					} else {
						$CardStep = $lStep;
						OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","$lFile","($FeatStatus) $thisWriter Last Modified: $file_time");
					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					ClosedDIV("class","ContentCardFooter","<form method=\"\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();
				} #end remove empty
			}#end @featureslist
				#}
#		}#end @stepoptions
				#if ($count == 0) {
				#	ClosedDIV("class","ContentInfo","No features found for the week of $sWeek");
				#}
	$weekNumbers--;
	} #end @allbaseweeks
			#ClosedDIV("class","CardCatHead","$count Features found for week of $sWeek");

} #end default value

if ($look eq 'search')  {
	my @featureslist = getFeatStarted();
	#foreach my $sWeek (@allbaseweeks) {
	#ClosedDIV("class","ContentBoxHead","Feature week of $sWeek");
			#foreach my $featline (@featureslist) {
			#print "$featline\n<br>";
			#}
			ClosedDIV("class","ContentBoxPlain","Search results for text - $feel");
		foreach my $sWeek (@allbaseweeks) {
					 my $count = 0;
			ClosedDIV("class","CardCatHead","Results for the week of $sWeek");
		foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				if (($lFile ne "") && ($sWeek eq $lWeek)) {
				#print "File location: $lLink \n<br>";
					use Tie::File;
					tie my @records, 'Tie::File', $lLink;
					my $all_lines = join "\n",@records;
					#			print "$lFile - \n<br> $all_lines\n<br>";
					untie @records;
					my $uc_all_lines = uc($all_lines);
					#			print "$lFile - \n<br> $uc_all_lines\n<br>";
					my $uc_feel = uc($feel);
					# print "searching for $uc_feel\n";
					if ($uc_all_lines =~ m/$uc_feel/) {
						$count++;
						my $thisWriter = findAuthor($lLink);
						if ($lStep eq "Filtered") {
						$CardStep = "Complete!";
						OpenDIV("class","ContentCardComplete");
						} else {
						$CardStep = $lStep;
						OpenDIV("class","ContentCard");
						}
						ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

						ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
						ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
						EndDIV();
					} #end search for matching text
			}#end @featureslist
				} #end if (($lFile ne "") && ($sWeek eq $lWeek))
					if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<p>No features match for this week.</p>");
					}
				} #end @allbaseweeks

} #end text search

if ($look eq 'feature')  {
	my @featureslist = getFeatStarted();
	my $count = 0;
			foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				my @featname = split ('\.',$lFile);
				if ($featname[0] =~ m/$feel/i) {
					$count++;
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();
					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","<b>$lStep</b> <br> Last modified: <b>$file_time</b> <br>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist
					if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<h2><center>No features found.<c/enter></h2>");
					}
} #end text search

### Step search
#########################
if ($look eq 'step')  {

	my @featureslist = getFeatStarted();
			foreach my $feat (@featureslist) {
				#ClosedDIV("class","ContentBoxFull","Checking $feel for MMMM $feat MMMM");
				#print "</div>";
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				my @fileSplits = split('\.',$lFile);
				my $templateUSe = "$fileSplits[0].tmp";
				my $tmp = "./templates/$templateUSe";
				if ($lStep eq $feel) {
					$count++;
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();

					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","<b>$lStep</b> <br> Last modified: <b>$file_time</b><br>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist
					if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<h2><center>No features found.</center></h2>");
					}

} #end step search

if ($look eq 'stepweek')  {

my ($thisstep,$thisweek) = split ('\|',$feel);

	my @featureslist = getFeatStarted();
			foreach my $feat (@featureslist) {
				#ClosedDIV("class","ContentBoxFull","Checking $feel for MMMM $feat MMMM");
				#print "</div>";
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
				if (($lStep eq $thisstep) && ($lWeek eq $thisweek)) {
					$count++;
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();

					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","<b>$lStep</b> <br> Last modified: <b>$file_time</b><br>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist
					if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<h2><center>No features found.</center></h2>");
					}

} #end step search

### week search
#########################

if ($look eq 'weekof') {
	my @featureslist = getFeatStarted();
	#ClosedDIV("class","ContentBoxHead","Features week of $feel");
#=begin test
					my $weekNumbers;
					#my ($week1,$week2,$week3,$week4,$week5,$week6) = getweeks();
					my @allWeeks = getweeks();
					my $weekcounter = 5;
					foreach (@allWeeks) {
						if ($_ eq $feel) {
							$weekNumbers = $weekcounter;
							#print "Week is $_<br> Counter is at $weekNumbers<br>";
						} else {
							$weekcounter--;
						}
					}
					my @deadlines = getFeatNS($weekNumbers);
					foreach $thisdl (@deadlines) {
					#print "$thisdl<br>";
						my @deadlineparts = split('\|',$thisdl);
						my $dlStatus = $deadlineparts[0];
						my $dlName = $deadlineparts[1];
						my $dlDay = $deadlineparts[2];
						my $dlTime = $deadlineparts[3];
						my $dlState = $deadlineparts[4];
						my $lLink = $deadlineparts[5];
						my $file_time = $deadlineparts[6];
						my @getTMPname = split('\.',$dlName);
						my $tmp = "./templates/${getTMPname[0]}.tmp";
						my @StatusParts = split(' - ',$dlStatus);
						if ($dlStatus eq "Not Started") {
								$progStatus = "Not Started";
								$valStat = "0";
								$NotStartTally++;
								$divHead = "DLHeadNS";
							if ($dlDay eq "Today") {
								$col1Info = "<b>$dlName</b> <hr>Due: ${dlDay} at $dlTime";
							} else {
								$col1Info = "<b>$dlName</b> <hr>Due: ${dlDay}s at $dlTime";
							}
							$actionButton = "<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"story\" value=\"$dlName\"><input type=\"hidden\" name=\"status\" value=\"new\"><input type=\"submit\" value=\"Start $dlName\"></form>\n";
							#@notStartedCol = (@notStartedCol,"$progStatus|$valStat|$divHead|$col1Info|$actionButton");
							OpenDIV("class","ContentCardNS");
							ClosedDIV("class","ContentCardHead","$dlName");
							ClosedDIV("class","ContentCardBody","Not Started");
							ClosedDIV("class","ContentCardFooter","$actionButton");
							EndDIV();
						}
					}

#=cut section
#		foreach my $steps (@stepoptions) {
			foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
#				if (($lStep eq $steps) && ($lWeek == $feel)) {
				if (($lWeek eq $feel) && ($feat ne "")) {
					$count++;
					my $thisWriter = findAuthor($lLink);
					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");

					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();

					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","$lStep last modified $file_time <br>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist

#		} #end @stepoptions
				#if ($count == 0){
				#	ClosedDIV("class","ContentBoxFull","<h2><center>No features found.</center></h2>");
				#}

} #end week value

if ($look eq 'writer') {
	my @featureslist = getFeatStarted();
		foreach my $steps (@stepoptions) {
			foreach my $feat (@featureslist) {
				my ($lFile,$lWeek,$lStep,$lLink,$file_time) = split ('\|',$feat);
					$count++;
					my $thisWriter = findAuthor($lLink);
				if (($lStep eq $steps) && ($thisWriter =~ /$feel/)) {

					if ($lStep eq "Filtered") {
					$CardStep = "Complete!";
					OpenDIV("class","ContentCardComplete");
					} else {
					$CardStep = $lStep;
					OpenDIV("class","ContentCard");
					}
					ClosedDIV("class","ContentCardHead","<b>$lFile</b>","$thisWriter Last Modified: $file_time");
					ClosedDIV("class","ContentCardBody","<b>$CardStep</b><br><progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","ContentCardBody","<b>$file_time</b>");
					ClosedDIV("class","ContentCardFooter","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					EndDIV();

					#OpenDIV("class","ContentBoxGood");
					#ClosedDIV("class","Content2of6Col","<b>$lFile</b>  <br> $thisWriter");
					#ClosedDIV("class","Content2of6Col","<b>$lStep</b> <br> Last modified: <b>$file_time</b>Progress: <progress value=\"$steptovalue{$lStep}\"max =\"$maxValue\">Step $steptovalue{$lStep} of $maxValue</progress>");
					#ClosedDIV("class","Content2of6Col","<form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi\"><input type=\"hidden\" name=\"tmp\" value=\"$tmp\"><input type=\"hidden\" name=\"modtime\" value=\"$file_time\"><input type=\"hidden\" name=\"fileLoc\" value=\"$lLink\"><input type=\"hidden\" name=\"status\" value=\"$lStep\"><input type=\"hidden\" name=\"story\" value=\"$lFile\"><input type=\"hidden\" name=\"viewtype\" value=\"ViewOnly\"><input type=\"submit\" value=\"View $lFile\"></form>");
					#EndDIV();
				} #end compare week and step
			}#end @featureslist
		} #end @writeroptions
			if ($count == 0){
					ClosedDIV("class","ContentBoxFull","<h2><center>No features found.</center></h2>");
			}

} #end week value

}#End Sub

sub makeHeaderTopper {

OpenDIV("class","HeaderTopper");
ClosedDIV ("class","TopperRight","<a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi\">Feature Photo Manager</a>");
#ClosedDIV ("class","TopperRight","<a href=\"http://$ThisIP/cgi-bin/FE2/featureDeadlines.cgi?deadlineweek=This Week\">Feature Deadline Manager</a>");
ClosedDIV ("class","TopperRight","<a href=\"http://$ThisIP/cgi-bin/FE2/specialsmanager.cgi\">Special Features Manager</a>");
ClosedDIV ("class","TopperRight","<a href=\"http://$ThisIP/cgi-bin/FE2/FCM_Backend.cgi\">FCM Backend Manager</a>");
ClosedDIV ("class","TopperRight","<a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi\">Features Content Manager</a>");
EndDIV();

}
sub makePhotosNAVbar {
my ($feature,$thisWeek) = @_;

my @storyparts = split('\.',$feature);
my $featName = $storyparts[0];
my $featWeek = $storyparts[1];
my ($ThisIP,$systemOn) = getHomeAddress();
my @allFeats = getFeatStarted();
my $home_page = "$ThisIP/cgi-bin/FE2/featurePhotos.cgi";
my $tmpFile = "$baseFEfolder/templates/$featName.tmp";
my ($week1,$week2,$week3,$week4,$week5,$week6,$week7) = getweeks();
my @allsteps = getstatelist();
my @allbaseweeks = getweeks();
my $PhotoFile = "$baseFEfolder/PhotoData/NewPhotoList.txt";
my $PosterPhotoFile = "$baseFEfolder/PhotoData/PhotoPosterPhotos.txt";
#my $PosterSetsFile = "$baseFEfolder/PhotoData/PhotoPosterSets.txt";
my $PosterSetsFile = "$baseFEfolder/PhotoData/NewPhotoSets.txt";
my @photosAndGroups = arrayFile($PhotoFile);
my @allPhotos = arrayFile($PosterPhotoFile);
my @allArchives = arrayFile($PosterSetsFile);
my @allGroups;
my @allSets;
foreach (@photosAndGroups) {
	if ($_ !~ m/^#/) {
		my @Parts = split('\|',$_);
		my $setName = $Parts[1];
		if (($setName ~~ @allGroups) || ($setName eq "")) {
		next; }
		 else 	{ @allGroups = (@allGroups,$setName);
		}
	}
}
my @allGroups = sort @allGroups;

foreach (@allArchives) {
	if ($_ !~ m/^#/) {
		my @Parts = split('\|',$_);
		my $setName = $Parts[0];
		if (($setName ~~ @allSets) || ($setName eq "")) {
		next; }
		 else 	{ @allSets = (@allSets,$setName);
		}
	}
}

@allSets = sort @allSets;
#@allSets = (@allSets,"Photo Poster");

#bottom NAV
print "<nav>\n";
print "	<ul>\n";
my $featLocation;
my $statusStep;

if ($feature ne "") {
	foreach (@allFeats) {
	#print $_, "\n";
		my @featParts = split('\|',$_);
		my $featCheck = $featParts[0];
	#print "$featParts[0] and $_\n";
		if (uc($featCheck) eq uc($feature)) {
		#foreach (@featParts) {
		#	print $_, "<br>";
		#}
			$featLocation = $featParts[3];
			$statusStep = $featParts[2];
			#print "Feature location is $featLocation<br>";
			last;
		}
	}

	print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?feature=$featName\.spc\">Show All $featName Photos</a>\n";
#	print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi?tmp=$tmpFile&fileLoc=$featLocation&status=$statusStep&story=$feature&viewtype=ViewOnly\">Return to $feature </a>\n";
	print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/feature_editor.cgi?tmp=$tmpFile&fileLoc=$featLocation&status=$statusStep&story=$feature&viewtype=ViewOnly\">Return to $feature </a>\n";
	#print "tmp=$tmpFile&fileLoc=$featLocation&status=$statusStep&story=$feature&viewType=ViewOnly";
} else {
	#print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=Sync\">Sync Photos</a>\n";
#	print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi\">New Week Photos</a>\n";

#2 layer drop down menu
	print "	<li><a href=\"#\">Get Photos &darr;</a>\n";
	print "	<ul>\n";
		foreach my $weeklink (@allbaseweeks) {
			print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?weekof=$weeklink&pageType=all\">$weeklink</a>\n";
			print "	<ul>\n";
			my @photoFormats = ("ALL","JPG","BW","CMYK","EPS");
			foreach my $format (@photoFormats) {
			print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?weekof=$weeklink&pageType=$format\">$format</a>\n";
			}
			print "	</ul>\n";
		}
		print "</li>\n";
	print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=moviesearch\">Movie Photos Search</a>\n";
	#	print "</li><form><input type=\"text\" id=\"photoSearch\" name=\"search\" placeholder=\"Photo Search..\"><input type=\"hidden\" name=\"pageMode\" value=\"photoInfo\"><input type=\"hidden\" name=\"pageType\" value=\"search\"><input type=\"submit\" value=\"Submit\"></form>\n";
		print "</li>\n";
	print "	</ul>\n";
#######################
	print "	<li><a href=\"#\">Photo groups &darr;</a>\n";
	print "	<ul>\n";
		foreach my $set (@allGroups) {
			my @setPieces = split('\|',$set);
			print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=$setPieces[0]&pageType=sets\">$setPieces[0] &rarr;</a>\n";
			print "	<ul>\n";
			foreach my $weeklink (@allbaseweeks) {
				print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=$setPieces[0]&pageType=sets&weekof=$weeklink\">$weeklink</a>\n";
			}
			print "	</ul>\n";

		}
		print "</li>\n";
#}
print "	</ul>\n";
	print "	<li><a href=\"#\">Photo Archive Sets &darr;</a>\n";
	print "	<ul>\n";
		foreach my $set (@allSets) {
			my @setPieces = split('\|',$set);
			print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=$setPieces[0]&pageType=archives\">$setPieces[0] &rarr;</a>\n";
			print "	<ul>\n";
			foreach my $weeklink (@allbaseweeks) {
				print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=$setPieces[0]&pageType=archives&weekof=$weeklink\">$weeklink</a>\n";
			}
			print "	</ul>\n";
		}
print "	</ul>\n";
	print "	<li><a href=\"#\">Run Photo Poster&darr;</a>\n";
	print "	<ul>\n";
				print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=Photo Poster&pageType=archives&weekof=0\">This Week's Photos</a>\n";
				print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=Photo Poster&pageType=archives&weekof=-1\">Last Week's Photos</a>\n";
				print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=Photo Poster&pageType=archives&weekof=1\">Next Week's Photos</a>\n";
	print "	</ul>\n";
	print "</li>\n";

	print "	<li><a href=\"#\">What's Due &darr;</a>\n";
	print "	<ul>\n";
				print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=whats_due&pageType=today&search=all\">Due Today</a>\n";
				print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=whats_due&pageType=late&search=all\">Whats Late</a>\n";
				print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=whats_due&pageType=all&search=all\">This Week</a>\n";
	print "	</ul>\n";
	print "</li>\n";

my @tempFiles = ArrayADir("$baseFEfolder/specs/","No");
my @photoSpecList;
foreach my $specName (@tempFiles) {
	my %specHash = hashAFile("$baseFEfolder/specs/$specName.spc");
	my $photoList = $specHash{'photo'};
	if ($photoList ne "") {
		push @photoSpecList,$specName;
	}
}
my @tempFiles = sort(@photoSpecList);
my $size = @tempFiles;

my $threeParts = int($size/3);
my $sectionOne = $threeParts;
my $sectionTwo = $threeParts*2;
my $sectionThree = $size;
my @sectionOneArray = @tempFiles[0..$sectionOne];
my @sectionTwoArray = @tempFiles[($sectionOne+1)..$sectionTwo];
my @sectionThreeArray = @tempFiles[($sectionTwo+1)..($size-1)];

my $sectionCounter = 0;
print "	<li><a href=\"#\">Feature Name &darr;</a>\n";
print "	<ul>\n";
	print "	<li>$tempFiles[0]<br>&darr;<br>$tempFiles[$sectionOne]\n";
#my $AllFeatList = getFileList("$baseFEfolder/templates","No");
print "	<ul>\n";
	foreach my $tempFile (@sectionOneArray) {
		print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?feature=$tempFile.spc\">$tempFile</a>\n";
	}
#print "<li><form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi\"><select name=\"feature\">\n$AllFeatList</select><input type=\"submit\" value=\"Show Feature\"></form>\n";
print "</li>\n";
print "	</ul>\n";
	print "	<li>$tempFiles[$sectionOne+1]<br>&darr;<br>$tempFiles[$sectionTwo]\n";
#my $AllFeatList = getFileList("$baseFEfolder/templates","No");
print "	<ul>\n";
	foreach my $tempFile (@sectionTwoArray) {
		print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?feature=$tempFile.spc\">$tempFile</a>\n";
	}
#print "<li><form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi\"><select name=\"feature\">\n$AllFeatList</select><input type=\"submit\" value=\"Show Feature\"></form>\n";
print "</li>\n";
print "	</ul>\n";
	print "	<li>$tempFiles[$sectionTwo+1]<br>&darr;<br>$tempFiles[$size-1]\n";
#my $AllFeatList = getFileList("$baseFEfolder/templates","No");
print "	<ul>\n";
	foreach my $tempFile (@sectionThreeArray) {
		print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?feature=$tempFile.spc\">$tempFile</a>\n";
	}
#print "<li><form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi\"><select name=\"feature\">\n$AllFeatList</select><input type=\"submit\" value=\"Show Feature\"></form>\n";
print "</li>\n";
print "	</ul>\n";
print "	</ul>\n";
print "</li>\n";
print "</li>\n";

	print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=bulkUpload&weekof=$weeklink\">Upload</a>\n";
		print "</li>\n";

	print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?pageMode=xmlfeats\">XML Photos</a>\n";
		print "</li>\n";

		print "<li><form><input type=\"text\" id=\"photoSearch\" name=\"search\" placeholder=\"Photo Search..\"><input type=\"hidden\" name=\"pageMode\" value=\"photoInfo\"><input type=\"hidden\" name=\"pageType\" value=\"search\"><input type=\"submit\" value=\"Submit\"></form>\n";
		print "</li>\n";
print "	</ul>\n";

print "</li>\n";

}
print "</nav>\n";

} # end makeNAVbar
sub makeNAVbar {
#my $home_page = $_[0];
my ($ThisIP,$systemOn) = getHomeAddress();
my $home_page = "$ThisIP/cgi-bin/FE2/featuremanager.cgi";
my ($week1,$week2,$week3,$week4,$week5,$week6,$week7) = getweeks();
my @allsteps = getstatelist();
my @allbaseweeks = getweeks();

#bottom NAV
print "<nav>\n";
print "	<ul>\n";
print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi\">Show All Features</a>\n";

#2 layer drop down menu
print "	<li><a href=\"#\">Steps &darr;</a>\n";
print "	<ul>\n";
foreach my $thisstep (@allsteps) {
	print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?step=$thisstep\">$thisstep</a>\n";
	print "	<ul>\n";
		foreach my $weeklink (@allbaseweeks) {
			print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?step=$thisstep&weekof=$weeklink\">$weeklink</a>\n";
		}
		print "</li>\n";
	print "	</ul>\n";
}
print "	</ul>\n";
print "</li>\n";
print "</li>\n";
# end 2 layer drop down
# new drop goes here
print "	<li><a href=\"#\">Weeks &darr;</a>\n";
print "	<ul>\n";
	foreach my $weeklink (@allbaseweeks) {
		print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?weekof=$weeklink\">$weeklink</a>\n";
	}
	print "</li>\n";
print "	</ul>\n";
###** end new drop down.

# new drop goes here
# print "	<li><a href=\"#\">Writers &darr;</a>\n";
# my @allWriters = getWriters();
# print "	<ul>\n";
# 	foreach my $writer (@allWriters) {
# 		print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?writer=$writer\">$writer</a>\n";
# 	}
# print "</li>\n";
# print "	</ul>\n";
###** end new drop down.
my @tempFiles = ArrayADir("$baseFEfolder/templates/","No");
my $size = @tempFiles;
my $threeParts = int($size/3);
my $sectionOne = $threeParts;
my $sectionTwo = $threeParts*2;
my $sectionThree = $size;
my @sectionOneArray = @tempFiles[0..$sectionOne];
my @sectionTwoArray = @tempFiles[($sectionOne+1)..$sectionTwo];
my @sectionThreeArray = @tempFiles[($sectionTwo+1)..($size-1)];

my $sectionCounter = 0;
print "	<li><a href=\"#\">Feature Name &darr;</a>\n";
print "	<ul>\n";
	print "	<li>$tempFiles[0]<br>&darr;<br>$tempFiles[$sectionOne]\n";
#my $AllFeatList = getFileList("$baseFEfolder/templates","No");
print "	<ul>\n";
	foreach my $tempFile (@sectionOneArray) {
		print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?feature=$tempFile\">$tempFile</a>\n";
	}
#print "<li><form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi\"><select name=\"feature\">\n$AllFeatList</select><input type=\"submit\" value=\"Show Feature\"></form>\n";
print "</li>\n";
print "	</ul>\n";
	print "	<li>$tempFiles[$sectionOne+1]<br>&darr;<br>$tempFiles[$sectionTwo]\n";
#my $AllFeatList = getFileList("$baseFEfolder/templates","No");
print "	<ul>\n";
	foreach my $tempFile (@sectionTwoArray) {
		print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?feature=$tempFile\">$tempFile</a>\n";
	}
#print "<li><form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi\"><select name=\"feature\">\n$AllFeatList</select><input type=\"submit\" value=\"Show Feature\"></form>\n";
print "</li>\n";
print "	</ul>\n";
	print "	<li>$tempFiles[$sectionTwo+1]<br>&darr;<br>$tempFiles[$size-1]\n";
#my $AllFeatList = getFileList("$baseFEfolder/templates","No");
print "	<ul>\n";
	foreach my $tempFile (@sectionThreeArray) {
		print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?feature=$tempFile\">$tempFile</a>\n";
	}
#print "<li><form method=\"post\" action=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi\"><select name=\"feature\">\n$AllFeatList</select><input type=\"submit\" value=\"Show Feature\"></form>\n";
print "</li>\n";
print "	</ul>\n";
print "	</ul>\n";
print "</li>\n";
print "</li>\n";

=begin
print "	<li><a href=\"#\">Steps &darr;</a>\n";
print "	<ul>\n";
foreach my $thisstep (@allsteps) {
	print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?step=$thisstep\">$thisstep</a>\n";
	print "	<ul>\n";
		foreach my $weeklink (@allbaseweeks) {
			print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?step=$thisstep&weekof=$weeklink\">$weeklink</a>\n";
		}
		print "</li>\n";
	print "	</ul>\n";
}
print "	</ul>\n";
print "</li>\n";
print "</li>\n";

=cut
print "	<li>|\n";
print "</li>\n";

###** link to a pagetype.
print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?pageType=newFeat\">Start A New Feature</a>\n";
print "</li>\n";
###** end link to a pagetype.

###** link to a pagetype.
print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi?pageType=textSearch\">Search Feature Text</a>\n";
print "</li>\n";
###** end link to a pagetype.


print "	</ul>\n";
print "</nav>\n";

} # end makeNAVbar

sub makeDLNAVbar {
#my $home_page = $_[0];
my ($ThisIP,$systemOn) = getHomeAddress();
my $home_page = "$ThisIP/cgi-bin/FE2/featuremanager.cgi";
my @DLstatus = ("Not Started","Started","Complete");
my ($week1,$week2,$week3,$week4,$week5,$week6,$week7) = getweeks();
my @allsteps = getstatelist();
my @allbaseweeks = getweeks();
my @filterdays = ("Today","This Week","Next Week","All Weeks");
print "<nav>\n";
print "	<ul>\n";
#print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featuremanager.cgi\">Return to Feature Manager Page</a>\n";
#print "</li>\n";
# new drop goes here
print "	<li><a href=\"#\">Filter Deadlines &darr;</a>\n";
print "	<ul>\n";
	foreach my $dayof (@filterdays) {
		print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featureDeadlines.cgi?deadlineweek=$dayof\">$dayof</a>\n";
	print "	<ul>\n";
		foreach my $state (@DLstatus) {
			print "	<li><a href=\"http://$ThisIP/cgi-bin/FE2/featureDeadlines.cgi?deadlineweek=$dayof&statefilter=$state\">$state</a>\n";
		}
		print "</li>\n";
	print "	</ul>\n";

	}
	print "</li>\n";
print "	</ul>\n";
###** end new drop down.
# new drop goes here
print "	</ul>\n";
print "	</ul>\n";
print "</nav>\n";
} # end makeNAVbar

sub MakeAPreview {
	my ($TFile,$OFile,$storyName) = @_;
	my @getDate = split '\.',$OFile;
	my $thisDate = $getDate[1];
	my @cgiListNames = getTmpNameList($TFile);
	my @storyParts = split '\.',$storyName;
if ($storyParts[1] eq "spe") {
	my $SpecName = getSpecialsInfo();
	my $specFile = "$baseFEfolder/specs $SpecName/${storyParts[0]}.spc";
	} else {
	my $specFile = "$baseFEfolder/specs/${storyParts[0]}.spc";
	}
	my %GetFeatSpecs = hashAFile($specFile);
	my $col_val = $GetFeatSpecs{'colnum'};
	my $photoList = $GetFeatSpecs{'photo'};
	my $captionList = $GetFeatSpecs{'caption'};
	my @allCaptions = split '\,',$captionList;
	my $usePhoto;
	my $useCaption = "";
	my $this_cap = "";
	if ($photoList =~ /jpg/) {
		my @thisPhotoList = split '\,',$photoList;
		#print "Photo list is @thisPhotoList\n";
		my $findNum = 0;
		foreach (@thisPhotoList) {
			#print "$_   ";
			if ($_ =~ /.jpg$/) {
				$usePhoto = $_;
				$useCaption = $allCaptions[$findNum];
				chomp($useCaption);
		#		print "Use caption is $useCaption<br>";
				$usePhoto =~ s/MDD/$thisDate/g;
				last;
			}
			$findNum++;
			#$usePhoto =~ s/MDD/$thisDate/g;
			#print "Photo will be $usePhoto";
		}
	} else {
			$usePhoto = "";
			#my @exifdata = getPhotoExif("/Images/$thisDate/$usePhoto");	
			#	$useCaption = "";
	}
	#			print "Use caption is $useCaption<br>";

	if ($usePhoto ne "") { my $photoLocale = "/Images/$thisDate/$usePhoto"; } #else { print "No valid photos found\n"; }
	my $columnMaker = "";
	my $NewspaprCol;
	open FP,"<",$OFile;
	my @thisList = <FP>;
	close FP;

	my $allrecords = join "", @thisList;
	foreach my $CGIlist (@cgiListNames) {
		chomp($CGIlist);
		my $whereToGo = "";
		my $markEnd = "";
		my @lineValues = getTMPLinevalues($TFile,$CGIlist);
		# [0] = field name
		# [1] = text field type
		# [2] = merlmarkup
		# [3] = default text
		# [4] = Placement marker ex. SideBar, Content to indicate where to place on the page and also to indicate it is not
		#        a part of the final filtered feature
		#$whereToGo = $lineValues[4];

		my $markStart = getMerltoHtmlMark($TFile,$CGIlist);

		#my $markStart = $lineValues[2];
		#print "$whereToGo<br>";
		if ($lineValues[4] eq "SideBar") {
			next;
		} elsif ($lineValues[4] eq "Video") {
			my $vidline = $lineValues[0];
			$this_vid = $allrecords;
			$this_vid =~ /\<$vidline\>(.*)\<\/$vidline\>/;
			$vidLink = $1;
			$featPreview = "$featPreview<center>$vidLink</center><br><hr>";
		} elsif ($lineValues[4] eq "Content") {
			my $this_line = $allrecords;
			$this_line =~ /\<$CGIlist\>(.*)\<\/$CGIlist\>/;
			$this_line = $1;
			utf8::decode($this_line);
			$featPreview = "$featPreview<br><p class=\"alt\">$CGIlist:<br>$this_line</p>";

		} elsif ($lineValues[4] eq "Photo") {
				$usePhoto = $lineValues[1];
#				print "Found photo - $usePhoto<br>";
				$useCaption = $lineValues[2];
				my $photoSize = $lineValues[3];
				if ($photoSize eq "") {
					$photoSize = "30";
				}
				$usePhoto =~ s/MDD/$thisDate/g;
				#print "Caption is $useCaption<br>";
				if ($useCaption ne "") {
					chomp($useCaption);
		#			print "Use caption is $useCaption<br>";
					$this_cap = $allrecords;
					$this_cap =~ /\<$useCaption\>(.*)\<\/$useCaption\>/;
					$this_cap = $1;
					utf8::decode($this_cap);
				} else {
					my @exifdata = getPhotoExif("/Library/WebServer/Documents/Images/$thisDate/$usePhoto");	
					$this_cap = "Photo Caption:<br>$exifdata[1]";
					utf8::decode($this_cap);
				}
				#print "Photo width is $photoSize";
				$featPreview = "$featPreview<figure class=\"photo-preview\" width=\"${photoSize}%\"><img src=\"/Images/$thisDate/$usePhoto\"><figcaption>$this_cap</figcaption></figure>";
			#print "$CGIlist belongs on the sidebar\n";
		} elsif (($CGIlist eq "EP") || ($CGIlist eq "Hidden") || ($CGIlist eq "EOF")) {
			$featPreview = "$featPreview${markStart}<br>";#Don't add these until we are ready for production.
		} else  {
			my $this_line = $allrecords;
			$this_line =~ /\<$CGIlist\>(.*)\<\/$CGIlist\>/;
			$this_line = $1;

			utf8::decode($this_line);
			#if ($CGIlist eq $useCaption) {
			# my $photoCap = $thisLine;
			#}
			if ($CGIlist eq "Headline") {
				$featPreview = "$featPreview${markStart}<h1><b>${this_line}</b></h1><br>";
			#	if ($usePhoto ne "") {
			#			my $this_cap = $allrecords;
			#			$this_cap =~ /\<$useCaption\>(.*)\<\/$useCaption\>/;
			#			$this_cap = $1;
			#			if ($this_cap eq $this_line) {
			#			$this_cap = "";
			#			}
			#			#print "Photo caption is $this_cap";
			#			$featPreview = "$featPreview<figure class=\"photo-preview\"><img src=\"/Images/$thisDate/$usePhoto\"  width=\"30%\"><figcaption>$this_cap</figcaption></figure>";
			#	}
			} else {
				$featPreview = "$featPreview${markStart}$this_line<br>";
			}
		}
	}
return($featPreview);
}

sub MakeASideBar {
	my ($TFile,$OFile,$storyName,$viewType) = @_;
	my @cgiListNames = getTmpNameList($TFile);
	#print "$OFile";
		my @fileParts = split '\/',$OFile;
		my $featureName = $fileParts[6];
		my @storyParts = split '\.',$featureName;
		my $featWeek = $storyParts[1];
		my $specFile = "$baseFEfolder/specs/$storyName.spc";
		my $photoDir = "/Library/WebServer/Documents/Images/$featWeek";
		my @photoList = ArrayADir($photoDir);
		my %specHash = hashAFile($specFile);
		my $photoList = $specHash{'photo'};
		$photoList =~ s/MDD/$featWeek/g;
		my @allPhotos = split '\,',$photoList;
		#print "@allPhotos";
		open FP,"<",$OFile;
			my @thisList = <FP>;
		close FP;

		my $allrecords = join "", @thisList;

	foreach my $CGIlist (@cgiListNames) {
		my $this_line;
		chomp($CGIlist);
		#utf8::decode($this_line);
		my @lineValues = getTMPLinevalues($TFile,$CGIlist);
					#ClosedDIV("class","NotesField","Placement for $CGIlist is $lineValues[4]");

		if ($lineValues[4] eq "SideBar") {
			my $this_line = $allrecords;
			$this_line =~ /\<$CGIlist\>(.*)\<\/$CGIlist\>/;
			$this_line = $1;
			#print "Placement for $CGIlist is $lineValues[4]<br>";
			#ClosedDIV("class","NotesField","Placement for $CGIlist is $lineValues[4]");
			ClosedDIV("class","SidebarTitle","$CGIlist");
			OpenDIV("class","SidebarGroup");
			#$this_line =~ s/\<br\>/\n/g;
			if ($this_line eq "") {
				$this_line = "No data for $CGIlist";
			}

			if ($viewType eq "edit") {
				ClosedDIV("class","ContentFormField","<textarea rows=\"10\" name=\"$CGIlist\">$this_line</textarea>");
			} else {
				ClosedDIV("class","NotesField","$this_line");
			}

			EndDIV();
		#No photos for specials, yet
		#	if ($CGIlist eq "Photo") {
		#		ClosedDIV("class","SidebarTitle","Photos list");
		#		OpenDIV("class","SidebarGroup");
		#		foreach (@allPhotos) {
		#			if ($_ ~~ @photoList) {
		#			ClosedDIV("class","NotesField","$_ is posted");
		#			} else {
		#			ClosedDIV("class","NotesField","<mark>$_ NOT posted</mark>");
		#			}
		#		}
		#		EndDIV();
		#		ClosedDIV("class","SidebarTitle","<a href=\"http://$ThisIP/cgi-bin/FE2/featurePhotos.cgi?tmp=$specFile&fileLoc=$featWeek&status=\"Filtered\"&story=$featureName&viewtype=Edit\">Manage These Photos</a><hr>\n");
		#	}

		}

		# [0] = field name
		# [1] = text field type
		# [2] = merlmarkup
		# [3] = default text
		# [4] = optional field marker indicated by "Opt"
		# [5] = number of columns for feature. Should be in the Body line Defaults to 1

	}
}

sub MakeAWebPage {
	my ($TFile,$OFile,$storyName,$photo,$caption) = @_;
	my @cgiListNames = getTmpNameList($TFile);
	#my @featSpecs = getFeatSpecs("$storyName");
	my $col_val = $featSpecs[1];
	#print @featSpecs;
	my $columnMaker = "";
	my $NewspaprCol;
	open FP,"<",$OFile;
	my @thisList = <FP>;
	close FP;
	my $allrecords = join "", @thisList;
	foreach my $CGIlist (@cgiListNames) {
		#print "Field: $CGIlist\n";
		chomp($CGIlist);
		my $markEnd = "";
		my @lineValues = getTMPLinevalues($TFile,$CGIlist);

		# [0] = field name
		# [1] = text field type
		# [2] = merlmarkup
		# [3] = default text
		# [4] = optional field marker indicated by "Opt"
		# [5] = number of columns for feature. Should be in the Body line Defaults to 1

		my $markStart = getMerltoHtmlMark($TFile,$CGIlist);

		#my $markStart = $lineValues[2];
		if (($CGIlist eq "EP") || ($CGIlist eq "Hidden") || ($CGIlist eq "EOF")) {
			$featPreview = "$featPreview<br>";#Don't add these until we are ready for production.
		} else {
			my $this_line = $allrecords;
			$this_line =~ /\<$CGIlist\>(.*)\<\/$CGIlist\>/;
			$this_line = $1;
			utf8::decode($this_line);
			#print "$CGIlist is $this_line\n";
			$this_line =~ s/\s+/ /g; #find more than one space together replace with single space
			$this_line =~ s/\n+/\<br>/g; #change new lines to html breaks
			$this_line =~ s/\<br \/>/\<\/p> \<p>/g; #change new lines to html breaks
			$this_line =~ s/<\/strong><\/p> <p>/<\/p> <p><\/strong>/g;
			$this_line =~ s/\"/ \&quot /g; #change double quotes to html double quote
			#print  "<${CGIlist}>${this_line}</${CGIlist}>\n";
			#print "Field $CGIlist is $this_line\n";

			if ($CGIlist eq "Headline") {
				$featPreview = "$featPreview<headline>${markStart}<h1><b>${this_line}</b></h1></headline><br><article>";
			} elsif ($CGIlist eq "Copyright") {
				$columnMaker = "$columnMaker${markStart}${this_line}";
			} elsif ($CGIlist eq "Byline") {
				$columnMaker = "$columnMaker${markStart}${this_line}</b><br>";
			} elsif ($CGIlist eq "Body") {
				if ($photo ne "") {
					$featPreview = "$featpreview<img src=\"$photo\" alt=\"$photo\" width=\"100\" height=\"200\" style=\"float:right\">\n";
				}
				#$columnMaker = "$columnMaker";
				if ($col_val eq "3") {
					$NewspaprCol = "$columnMaker<div class=\"Content3col\">${markStart}${this_line}</div>";
				} elsif ($col_val eq "2") {
					$NewspaprCol = "$columnMaker<div class=\"Content2col\">${markStart}${this_line}</div>";
				} else {
					$NewspaprCol = "$columnMaker${markStart}${this_line}";
				}
				#	$columnMaker = "$columnMaker<hr><div class=\"Content3col\">${markStart}${this_line}</div><br>";
				#my $NewspaprCol = "$columnMaker<div class=\"Content3col\">${markStart}${this_line}</div>";
				$featPreview = "$featPreview${NewspaprCol}</article>";
			}
		}
	}
return($featPreview);
}


## used to search within all features and grab the byline that conatins the author's name.
## This routine is called by the search function to display a list of features written by a specific writer.
sub findAuthor {
my $thisAuthor = "Not Applicable";
my $fileToCheck = $_[0];
open FH, "<", $fileToCheck;
	my @records = <FH>;
	my $allrecords = join "", @records;
	if ($allrecords =~ /\<Byline\>/) {
		$allrecords =~ /\<Byline\>(.*)\<\/Byline\>/s;
		$thisAuthor = $1;
		}
close FH;
return $thisAuthor;
}

sub findRecord {
my ($recordFind,$featureName) = @_;
my $returnText = "No value found";
my $fileToCheck = $featureName;
open FH, "<", $fileToCheck;
	my @records = <FH>;
	my $allrecords = join "", @records;
close FH;
	if ($allrecords =~ /\<$recordFind\>/) {
		$allrecords =~ /\<$recordFind\>(.*)\<\/$recordFind\>/s;
		$returnText = $1;
		}
return $returnText;
}


sub findNotes {
my $thisNote = "No Notes Found";
my $fileToCheck = $_[0];
open FH, "<", $fileToCheck;
	my @records = <FH>;
	my $allrecords = join "", @records;
close FH;
	if ($allrecords =~ /\<Notes\>/) {
		$allrecords =~ /\<Notes\>(.*)\<\/Notes\>/s;
		$thisNote = $1;
		}
return $thisNote;
}

sub findPhoto {
my $thisPhoto = "No Photo Info Found";
my $fileToCheck = $_[0];
open FH, "<", $fileToCheck;
	my @records = <FH>;
	my $allrecords = join "", @records;
close FH;
	if ($allrecords =~ /\<Photo\>/) {
		$allrecords =~ /\<Photo\>(.*)\<\/Photo\>/s;
		$thisPhoto = $1;
	} else {
	$thisPhoto = "No photo";
	}
return $thisPhoto;
}

sub CheckforPhoto {
my $foundPhoto = "No";
my $fileToCheck = $_[0];
open FH, "<", $fileToCheck;
	my @records = <FH>;
close FH;
	foreach (@records) {
		if ($_ =~ /^Photo/) {
			$foundPhoto = "Yes";
		}
	}
return $foundPhoto;
}

sub FeatureToHash {
#returns hash with TEMP field name as key and value is from what's in the feature
# tempFile and feature need to be full paths.
my ($tempFile,$feature) = @_;
		my %FeatHash;
		tie my @records, 'Tie::File', $feature;
		my $allrecords = join "", @records;
		untie @records;
		open TF, "<",$tempFile;
		my @TempFields = <TF>;
		close TF;
		my @cgiListNames = getTmpNameList($tempFile);
		foreach my $CGIlist (@cgiListNames) {
			chomp($CGIlist);
			#my $markEnd = "";
			#my @lineValues = getTMPLinevalues($tempFile,$CGIlist);
			my $this_line = $allrecords;
			my $this_line =~ /\<$CGIlist\>(.*)\<\/$CGIlist\>/s;
		$FeatHash{$CGIlist} = $this_line;
		}
return(%FeatHash);
}

sub hashAFile {
#returns hash for a file with | (pipe) delims
my ($thisFile) = $_[0];
		my %FileHash;
		my $line;
		my @records = arrayFile($thisFile);
		foreach $line (@records) {
			chomp($line);
			my @twoParts = split('\|',$line);
			my $thisKey = $twoParts[0];
			my $thisValue = $twoParts[1];
			$FileHash{$twoParts[0]} = $twoParts[1];
		}
return(%FileHash);
}

### Not used, but might be usefull at another release date.
# This takes feature text and creates a 3 col layout table.
# Column layouts look more similar to newspaper type layouts and could be easier to read on screen.

sub show3ColPrev {
my ($title,$byline,$copy,$body,$contact,$name,$story,$cap1,$cap2) = @_;

my @wordlist = split(/\s/, $body);
my $wc = scalar(@wordlist);
my $intoThirds = scalar($wc/3);
my $col1end = scalar($intoThirds);
my $col2end = scalar(($intoThirds * 2));
my $wordPos = "0";
print "<table width =\"100%\" cellpadding=\"10\">\n";
print "<tr valign=\"top\"><td colspan=\"3\"><h1>$title</h1></td></tr>\n";
print "<tr valign=\"top\"><td colspan=\"3\"><hr></td></tr>\n";
print "<tr valign=\"top\"><td width=\"33%\">\n";
print "Body word count is $wc<br>\n";
print "<b>$byline</b></br>\n";
print "&#169;$copy\n</br></br>\n";
	while ($wordPos <= $col1end) {
		print " $wordlist[$wordPos]";
		$wordPos = $wordPos + 1;
	}
print "</td>";
print "<td width=\"33%\">";
	while ($wordPos <= $col2end) {
		print " $wordlist[$wordPos]";
		$wordPos = $wordPos + 1;
	}
print "</td>";
print "<td width=\"33%\">";
	while ($wordPos <= $wc) {
		print " $wordlist[$wordPos]";
		$wordPos = $wordPos + 1;
	}
print "<b>$contact</b>\n$breakbreak\n";
print "</td></tr>\n";
print "<tr><td colspan=\"3\"><b>Caption 1: $cap1\n$breakbreak</td></tr>\n";
print "<tr><td colspan=\"3\"><b>Caption 2: $cap2\n$breakbreak</td></tr>\n";
print "</table>\n";

}

sub makeColPrev {
#my ($title,$byline,$copy,$body,$contact,$name,$story,$cap1,$cap2) = @_;
my $columnText = "";
my ($textTOdo,$colnum) = @_;
if ($colnum eq "") {
	$colnum = 3;
}
my @wordlist = split(/\<\/p\>/, $textTOdo);
my $wc = scalar(@wordlist);
my $intoThirds = scalar($wc/3);
my $col1end = scalar($intoThirds);
my $col2end = scalar(($intoThirds * 2));
my $wordPos = "0";
$columnText = "<table width =\"100%\" cellpadding=\"10\">\n";
#print "<tr valign=\"top\"><td colspan=\"3\"><h1>$title</h1></td></tr>\n";
#print "<tr valign=\"top\"><td colspan=\"3\"><hr></td></tr>\n";
$columnText = "$columnText<tr valign=\"top\"><td width=\"33%\">\n";
#my $wordTally = $columnText = "$columnTextBody word count is $wc<br>\n";
#print "<b>$byline</b></br>\n";
#print "&#169;$copy\n</br></br>\n";
while ($wordPos <= $col1end) {
		$columnText = "$columnText $wordlist[$wordPos]";
		$wordPos = $wordPos + 1;
	}
$columnText = "$columnText</td>";
$columnText = "$columnText<td width=\"33%\">";
	while ($wordPos <= $col2end) {
		$columnText = "$columnText $wordlist[$wordPos]";
		$wordPos = $wordPos + 1;
	}
$columnText = "$columnText</td>";
$columnText = "$columnText<td width=\"33%\">";
	while ($wordPos <= $wc) {
		$columnText = "$columnText $wordlist[$wordPos]";
		$wordPos = $wordPos + 1;
	}
#print "<b>$contact</b>\n$breakbreak\n";
$columnText = "$columnText</td></tr>\n";
#print "<tr><td colspan=\"3\"><b>Caption 1: $cap1\n$breakbreak</td></tr>\n";
#print "<tr><td colspan=\"3\"><b>Caption 2: $cap2\n$breakbreak</td></tr>\n";
$columnText = "$columnText</table>\n";
return($columnText);
}


## creates 2 levels of directory in the FF2 directory of MDD/Step
## takes 2 parameters: (baseweek(MDD), Step name)
sub makeadir {
	my $fold1 = $_[0];
	my $fold2 = $_[1];
	my $directory1 = "$FeatFolder/$fold1";
	#print "attempting to create directory $directory\n";

	unless(-e $directory1 or mkdir $directory1) {
		die "Unable to create $directory\n";
	}
	chmod(0777,$directory1);
		my $directory2 = "$FeatFolder/$fold1/$fold2";
	unless(-e $directory2 or mkdir $directory2) {
		die "Unable to create $directory\n";
	}
	chmod(0777,$directory2);

}

sub makeaPhotodir {
	my $fold1 = $_[0];
	#my $fold2 = $_[1];
	my $directory1 = "/Library/WebServer/Documents/Images/$fold1";
	#print "attempting to create directory $directory\n";
	my $scanDir = "/Volumes/Scans/Ready For Production/$fold1";
	unless(-e $directory1 or mkdir $directory1) {
		print  "Uh-oh! Unable to create $directory\n";
	}
	chmod(0777,$directory1);
	unless(-e $scanDir or mkdir $scanDir) {
		print  "Uh-oh! Scans Volume is not mounted on this machine. Please contact jason.gifford\@nielsen.com\n";
	}
	chmod(0777,$scanDir);

	my $directory3 = "/Library/WebServer/Documents/Images/XML/$fold1";
	#print "attempting to create directory $directory\n";
	#my $scanDir = "/Volumes/Scans/Ready For Production/XML/$fold1";
	unless(-e $directory3 or mkdir $directory3) {
		print  "Uh-oh! Unable to create $directory3\n";
	}
	chmod(0777,$directory3);
#	unless(-e $scanDir) {
}
sub syncPhotos {
	my $runScript = system("perl /PerlLib/syncScans.pl $weekof");
}
sub oldsyncPhotos {
	use File::Copy;
	my $scansBaseDir = "/Volumes/Scans/Ready For Production/";
	my $photoDir = "/Library/WebServer/Documents/Images/";
	my @allWeeks = getweeks();
	foreach my $photoWeek (@allWeeks) {
			opendir(DLDIR, "$photoDir$photoWeek");
			my @localfiles = readdir DLDIR;
			closedir(DLDIR);
			opendir(SCANDIR, "$scansBaseDir$photoWeek");
			my @scansfiles = readdir SCANDIR;
			closedir(SCANDIR);
print "Local photos for week of $photoWeek in $photoDir$photoWeek - " . scalar(@localfiles) . "<br>";
print "Scan photos for week of $photoWeek in $scansBaseDir$photoWeek - " . scalar(@scansfiles) . "<br>";

			foreach (@localfiles) {
				if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
					next;
				} else {
					if ($_ ~~ @scansfiles) {
						next;
					} else {
						#print "Copying $_ to $scansBaseDir$photoWeek/$_<br>";
						#copy("$photoDir$photoWeek/$_","$scansBaseDir$photoWeek/$_");
					}
				}
			}
	}
}

sub makeaPhotoSetdir {
	my $fold1 = $_[0];
	#my $fold2 = $_[1];
	my $directory1 = "/Library/WebServer/Documents/ImageSets/$fold1";
	#print "attempting to create directory $directory\n";

	unless(-e $directory1 or mkdir $directory1) {
		die "Unable to create $directory\n";
	}
	chmod(0777,$directory1);
}

sub PhotoGetter {

use Net::FTP;
use File::Copy;
my @args = @ARGV;
my $destinationFolder =  $args[1];
my $photo = $args[0];
#my $downloadDir = $args[1];
downloadFile("10.187.67.82", "features", "0feats2", "mac", "$destinationFolder$photo", "$photo");
## Unstuffs downloaded file. Option "-e no" says to never put file in a folder. Leaving out this option will let
##		stuffit to determine on it's own whether or not to do that.
##		This became a problem because it was putting single photos in a folder.
system("/usr/local/bin/unstuff -e no $destinationFolder$photo >> /dev/null");
system("/bin/rm $destinationFolder$photo >> /dev/null");

}

sub downloadFile
{
	my @parameters = @_;
	my $server = "$parameters[0]";
	my $user = "$parameters[1]";
	my $pass = "$parameters[2]";
	my $init = "$parameters[3]";	#supports only one level
	my $path = "$parameters[4]";
	my $downloadname = "$parameters[5]";

	my $ftp = Net::FTP->new("$server", Debug => 0, Passive => 0);
	$ftp->login("$user","$pass");
	$ftp->binary();
	$ftp->cwd("$init");
	$ftp->get("$downloadname","$path") or warn (print "**WARNING** - Cannot find $photo on Features FTP\n");
	$ftp->quit;
	return 1;
}

## creates 2 levels of directory in the FF/History directory of MDD/Step
## takes 2 parameters: (baseweek(MDD), Step name)

sub makeahistdir {
	my $fold1 = $_[0];
	my $fold2 = $_[1];
	my $directory1 = "$FeatFolder/History/$fold1";
	#print "attempting to create directory $directory\n";

	unless(-e $directory1 or mkdir $directory1) {
		die "Unable to create $directory\n";
	}
	chmod(0777,$directory1);
		my $directory2 = "$FeatFolder/History/$fold1/$fold2";
	unless(-e $directory2 or mkdir $directory2) {
		die "Unable to create $directory\n";
	}
	chmod(0777,$directory2);

}

sub getweeks {
#  gets a list of Sunday baseweeks for use in filenames, etc.
#  returns next for Sunday baseweeks in MDD format

	my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
	my ($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear);
	my  @forwardsOfWeek = qw( 0 -86400 -172800 -259200 -345600 -432000 -518400 );
	my $time = time();
	my  $shiftZero = "$forwardsOfWeek[$f_weekDay]";
	$shiftZero = $time + $shiftZero;
	my $epochweekback = -604800;
	my $epochweekforward = 604800;
	my $shiftbackone = $shiftZero + $epochweekback;
	my $shiftbacktwo = $shiftbackone + $epochweekback;
	my $shiftbackthree = $shiftbackone + $epochweekback;
	my $shiftupone = $shiftZero + $epochweekforward;
	my $shiftuptwo = $shiftupone + $epochweekforward;
	my $shiftupthree = $shiftuptwo + $epochweekforward;
	my $shiftupfour = $shiftupthree + $epochweekforward;
	my $shiftupfive = $shiftupfour + $epochweekforward;
	my $shiftupsix = $shiftupfive + $epochweekforward;
	my $shiftupseven = $shiftupsix + $epochweekforward;

	#print "$time\n";
	# Takes current time in seconds and shifts it to the correct day of log cycle.
	($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftbacktwo);
		$mm++;
	if($day < 10)
	{
	 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		$mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $weekback2 = "$mm$day";

	($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftbackone);
		$mm++;
		if ($day < 10)
	{
		 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		 $mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $weekback1 = "$mm$day";

		($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftZero);
		$mm++;
	if($day < 10)
	{
		 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		 $mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $thisweek = "$mm$day";

			($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftupone);
		$mm++;
	if($day < 10)
	{
		 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		 $mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $weekup1 = "$mm$day";


			($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftuptwo);
		$mm++;
	if($day < 10)
	{
		 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		 $mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $weekup2 = "$mm$day";


			($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftupthree);
		$mm++;
	if($day < 10)
	{
		 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		 $mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $weekup3 = "$mm$day";


			($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftupfour);
		$mm++;
	if($day < 10)
	{
		 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		 $mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $weekup4 = "$mm$day";

				($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftupfive);
		$mm++;
	if($day < 10)
	{
		 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		 $mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $weekup5 = "$mm$day";

					($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftupsix);
		$mm++;
	if($day < 10)
	{
		 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		 $mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $weekup6 = "$mm$day";

				($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($shiftupseven);
		$mm++;
	if($day < 10)
	{
		 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		 $mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $weekup7 = "$mm$day";

	#return("o12","o05","928","921","914","907","831","824");
	return($weekup7,$weekup6,$weekup5,$weekup4,$weekup3,$weekup2,$weekup1,$thisweek);
}

sub getweeksout {
#  gets the mdd date of the number of weeks offset
#  returns next for Sunday baseweeks in MDD format
	my $numofweeksout = $_[0];
	#my $numofweeksout += 0;
	my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
	my ($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear);
	my  @forwardsOfWeek = qw( 0 -86400 -172800 -259200 -345600 -432000 -518400 );
	my $time = time();
	my  $shiftZero = "$forwardsOfWeek[$f_weekDay]";
	$shiftZero = $time + $shiftZero;
	my $epochweekback = -604800;
	my $epochweekforward = 604800;
	my $epochOffset = $numofweeksout * $epochweekforward;
	my $epochweek = $shiftZero + $epochOffset;


	#print "$time\n";
	# Takes current time in seconds and shifts it to the correct day of log cycle.
	($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($epochweek);
		$mm++;
	if($day < 10)
	{
	 $day = "0$day";
	}
	if($mm == 10)
	{
		 $mm = "o";
	}
	elsif($mm == 11)
	{
		$mm =  "n";
	}
	elsif($mm == 12)
	{
		 $mm =  "d";
	}
	my $thisweek = "$mm$day";


	return($thisweek);
}

## Sends feature out via email.
# This can determine who gets the email based upon the step it was changed to.
# If the step does not change (with the exception of Filtered), this routine will not be called upon.
sub emailnotifier {
	use MIME::Lite;
		my $toLine = "";
	my @parameters = @_;
	my $oldstatus = $parameters[0];
	my $thisstatus = $parameters[1];
	my $thisfile = $parameters[2];
	my $thisstory = $parameters[3];
	my $thisspec = $parameters[4];
	my %GetFeatSpecs = hashAFile($thisspec);
	my $emailGroup = $GetFeatSpecs{'emailgroup'};
	#print "Found a list of emails - $emailGroup\n";
	my @allEmails = split(',',$emailGroup);
	#print "Found email $thisspec and it's list @allEmails\n";
	foreach (@allEmails) {
		if ($toLine eq "") {
		$toLine = "$_\@nielsen.com"
		} else {
		$toLine = "$toLine,$_\@nielsen.com"
		}
	}
	#my @Specs = getFeatSpecs($thisstory);
	#my $emailDist = $Specs[4];
	my $gLogFilePath = "$thisfile";
	my @fileparts = split('/',$thisfile);
	chomp($oldstatus);
	chomp($thisstaus);

	my $date = $fileparts[4];
	my $state = $fileparts[5];
	my $filename = $fileparts[6];
	my @featureName = split('\.',$filename);
	my $FeatNoDot = $featureName[0];
	my $FeatWeek = $featureName[1];
	#my $toLine = "$emailDistm"; # by default
	if ($toLine eq "") {
	$toLine = "jason.gifford\@nielsen.com";
	}
	if ($systemType eq "Development") {
		$toLine = "jason.gifford\@nielsen.com,kalinn.saunders\@nielsen.com";
	}
	my $subjectLine = "$filename has changed status from $oldstatus to $thisstatus";

if (($thisstatus eq 'Filtered') && ($oldstatus eq 'Filtered')) {
		my $subjectLine = "$filename has been refiltered";
	}
	if ($thisstatus eq 'trash') {
		my $subjectLine = "$filename has been deleted";

	}
if ($thisstatus eq 'posted') {
	my $subjectLine = "$filename has been posted.";
	$toLine = "jason.gifford\@nielsen.com,kalinn.saunders\@nielsen.com";
}
	my $runninglog = "";
	my $mailline = "";
	#my $addr = "163.193.250.55";
	open (MAILLOGFILE, "$gLogFilePath") || die "Could not open log file to email!";
	while ($mailline = <MAILLOGFILE>)
	{
		$runninglog = "$runninglog$mailline<br>";
	}
	close(MAILLOGFILE);
    #  print "Created Email\nGoing to $toLine\nSubject is $subjectLine";
  #print "Sending email message with error.\n";
  #	$toLine = "jason.gifford\@nielsen.com, george.dickie\@nielsen.com";

    my $msg = MIME::Lite->new (
    From    => "FeatureManager\@nielsen.com",
    To      => "$toLine",
    Subject => "$subjectLine",
    #Subject => "Where is my Subject?",
    Type    => "text/html",
    Data    => "$runninglog",

    );
    $msg->send();

}

sub CopyEditnotifier {
	use MIME::Lite;
	my $toLine = "";
	my @parameters = @_;
	my $oldstatus = $parameters[0];
	my $thisstatus = $parameters[1];
	my $thisfile = $parameters[2];
	my $thisstory = $parameters[3];
	my $thisspec = $parameters[4];
#my %GetFeatSpecs = hashAFile($thisspec);
	#my $emailGroup = $GetFeatSpecs{'emailgroup'};
	#print "Found a list of emails - $emailGroup\n";
	#my @allEmails = split(',',$emailGroup);
	#print "Found email $thisspec and it's list @allEmails\n";
	#foreach (@allEmails) {
	#	if ($toLine eq "") {
	#	$toLine = "$_\@nielsen.com"
	#	} else {
	#	$toLine = "$toLine,$_\@nielsen.com"
	#	}
	#}
	#my @Specs = getFeatSpecs($thisstory);
	#my $emailDist = $Specs[4];
	my $gLogFilePath = "$thisfile";
	my @fileparts = split('/',$thisfile);
	chomp($oldstatus);
	chomp($thisstaus);
	my $date = $fileparts[4];
	my $state = $fileparts[5];
	my $filename = $fileparts[6];
	my @featureName = split('\.',$filename);
	my $FeatNoDot = $featureName[0];
	my $FeatWeek = $featureName[1];
	#my $toLine = "$emailDistm"; # by default
	$toLine = "jason.gifford\@nielsen.com, george.dickie\@nielsen.com, michelle.wilson\@nielsen.com, tara.weaver\@nielsen.com,Susan.Pierce\@nielsen.com";
	if ($systemType eq "Development") {
		$toLine = "jason.gifford\@nielsen.com,kalinn.saunders\@nielsen.com";
	}

	my $subjectLine = "Ready for Copy Edit: $filename";

	my $mailHyperLink = "";
	my $runninglog = "";
	my $mailline = "";
	#my $addr = "163.193.250.55";
	open (MAILLOGFILE, "$gLogFilePath") || die "Could not open log file to email!";
	while ($mailline = <MAILLOGFILE>)
	{
		$runninglog = "$runninglog$mailline<br>";
	}
	close(MAILLOGFILE);
    #  print "Created Email\nGoing to $toLine\nSubject is $subjectLine";
  #print "Sending email message with error.\n";
    my $msg = MIME::Lite->new (
    From    => "FeatureManager\@nielsen.com",
    To      => "$toLine",
    Subject => "$subjectLine",
    #Subject => "Where is my Subject?",
    Type    => "text/html",
    Data    => "$runninglog",

    );
    $msg->send();

}

##Not used
sub findEmailDist {
	my $FeatureName = $_[0];
	chomp($FeatureName);
	my $returnDist = "jason.gifford\@nielsen.com";
	my %featTOdist = (
	"spofan" => "jason.gifford\@nielsen.com,dladd\@nielsen.com,kyle.lewis\@nielsen.com",
	"spoquiz" => "jason.gifford\@nielsen.com,kyle.lewis\@nielsen.com",
	);
	while ( my ($key, $value) = each %featTOdist ) {
		if ($key eq $FeatureName) {
			my $returnDist = $value;
		}
	}
return($returnDist);
}



## created the drop down that lists all the available feature to create new for a specific week.
# This is used on the main featureman site. This also does not include any features already started.
sub getNewFeatslistoptions {
	my @thisIsAllFeatures = getFeatStarted();
	my @featInEdit = getFeatInEdit();
	my $count = 0;
	my $weektofind = $_[0];
	my $tmpfeatlist = "";
	my $tempfolder = "$baseFEfolder/templates/";
	opendir(TMPDIR, $tempfolder);
	my @tmpfiles = readdir TMPDIR;
	closedir(TMPDIR);
	#my @allbaseweeks = getweeks();
		foreach my $featname (@tmpfiles) {
			my @featparts = split (/\./,$featname);
				if ($featparts[0] ne "") {
					my $featnameweek = "$featparts[0].${weektofind}";
					#### my $seeFeat = checkforFeat("$featnameweek");
					my $fileFound = "FALSE";
					my $fileCheck = $_[0];
						foreach my $thisfeat (@thisIsAllFeatures) {
							my @section = split(/\|/,$thisfeat);
								if ($section[0] eq $featnameweek) {
									$fileFound = "TRUE";
								}
						}
						foreach my $thisEditfeat (@featInEdit) {
								my @section = split(/\|/,$thisEditfeat);
								if	($section[0] eq $featnameweek) {
									$fileFound = "TRUE";
								}
						}

					######
					if ($fileFound eq "FALSE") {
						$tmpfeatlist = ("$tmpfeatlist<option value=\"$featnameweek\">$featnameweek</option>\n");
						$count++;
					}
				}
			if ($count == 0) {$tmpfeatlist = "No Features"};
		}
return($tmpfeatlist);
}

#returns a list of files in a directory (Parameter 1) with a specific extension (Parameter 2) and created a option value drop down.
# used to create a drop down of feature names based upon available tmp file in the template directory
sub getFileList {
	#/Library/WebServer/CGI-Executables/templates
	my $filenameList = "";
	my $tempfolder = $_[0];
	my $extOption = $_[1];
	opendir(TMPDIR, $tempfolder);
	my @tmpfiles = readdir TMPDIR;
	closedir(TMPDIR);
		foreach my $name (@tmpfiles) {
			my @parts = split (/\./,$name);
				if ($parts[0] ne "") {
					if ($extOption eq "No") {
						my $fileList = "$parts[0]";
						$filenameList = ("$filenameList<option value=\"$fileList\">$fileList</option>\n");
					} else {
						my $fileList = "$parts[0].$parts[1]";
						$filenameList = ("$filenameList<option value=\"$fileList\">$fileList</option>\n");
					}
				}
		}
return($filenameList);
}

sub convertMMDDYYYYtoMDD {
	my @xmlFiles = @_;
	my $filenameList = "";
	foreach (@xmlFiles) {
		$filenameList = ("$filenameList<option value=\"$_\">$_</option>\n");
	}
return($filenameList);
}

sub ArrayADir {
	my @filenameListArray;
	my $tempfolder = $_[0];
	my $extOption = $_[1];
	opendir(TMPDIR, $tempfolder);
	my @tmpfiles = readdir TMPDIR;
	closedir(TMPDIR);
		foreach my $name (@tmpfiles) {
			my @parts = split (/\./,$name);
				if ($parts[0] ne "") {
					if ($extOption eq "No") {
						my $fileList = "$parts[0]";
						push(@filenameListArray,"$fileList");
					} else {
						#my $fileList = "$parts[0].$parts[1]";
						push(@filenameListArray,"$name");
					}
				}
		}
return(@filenameListArray);

}
### checks to see if a feature has already been started. Returns TRUE or FALSE if the feature was found or not found.
sub checkforFeat {
my @thisIsAllFeatures = getFeatStarted();
	# Check to see a feature already exists when user selects to create a new feature receives the file name with date
	my $fileFound = "FALSE";
	my $fileCheck = $_[0];
	foreach my $thisfeat (@thisIsAllFeatures) {
		my @section = split(/\|/,$thisfeat);
		if ($section[0] eq $fileCheck) {
			$fileFound = "TRUE";
		}
	}
return($fileFound);
}

## returns a searchable list of features that have been started. This is used in many aspects throughout this site.
## returns a pipe delimited file of all features for all weeks.
sub getFeatStarted {
	my @featlist = "";

		#my ($week1,$week2,$week3,$week4,$week5,week6) = getweeks(); #Gets Sunday dates. week3 is current Sunday mdd
		my @allbaseweeks = getweeks();

#	my $baseFolder = "$FeatFolder";
	my $baseFolder = "$FeatFolder";
	my @allsteps = getstatelist();
	foreach my $week (@allbaseweeks) {
			foreach my $step (@allsteps) {
				my $checkfolder = "$baseFolder/$week/$step/";
				#print "Checking $checkfolder\n";
					if (-d $checkfolder) {
					opendir(DIR, $checkfolder);
					my @files = readdir DIR;
				    closedir(DIR);
					    foreach (@files) {
							if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
							next;
							}
							else {
							my $file_modTime = getFileStats("$baseFolder/$week/$step/$_");
							my $addthis = "$_|$week|$step|$baseFolder/$week/$step/$_|$file_modTime";
							 @featlist = (@featlist,$addthis);
							}
		 				 }
		 			 }
			}
	}

return(@featlist);
}

sub getSpecialStarted {
	my @featlist;
	my $specialName = $_[0];

		#my ($week1,$week2,$week3,$week4,$week5,week6) = getweeks(); #Gets Sunday dates. week3 is current Sunday mdd

#	my $baseFolder = "$FeatFolder";
	my $baseFolder = "$FeatFolder";
	my @allsteps = getstatelist();
			#print "Steps are @allsteps";
			foreach my $step (@allsteps) {
				my $checkfolder = "$baseFolder/$specialName/$step/";
				#print "Checking $checkfolder<br>";
					if (-d $checkfolder) {
					opendir(DIR, $checkfolder);
					my @files = readdir DIR;
				    closedir(DIR);
					    foreach (@files) {
							if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
							next;
							}
							else {
							my $file_modTime = getFileStats("$baseFolder/$specialName/$step/$_");
							my $addthis = "$_|$specialName|$step|$baseFolder/$specialName/$step/$_|$file_modTime";
							 @featlist = (@featlist,$addthis);
							}
		 				 }
		 			 }
			}

return(@featlist);
}


sub getPhotosStarted {
#mountScans();
	my @featlist;

		#my ($week1,$week2,$week3,$week4,$week5,week6) = getweeks(); #Gets Sunday dates. week3 is current Sunday mdd
	my @allbaseweeks = getweeks();

#	my $baseFolder = "$FeatFolder";
	#my $baseFolder = "$FeatFolder";
#	my @allsteps = getstatelist();
	foreach my $week (@allbaseweeks) {
#	print "Searching through $week<br>";
#			foreach my $step (@allsteps) {
				my $checkfolder = "/Library/WebServer/Documents/Images/$week/";
				#print "Checking $checkfolder\n";
					if (-d $checkfolder) {
					opendir(DIR, $checkfolder);
					my @files = readdir DIR;
				    closedir(DIR);
					    foreach (@files) {
							if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
							next;
							} else {
#							print "found $_<br>";
							my $file_modTime = getFileStats("$checkFolder/$_");
						#	my $addthis = "$_|$week|$checkFolder/$_|$file_modTime";
							my $addthis = "$_";
							 @featlist = (@featlist,$addthis);
							}
		 				 }
		 			}
#			}
	}

return(@featlist);
}
sub getXMLPhotosStarted {
#mountScans();
	#my @allbaseweeks = @$_[0];

	my ($week1,$week2,$week3,$week4,$week5,$week6) = getweeks(); #Gets Sunday dates. week3 is current Sunday mdd
	my @allbaseweeks = getweeks();

#	my $baseFolder = "$FeatFolder";
	#my $baseFolder = "$FeatFolder";
#	my @allsteps = getstatelist();
	foreach my $week (@allbaseweeks) {
#	print "Searching through $week<br>";
#			foreach my $step (@allsteps) {
				my $checkfolder = "/Library/WebServer/Documents/Images/XML/$week/";
				#print "Checking $checkfolder\n";
					if (-d $checkfolder) {
					opendir(DIR, $checkfolder);
					my @files = readdir DIR;
				    closedir(DIR);
					    foreach (@files) {
							if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
							next;
							} else {
#							print "found $_<br>";
							my $file_modTime = getFileStats("$checkFolder/$_");
						#	my $addthis = "$_|$week|$checkFolder/$_|$file_modTime";
							my $addthis = "$_";
							 @featlist = (@featlist,$addthis);
							}
		 				 }
		 			}
#			}
	}

return(@featlist);
}
sub getPhotosList {
	my $forweek = $_[0];
	#print "Week is $forweek";
	my @photos;
	my @photoSetList = arrayFile("$baseFEfolder/PhotoData/PhotoPosterPhotos.txt");
	#print @photoSetList;
	#my @allbaseweeks = getweeks();
		foreach my $thisFeat (@photoSetList) {
			my @photoparts = split('\|',$thisFeat);
			my $thisphoto = "$photoparts[1]${forweek}\.$photoparts[3]";
			if ($photoparts[2] ne "FileName") {
				@photos = (@photos,$thisphoto);
				#print $thisphoto, "\n<br>";
			}
		}
		my @allPhotos = sort { "\L$a" cmp "\L$b" } @photos;
return(@allPhotos);
}


sub photoChecker {
	my $is_posted;
	my @params = @_;
	my $photoName = $_[0];
	my $photoWeek = $_[1];
	my $photoDirCheck = "$PhotoDir$photoWeek/";
	opendir(TMPDIR, $photoDirCheck);
	my @photofiles = readdir TMPDIR;
	closedir(TMPDIR);
	if ($photoName ~~ @photofiles) {
		$is_posted = "Y";
	} else {
		$is_posted = "N";
	}
}

sub findDAW {
my $dawNum = $_[0];
	my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
	my @daysOfWeek = ("SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT");
	my $three_day = $daysOfWeek[$f_weekDay];
	return($three_day);
}

sub whenDue {
	my $due_diff;
	my $due_off;
	my $dawNum = $_[0];
	my $time_due = $_[1];
	my %hash_days = ("SUN" => "0", "MON" => "1","TUE" => "2","WED" => "3","THU" => "4","FRI" => "5","SAT" => "6");
	my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
	my @daysOfWeek = ("SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT");
	my @forwardsOfWeek = qw( 0 86400 172800 259200 345600 432000 518400 );
	my $now_three_day = $daysOfWeek[$f_weekDay];
		my $today_num = $hash_days{$now_three_day};
		my $due_num = $hash_days{$dawNum};
		if ($today_num == $due_num) {
			$due_diff = "due Today at $time_due";
			$due_off = "0";
		} elsif ($today_num > $due_num) {
			$due_diff = "Late! Was due $dawNum at $time_due.";
			$due_off = "";
		} else {
			$due_diff = $due_num - $today_num;
			$due_off = $due_diff;
			if ($due_diff == 1) {$due_diff = "Due Tomorrow at $time_due"} else {$due_diff = "Due in $due_diff Days";}
		}
	return($due_diff,$due_off);
}
sub arrayPhotoFile {
## Need one param. Full file path
## This filters out blank lines.
my @fileArray;
my $thisFile = $_[0];
open FH,"<$thisFile";
my @fileSplit = <FH>;
close FH;
		foreach my $line (@fileSplit) {
		if (($line ne "") && ($line !~ m/^#/)) {
			chomp($line);
			push (@fileArray,$line);
		}
		}
return(@fileArray);
}

sub makePhotoList {
	##makePhotoList("whats_due","all","today");
	my $PhotoFile = "$baseFEfolder/PhotoData/NewPhotoList.txt";
	my @listReturn;
	my @params = @_;
	my $type = $params[0];
	my $group = $params[1];
	my $when = $params[2];
	my @photoArray = arrayPhotoFile("$PhotoFile");
	my @allbaseweeks = getweeks();
	my @revbaseweeks = reverse @allbaseweeks;
	my ($jpeg,$cmyk,$BW,$eps);
	my $today_DAW = findDAW();
	#@listReturn = (@listReturn,"Today is $DAW.\n\n");
		foreach (@photoArray) {
#print "$_</br>";
		 	my @Line = split('\|',$_);
		 	my $thisGroup = $Line[1];
			my $weekof = @revbaseweeks[$Line[2]];
			my $photoName = $Line[0];
			my $dueDay = $Line[3];
			my $dueTime = $Line[4];
			my ($find_when,$due_off) = whenDue($dueDay,$dueTime);
			if ($due_off eq "0") {
				$dueDay = "today";
			}
			if ($due_off eq "") {
				$dueDay = "late";
			}

		if ((($group eq "all") || ($thisGroup eq $group)) && (($when eq "all") || ($dueDay eq $when))) {
				if ($Line[5] eq "Y") {
					my $check_4_file = photoChecker("$photoName${weekof}.jpg",$weekof);
					if ($check_4_file eq "N") {
						@listReturn = (@listReturn,"$photoName${weekof}.jpg|$find_when|$dueTime|$weekof|$dueDay");
					} else {
						@listReturn = (@listReturn,"$photoName${weekof}.jpg|Posted!|$dueTime|$weekof|Posted!");
					}
				}
				if ($Line[6] eq "Y") {
					my $check_4_file = photoChecker("${photoName}ck${weekof}.tif",$weekof);
					if ($check_4_file eq "N") {
					@listReturn = (@listReturn,"${photoName}ck${weekof}.tif|$find_when|$dueTime|$weekof|$dueDay");
					}
					else {@listReturn = (@listReturn,"${photoName}ck${weekof}.tif|Posted!|$dueTime|$weekof|Posted!");}
				}
				if ($Line[7] eq "Y") {
					my $check_4_file = photoChecker("${photoName}${weekof}.tif",$weekof);
					if ($check_4_file eq "N") {
					@listReturn = (@listReturn,"${photoName}${weekof}.tif|$find_when|$dueTime|$weekof|$dueDay");
					}
					else {@listReturn = (@listReturn,"${photoName}${weekof}.tif|Posted!|$dueTime|$weekof|Posted!");}
				}
				if ($Line[8] eq "Y") {
					my $check_4_file = photoChecker("${photoName}${weekof}.eps",$weekof);
					if ($check_4_file eq "N") {
					@listReturn = (@listReturn,"${photoName}${weekof}.eps|$find_when|$dueTime|$weekof|$dueDay");
					}
					else {@listReturn = (@listReturn,"${photoName}${weekof}.eps|Posted!|$dueTime|$weekof|Posted!");}
				}
			}
		}
return(@listReturn);
}
sub makeVoomPhotoList {
	##makePhotoList("whats_due","all","today");
	my $PhotoFile = "$baseFEfolder/PhotoData/XMLPhotoList.txt";
	my @listReturn;
	my @params = @_;
	my $type = $params[0];
	my $group = $params[1];
	my $when = $params[2];
	my @photoArray = arrayPhotoFile("$PhotoFile");
	my @allbaseweeks = getweeks();
	my @revbaseweeks = reverse @allbaseweeks;
	my ($jpeg,$cmyk,$BW,$eps);
	my $today_DAW = findDAW();
	#@listReturn = (@listReturn,"Today is $DAW.\n\n");
		foreach (@photoArray) {
#print "$_</br>";
		 	my @Line = split('\|',$_);
		 	my $thisGroup = $Line[1];
			my $weekof = @revbaseweeks[$Line[2]];
			my $photoName = $Line[0];
			my $dueDay = $Line[3];
			my $dueTime = $Line[4];
			my ($find_when,$due_off) = whenDue($dueDay,$dueTime);
			if ($due_off eq "0") {
				$dueDay = "today";
			}
			if ($due_off eq "") {
				$dueDay = "late";
			}

		if ((($group eq "all") || ($thisGroup eq $group)) && (($when eq "all") || ($dueDay eq $when))) {
				if ($Line[5] eq "Y") {
					my $check_4_file = photoChecker("$photoName${weekof}.jpg",$weekof);
					if ($check_4_file eq "N") {
						@listReturn = (@listReturn,"$photoName${weekof}.jpg|$find_when|$dueTime|$weekof|$dueDay");
					} else {
						@listReturn = (@listReturn,"$photoName${weekof}.jpg|Posted!|$dueTime|$weekof|Posted!");
					}
				}
				if ($Line[6] eq "Y") {
					my $check_4_file = photoChecker("${photoName}ck${weekof}.tif",$weekof);
					if ($check_4_file eq "N") {
					@listReturn = (@listReturn,"${photoName}ck${weekof}.tif|$find_when|$dueTime|$weekof|$dueDay");
					}
					else {@listReturn = (@listReturn,"${photoName}ck${weekof}.tif|Posted!|$dueTime|$weekof|Posted!");}
				}
				if ($Line[7] eq "Y") {
					my $check_4_file = photoChecker("${photoName}${weekof}.tif",$weekof);
					if ($check_4_file eq "N") {
					@listReturn = (@listReturn,"${photoName}${weekof}.tif|$find_when|$dueTime|$weekof|$dueDay");
					}
					else {@listReturn = (@listReturn,"${photoName}${weekof}.tif|Posted!|$dueTime|$weekof|Posted!");}
				}
				if ($Line[8] eq "Y") {
					my $check_4_file = photoChecker("${photoName}${weekof}.eps",$weekof);
					if ($check_4_file eq "N") {
					@listReturn = (@listReturn,"${photoName}${weekof}.eps|$find_when|$dueTime|$weekof|$dueDay");
					}
					else {@listReturn = (@listReturn,"${photoName}${weekof}.eps|Posted!|$dueTime|$weekof|Posted!");}
				}
			}
		}
return(@listReturn);
}

sub getPhotosTypes {
		my @allPhotos;
		my @params = @_;
		my @LineParts = split '\|',$params[0];
		my $weekOf = $params[1];
					my @photoTypes = ("$LineParts[0]$weekOf.jpg","$LineParts[0]ck$weekOf.tif","$LineParts[0]$weekOf.tif","$LineParts[0]$weekOf.eps");
					my @photoYorN = ($LineParts[5],$LineParts[6],$LineParts[7],$LineParts[8]);
					#print "@photoYorN";
					my $photoCounter = 0;
					foreach (@photoYorN) {
						if ($_ eq "Y") {
						my $photoName = $photoTypes[$photoCounter];
						#print "Photo is $photoName<br>";
						@allPhotos = (@allPhotos,$photoName);
						$photoCounter++;
						}
					}
return(@allPhotos);
}

sub getFeatDeadlines {
			my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
			my @daysOfWeek = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
			my $todayDay = $daysOfWeek[$f_weekDay];
			my @deadlineList;
			my @featlist;
			my $weeksToAdjust = $_[0];
			if ($weeksToAdjust eq '') {$weeksToAdjust = 0;}
			my $dlcheckfolder = "$baseFEfolder/specs/";
			my @featDeadlines;
			my @allbaseweeks = getweeks();
			my $week;
			my @featlist = getFeatStarted();
				#$_|$week|$step|$baseFolder/$week/$step/$_|$file_modTime
		if (-d $dlcheckfolder) {
			opendir(DLDIR, $dlcheckfolder);
			my @dlfiles = readdir DLDIR;
			closedir(DLDIR);
			foreach (@dlfiles) {
				if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
					next;
				} else {
					my $poststatus = "Not Complete";
					my %featSpec = hashAFile("$dlcheckfolder$_");
					my $featName = $featSpec{'name'};
					my $daydue = $featSpec{'dueday'};
					my $dlduetime = $featSpec{'duetime'};
					my $weeksToAdd = $featSpec{'dueweek'};
					my $offsetWeeks =  $weeksToAdd + $weeksToAdjust;
					my $dayweek = getweeksout($offsetWeeks);
					#print "ADDING: ${featName}.${dayweek}|$dayweek|$daydue|${dlduetime}\n";
					if ($featName ne '') {
						@featDeadlines = (@featDeadlines,"${featName}.${dayweek}|$dayweek|$daydue|$dlduetime");
					}
				}  #END (($_ =~ /^\./m) || ($_ eq "") || (!defined($_)))
		 	} #END foreach (@dlfiles)
		} #END if (-d $dlcheckfolder)
		 	my $thisFeature;
		 	my @dlParts;
		 	my $dlName;
		 	my $dlweek;
		 	my $dldueday;
		 	my $dlduetime;
		 	my $Foundit;
		 	my $dlstatus;
		 		my @parts;
		 		my $feature;
		 		my $featstep;

		foreach my $featstarted (@featDeadlines) {
		 	$thisFeature;
		 	@dlParts = split('\|',$featstarted);
		 	$dlName = $dlParts[0];
		 	$dlweek = $dlParts[1];
		 	$dldueday = $dlParts[2];

		 		if ("$dldueday" eq "$todayDay") {
					$dldueday = "Today";
				}

		 	$dlduetime = $dlParts[3];
		 			my $duehour = substr($dlduetime,0,2);
					my $duemins = substr($dlduetime,2);
			$dlduetime = "$duehour:$duemins";
		 	$Foundit = "FALSE";
		 	$dlstatus = "Not Started";

			foreach my $thisFeature (@featlist) {
		 		@parts = split('\|',$thisFeature);
		 		$feature = $parts[0];
		 		$featstep = $parts[2];
		 		$featlink = $parts[3];
		 		$featmod = $parts[4];
=begin list
			[0] = filename
			[1] = week of (mdd)
			[2] = step
			[3] = location
			[4] = file last modified	#"$_|$week|$step|$baseFolder/$week/$step/$_|$file_modTime"
=cut list

				#print "thisfeature is $feature in $featstep \nstarted feature is $dlName for $dlduetime\n\n";
		 		if (($dlName eq $feature) && ($featstep eq "Filtered")) {
		 			$Foundit = "TRUE";
		 			my $dlstatus = "Complete";
		 			#print "Found a Feature: $dlstatus|$thisFeature|$dldueday|$dlduetime|$featstep\n";
					@deadlineList = (@deadlineList,"$dlstatus|$feature|$dldueday|$dlduetime|$featstep|$featlink|$featmod");
		 		}
		 		if (($dlName eq $feature) && ($featstep ne "Filtered")) {
		 			$Foundit = "TRUE";
	 				my $dlstatus = "Started - $featstep";
		 			#print "Found a Feature: $dlstatus|$thisFeature|$dldueday|$dlduetime|$featstep\n";
		 			@deadlineList = (@deadlineList,"$dlstatus|$feature|$dldueday|$dlduetime|$featstep|$featlink|$featmod");
		 		} #END

		 	}	#END foreach $thisFeature (@featlist)
			 if ($Foundit ne "TRUE") {
		 		#print "Didn't find a Feature: Not Started|$feature|$dldueday|$dlduetime|$featstep\n";
				@deadlineList = (@deadlineList,"Not Started|$dlName|$dldueday|$dlduetime|Not Started|$featlink|$featmod");
			 }
	} #END of foreach $featstarted (@featDeadlines)
		@deadlineList = sort @deadlineList;
return(@deadlineList);
}

sub getFeatNS {
			my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
			my @daysOfWeek = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
			my $todayDay = $daysOfWeek[$f_weekDay];
			my @deadlineList;
			my @featlist;
			my $weeksToAdjust = $_[0];
			if ($weeksToAdjust eq '') {$weeksToAdjust = 0;}
			my $dlcheckfolder = "./specs/";
			my @featDeadlines;
			my @allbaseweeks = getweeks();
			my $week;
			my @featlist = getFeatStarted();
				#$_|$week|$step|$baseFolder/$week/$step/$_|$file_modTime
		if (-d $dlcheckfolder) {
			opendir(DLDIR, $dlcheckfolder);
			my @dlfiles = readdir DLDIR;
			closedir(DLDIR);
			foreach (@dlfiles) {
				if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
					next;
				} else {
					my $poststatus = "Not Complete";
					my %featSpec = hashAFile("$dlcheckfolder$_");
					my $featName = $featSpec{'name'};
					my $daydue = $featSpec{'dueday'};
					my $dlduetime = $featSpec{'duetime'};
					my $weeksToAdd = $featSpec{'dueweek'};
					my $offsetWeeks = $weeksToAdjust;
					my $dayweek = getweeksout($offsetWeeks);
					#print "ADDING: ${featName}.${dayweek}|$dayweek|$daydue|${dlduetime}\n";
					if ($featName ne '') {
						@featDeadlines = (@featDeadlines,"${featName}.${dayweek}|$dayweek|$daydue|$dlduetime");
					}
				}  #END (($_ =~ /^\./m) || ($_ eq "") || (!defined($_)))
		 	} #END foreach (@dlfiles)
		} #END if (-d $dlcheckfolder)
		 	my $thisFeature;
		 	my @dlParts;
		 	my $dlName;
		 	my $dlweek;
		 	my $dldueday;
		 	my $dlduetime;
		 	my $Foundit;
		 	my $dlstatus;
		 		my @parts;
		 		my $feature;
		 		my $featstep;

		foreach my $featstarted (@featDeadlines) {
		 	$thisFeature;
		 	@dlParts = split('\|',$featstarted);
		 	$dlName = $dlParts[0];
		 	$dlweek = $dlParts[1];
		 	$dldueday = $dlParts[2];

		 		if ("$dldueday" eq "$todayDay") {
					$dldueday = "Today";
				}

		 	$dlduetime = $dlParts[3];
		 			my $duehour = substr($dlduetime,0,2);
					my $duemins = substr($dlduetime,2);
			$dlduetime = "$duehour:$duemins";
		 	$Foundit = "FALSE";
		 	$dlstatus = "Not Started";

			foreach my $thisFeature (@featlist) {
		 		@parts = split('\|',$thisFeature);
		 		$feature = $parts[0];
		 		$featstep = $parts[2];
		 		$featlink = $parts[3];
		 		$featmod = $parts[4];
=begin list
			[0] = filename
			[1] = week of (mdd)
			[2] = step
			[3] = location
			[4] = file last modified	#"$_|$week|$step|$baseFolder/$week/$step/$_|$file_modTime"
=cut list

				#print "thisfeature is $feature in $featstep \nstarted feature is $dlName for $dlduetime\n\n";
		 		if (($dlName eq $feature) && ($featstep eq "Filtered")) {
		 			$Foundit = "TRUE";
		 			my $dlstatus = "Complete";
		 			#print "Found a Feature: $dlstatus|$thisFeature|$dldueday|$dlduetime|$featstep\n";
					@deadlineList = (@deadlineList,"$dlstatus|$feature|$dldueday|$dlduetime|$featstep|$featlink|$featmod");
		 		}
		 		if (($dlName eq $feature) && ($featstep ne "Filtered")) {
		 			$Foundit = "TRUE";
	 				my $dlstatus = "Started - $featstep";
		 			#print "Found a Feature: $dlstatus|$thisFeature|$dldueday|$dlduetime|$featstep\n";
		 			@deadlineList = (@deadlineList,"$dlstatus|$feature|$dldueday|$dlduetime|$featstep|$featlink|$featmod");
		 		} #END

		 	}	#END foreach $thisFeature (@featlist)
			 if ($Foundit ne "TRUE") {
		 		#print "Didn't find a Feature: Not Started|$feature|$dldueday|$dlduetime|$featstep\n";
				@deadlineList = (@deadlineList,"Not Started|$dlName|$dldueday|$dlduetime|Not Started|$featlink|$featmod");
			 }
	} #END of foreach $featstarted (@featDeadlines)
		@deadlineList = sort @deadlineList;
return(@deadlineList);
}


sub showDeadlineList {

}
## returns a list of features in the TEMP directory. This indicates that the feature is current being edited.
sub getFeatInEdit {
	my @featlist = "";

		my ($week1,$week2,$week3,$week4,$week5,$week6,$week7) = getweeks(); #Gets Sunday dates. week3 is current Sunday mdd
		my @allbaseweeks = ($week1,$week2,$week3,$week4,$week5,$week6,$week7);

	my $baseFolder = "$FeatFolder/Temp";
	my @allsteps = getstatelist();
			foreach my $step (@allsteps) {
				my $checkfolder = "$baseFolder/$step/";
					if (-d $checkfolder) {
					opendir(DIR, $checkfolder);
					my @files = readdir DIR;
				    closedir(DIR);
					    foreach (@files) {
							if (($_ =~ /^\./m) || ($_ eq "")) {
							next;
							}
							else {
							my $file_modTime = getFileStats("$baseFolder/$week/$step/$_|$file_modTime");
							my $addthis = "$_|$step|$baseFolder/$step/$_";
							 @featlist = (@featlist,$addthis);
							}
		 				 }
		 			 }
			}
return(@featlist);
}
sub getSpecialsInEdit {
	my $specialName = $_[0];
	my @featlist = "";

		my ($week1,$week2,$week3,$week4,$week5,$week6,$week7) = getweeks(); #Gets Sunday dates. week3 is current Sunday mdd
		my @allbaseweeks = ($week1,$week2,$week3,$week4,$week5,$week6,$week7);

	my $baseFolder = "$FeatFolder/Temp";
	my @allsteps = getstatelist();
			foreach my $step (@allsteps) {
				my $checkfolder = "$baseFolder/$step/";
					if (-d $checkfolder) {
					opendir(DIR, $checkfolder);
					my @files = readdir DIR;
				    closedir(DIR);
					    foreach (@files) {
							if (($_ =~ /^\./m) || ($_ eq "")) {
							next;
							}
							else {
							my $file_modTime = getFileStats("$baseFolder/$week/$step/$_|$file_modTime");
							my $addthis = "$_|$step|$baseFolder/$step/$_";
							 @featlist = (@featlist,$addthis);
							}
		 				 }
		 			 }
			}
return(@featlist);
}


#### MARKUP ROUTINES.

## Wraps all lines to 180 characters at most. Lines in VMS cannot exceed 200+ characters. 180 is used as a safe gaurd.
sub make180 {
##  $_[0] should be text
my $checkstring = $_[0];
#$checkstring =~ s/\R*$/\<ep\>\n/;
#$checkstring =~ s/\<ep\>\<ep\>/\<ep\>/g;
#my $wrapper = Text::Wrapper->new(columns => 180, body_start => ' ');
my $wrapper = Text::Wrapper->new(wrap_after => '', columns => 180);

my $value180 = $wrapper->wrap($checkstring);
chomp($value180);
$value180 =~ s/\n\s*/ \n/g;
#$value180 =~ s/ \n / \n/g;
return($value180);
}

### NOT used #####
sub searchandreplace {
use Tie::File;
$file = $_[0];
tie @records, 'Tie::File', $file;
	foreach ( @records ) {
		s/  / /g; #find more than one space together replace with single space
		#s/\<2\>\<ep\>\n/\<ep\>\n\<2\>/g; # replace all newlines with <EP> newline
		s/\n+/\n/g; # replace multiple newlines, repalce with just one
		}
untie @records;
return 1;
}

### Uploads feature file to the VMS system
### This is currently set up in test mode to post to Larry Gonyea's home directory.

sub uploadFeatureTEST {
use Net::FTP;
	my $outfilename = $_[0];
	my $server = "becky.tmsgf.trb";
	my $user = "jason.gifford";
	my $pass = "jason.gifford";
	my $init = "";	#supports only one level
	my $path = "";
	#my $uploadname = "$_";

	my $ftp = Net::FTP->new("$server", Debug => 0, Passive => 0);
	$ftp->login("$user","$pass");
#	$ftp->ascii();
	$ftp->binary();
	#$ftp->cwd("BECKY_D2:[PCSA.FILES.ELECFEAT.WORK.WIRE2]");
	#$ftp->cwd("DNFS1:[200301]");
	$ftp->cwd("OPDISK:[USERS.OPERATIONS.jason.gifford.FEATURES]");
	$ftp->put("$outfilename") or die "Upload of ${outfilename} failed";

	$ftp->quit;
	#print "$server $user $pass $init $path $uploadname\n";
	return 1;
}

sub uploadXMLFEAT {
use Net::FTP;
	my $outfilename = $_[0];
	my $server = "ftp1.tmsgf.trb";
	my $user = "tms123gf";
	my $pass = "SEC428ur";
	my $init = "";	#supports only one level
	my $path = "";
	#my $uploadname = "$_";

	my $ftp = Net::FTP->new("$server", Debug => 0, Passive => 0);
	$ftp->login("$user","$pass");
#	$ftp->ascii();
	$ftp->binary();
	#$ftp->cwd("BECKY_D2:[PCSA.FILES.ELECFEAT.WORK.WIRE2]");
	#$ftp->cwd("DNFS1:[200301]");
	$ftp->cwd("/glen_prod/features/xmlf");
	$ftp->put("$outfilename") or die "Upload of ${outfilename} failed";

	$ftp->quit;
	#print "$server $user $pass $init $path $uploadname\n";
	return 1;
}

sub uploadFeatureLIVE {
use Net::FTP;
	my $outfilename = $_[0];
	my $server = "backend3.tmsgf.trb";
	my $user = "printpro";
	my $pass = "1print2";
	# Had server problems to commenting out 
	# code below which is replaced above
	#my $server = "becky.tmsgf.trb";
	#my $user = "printpro";
	#my $pass = "printpro";
	my $init = "";	#supports only one level
	my $path = "";
	#my $uploadname = "$_";

	my $ftp = Net::FTP->new("$server", Debug => 0, Passive => 0);
	$ftp->login("$user","$pass");
	#$ftp->ascii();
	$ftp->binary();
   #$ftp->cwd("OPDISK:[USERS.OPERATIONS.jason.gifford.FEATURES]");
	$ftp->cwd("/200301");
#	$ftp->cwd("BECKY_D2:[PCSA.FILES.ELECFEAT.WORK.WIRE2]");
	$ftp->put("$outfilename") or die "Upload of ${outfilename} failed";

	$ftp->quit;
	#print "$server $user $pass $init $path $uploadname\n";
	return 1;
}
sub uploadVoomPhotos {
use Net::FTP;
	my $outfilename = $_[0];
	my $voomDate = $_[1];
#	my $server = "becky.tmsgf.trb";
	my $server = "voom.tmsgf.trb";
#	my $user = "printpro";
#	my $pass = "printpro";
	my $user = "xmlfeat";
	my $pass = "xmlfeat";
	my $init = "Web_Version/$voomDate";	#supports only one level
	my $path = "";
	my @fileParts = split "/",$outfilename;
	my $voomuploadname = "$fileParts[-1]";
#	my $macFile = "/Library/WebServer/Documents/Images/macTMP/$fileParts[-1]";
#	copy("$outfilename","$macFile") or die "File $outfilename couldn't copy to $macFile<br>\n";
#	print "$err\n";

#Upload PC directory
	my $ftp = Net::FTP->new("$server", Debug => 0, Passive => 0);
	$ftp->login("$user","$pass");
	#$ftp->ascii();
	$ftp->binary();
	$ftp->cwd("$init");
	$ftp->put("$outfilename","$voomuploadname") or die "Upload of $outfilename as $voomuploadname failed";
	$ftp->quit;
	return 1;
}

sub uploadPhotos {
use Net::FTP;
	my $outfilename = $_[0];
#	my $server = "becky.tmsgf.trb";
	my $server = "ftp1.tmsgf.trb";
#	my $user = "printpro";
#	my $pass = "printpro";
	my $user = "features";
	my $pass = "0feats2";
	my $init = "";	#supports only one level
	my $path = "";
	my @fileParts = split "/",$outfilename;
#	my $macFile = "/Library/WebServer/Documents/Images/macTMP/$fileParts[-1]";
#	copy("$outfilename","$macFile") or die "File $outfilename couldn't copy to $macFile<br>\n";
#	print "$err\n";
	my $uploadname = "$fileParts[-1].bin";
	my $pcuplaodname = "$fileParts[-1]";
	my $ftp = Net::FTP->new("$server", Debug => 0, Passive => 0);
	$ftp->login("$user","$pass");
	#$ftp->ascii();
	$ftp->binary();
	$ftp->cwd("mac");
#	$ftp->cwd("NFSDISK:[200301]");
#	$ftp->cwd("BECKY_D2:[PCSA.FILES.ELECFEAT.WORK.WIRE2]");
	#$ftp->put("$outfilename","$uploadname") or die "Upload of $macFile as ${uploadname} failed";
	$ftp->quit;

#Upload PC directory
	my $ftp = Net::FTP->new("$server", Debug => 0, Passive => 0);
	$ftp->login("$user","$pass");
	#$ftp->ascii();
	$ftp->binary();
	$ftp->cwd("pc");
	$ftp->put("$outfilename","$pcuplaodname") or die "Upload of $outfilename as ${pcuplaodname} failed";
	$ftp->quit;
	return 1;
}

sub uploadZipPhotos {
use Net::FTP;
	my $outfilename = $_[0];
#	my $server = "becky.tmsgf.trb";
	my $server = "ftp1.tmsgf.trb";
#	my $user = "printpro";
#	my $pass = "printpro";
	my $user = "features";
	my $pass = "0feats2";
	my $init = "";	#supports only one level
	my $path = "";
	my @fileParts = split("/",$outfilename);
	my $uploadname = "$fileParts[-1]";

	my $ftp = Net::FTP->new("$server", Debug => 0, Passive => 0);
	$ftp->login("$user","$pass");
	#$ftp->ascii();
	$ftp->binary();
	$ftp->cwd("mac");
#	$ftp->cwd("NFSDISK:[200301]");
#	$ftp->cwd("BECKY_D2:[PCSA.FILES.ELECFEAT.WORK.WIRE2]");
	$ftp->put("$outfilename","$uploadname") or die "Upload of ${outfilename} as $uploadname failed";
	$ftp->quit;

#Upload PC directory
	my $ftp = Net::FTP->new("$server", Debug => 0, Passive => 0);
	$ftp->login("$user","$pass");
	#$ftp->ascii();
	$ftp->binary();
	$ftp->cwd("pc");
#	$ftp->cwd("NFSDISK:[200301]");
#	$ftp->cwd("BECKY_D2:[PCSA.FILES.ELECFEAT.WORK.WIRE2]");
	$ftp->put("$outfilename","$uploadname") or die "Upload of ${outfilename} as $uploadname failed";
	$ftp->quit;

	#print "$server $user $pass $init $path $uploadname\n";
	return 1;
}


### Returns the last modified value of a given value.
### time is converted from epoch time to a readable time format.
sub getFileStats {
	my $thisFile = $_[0];
	my $modtime = int((stat($thisFile))[9]);
	my $lastAccessTime = int((stat($thisFile))[8]);
	my @daysOfWeek = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
	my @shortdaysOfWeek = qw( Sun Mon Tue Wed Thu Fri Sat );
	my @monthsOfYear = qw( January Febuary March April May June July August September October November December );
	my @shortmonthsOfYear = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
	my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
	(my $second, my $minute, my $hour, my $day, my $mm, my $year, my $weekDay, my $dayOfYear, $IsDST) = localtime($modtime);
	my $weekAsWord = "$shortdaysOfWeek[$weekDay]";
	my $monthAsWord = "$shortmonthsOfYear[$mm]";
				if ($minute < 10){
					$minute = "0$minute";
				}
			if ($f_day != $day) {
			$lastmod = "$weekAsWord, $monthAsWord $day at $hour:$minute";
			} else {
			$lastmod = "Today at $hour:$minute";
			}

	(my $second, my $minute, my $hour, my $day, my $mm, my $year, my $weekDay, my $dayOfYear, $IsDST) = localtime($lastAccessTime);
	my $weekAsWord = "$shortdaysOfWeek[$weekDay]";
	my $monthAsWord = "$shortmonthsOfYear[$mm]";
				if ($minute < 10){
					$minute = "0$minute";
				}
			if ($f_day != $day) {
			$lastaccess = "$weekAsWord, $monthAsWord $day at $hour:$minute";
			} else {
			$lastaccess = "Today at $hour:$minute";
			}

	return($lastmod);
}

### Returns current time in a readable format.
sub GetDateTime {
my $time = time;
my ($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($time);
my @daysOfWeek = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
my @shortdaysOfWeek = qw( Sun Mon Tue Wed Thu Fri Sat );

my @monthsOfYear = qw( January Febuary March April May June July August September October November December );
my @shortmonthsOfYear = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
my $weekAsWord = "$shortdaysOfWeek[$weekDay]";
my $monthAsWord = "$shortmonthsOfYear[$mm]";

				my $realMinute = "";
	#If needed add leading zero to minute
	if($minute < 10)
	{
		$realMinute = "0$minute";
	}
	else
	{
		$realMinute = "$minute";
	}

		if($hour >= 13)
	{
		$realHour = $hour - 12;
		my $AMPM = "PM";
	}
	else
	{
		$realHour = $hour;
		my $AMPM = "AM";

	}

my $nowtime = " $hour:$realMinute $AMPM - $weekAsWord, $monthAsWord $day";
return($nowtime);
}
sub GetTimeStamp {
my $time = time;
my ($second, $minute, $hour, $day, $mm, $year, $weekDay, $dayOfYear, $IsDST) = localtime($time);
my @daysOfWeek = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
my @shortdaysOfWeek = qw( Sun Mon Tue Wed Thu Fri Sat );

my @monthsOfYear = qw( January Febuary March April May June July August September October November December );
my @shortmonthsOfYear = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
my $weekAsWord = "$shortdaysOfWeek[$weekDay]";
my $monthAsWord = "$shortmonthsOfYear[$mm]";

				my $realMinute = "";
	#If needed add leading zero to minute
	if($minute < 10)
	{
		$realMinute = "0$minute";
	}
	else
	{
		$realMinute = "$minute";
	}

		if($hour >= 13)
	{
		$realHour = $hour - 12;
		my $AMPM = "PM";
	}
	else
	{
		$realHour = $hour;
		my $AMPM = "AM";

	}

my $nowtime = "$monthAsWord$day$hour$realMinute";
return($nowtime);
}
sub datetoVoomDatePhoto {
		my $xmlweek = $_[0];
		#my @datestochange = @$thisDates;
		#my @voomDates;
		my ($c_second, $c_minute, $c_hour, $c_day, $c_month, $c_year, $c_weekDay, $c_dayOfYear, $IsDST) = localtime(time);
		my $current_year = $c_year + 1900;
		my $current_month = $c_month + 1;
		my $correct_year = $current_year;
		#foreach my $xmlweek (@datestochange) {
			my $fourCharWeek;
			my $checkWeek = $xmlweek;
			my $dayOf = substr $checkWeek,1,2;
			my $thisweek = substr $checkWeek,0,1;
			if (($c_month < 2) && (($checkWeek =~ /^[9]/) || ($checkWeek =~ /^[n]/) || ($checkWeek =~ /^[d]/) || ($checkWeek =~ /^[o]/))) {
				$correct_year = $current_year -1;
			}
			if ($checkWeek =~ /^d/) {
				$fourCharWeek = "12$dayOf";
			} elsif ($checkWeek =~ /^o/) {
				 $fourCharWeek = "10$dayOf";
	  		} elsif ($checkWeek =~ /^n/) {
				 $fourCharWeek = "11$dayOf";
			} else {
		#if ($thisweek =~ /^[1-9]/) {
	 		 $fourCharWeek = "0$xmlweek";
			}
		my $xml_withyear = "$correct_year$fourCharWeek";
		#@voomDates = (@voomDates,$xml_withyear);
		#}
return($xml_withyear);
}

sub showFinder {
my $title = $_[0];
my $lang = $_[1];
#print "Searching for $title in the language $lang\n";
($mday,$mon,$year) = (localtime)[3..5];
$ymd      = sprintf( "%04d%02d%02d",$year+1900,$mon+1,$mday );

$filename = "/Library/WebServer/ONXML/on_tv_advance_planner.xml";
#$title    = '21 jum';

$parser   = XML::LibXML->new();
$doc      = $parser->parse_file( $filename );
$xpc      = XML::LibXML::XPathContext->new( $doc );
$query    = "//events/event/progTitle";
@nodes    = $xpc->findnodes($query);
my @results;

foreach  $nodes ( @nodes ) {
	$prog       = $nodes->textContent;
	 my $lcprog = lc($prog);
	 my $lctitle = lc($title);
	 #print "$lcprog<br>";
	if ( $lcprog =~ /$lctitle/i ) {
    	my $progArea    = $nodes->parentNode;
    	my @idTag       = $progArea->getElementsByTagName( 'TMSId' );
    	my @idValue     = $idTag[0]->textContent;
    	my @AirDateTag  = $progArea->getElementsByTagName( 'airDate' );
  		my $AiringY  =  $AirDateTag[0]->textContent;
  		#my $AiringM =  $AirDateTag[1]->textContent;
  		#my $AiringD = $AirDateTag[2]->textContent;
		my @descTag     = $progArea->getElementsByTagName( 'description' );
    	my $description = $descTag[0]->textContent;
		my @AiringDate = split " ", $AiringY;
		my $AirDate = "$AiringDate[1]\/$AiringDate[2]\/$AiringDate[0]";

    	if ( $description eq "" ) {
    		$description  = 'No Description Available.'
    	}

        my $completeId    = join ( '=', 'TMS ID', $idValue[0] );
	    my $completeData  = join ( '|', $prog, $completeId, $description, $AirDate);

	    push ( @results, $completeData );
    }
}

#print join ( "\n", @results ), "\n";
return(@results);
}

sub OTTshowLister {
my $title = $_[0];
my $lang = $_[1];
my @OTTlist = ("AMZONOV","HULUOV","NETOV");
#print "Searching for $title in the language $lang\n";
($mday,$mon,$year) = (localtime)[3..5];
$ymd      = sprintf( "%04d%02d%02d",$year+1900,$mon+1,$mday );
my $completeData;
$filename = "/Library/WebServer/FF2/ONXML/on_tv_advance_planner.xml";
#$title    = '21 jum';

$parser   = XML::LibXML->new();
$doc      = $parser->parse_file( $filename );
$xpc      = XML::LibXML::XPathContext->new( $doc );
$query    = "//events/event/network";
@nodes    = $xpc->findnodes($query);
my @results;

foreach  $nodes ( @nodes ) {
	$prog       = $nodes->textContent;
	 my $lcprog = lc($prog);
	 my $lctitle = lc($title);
	# print "Looking for $lcprog in $lctitle<br>";
	if ($prog ~~ @OTTlist ) {
	#print $prog;
    	my $progArea    = $nodes->parentNode;
    	#my @idTag       = $progArea->getElementsByTagName( 'TMSId' );
    	#my @idValue     = $idTag[0]->textContent;
      	my @titleTag       = $progArea->getElementsByTagName( 'progTitle' );
    	my $titleValue     = $titleTag[0]->textContent;
  		my @AirDateTag  = $progArea->getElementsByTagName( 'airDate' );
  		my $AiringY  =  $AirDateTag[0]->textContent;
      	my @AiringDate = split " ", $AiringY;
		my $AirDate = "$AiringDate[1]\/$AiringDate[2]\/$AiringDate[0]";
		my @episodeTag       = $progArea->getElementsByTagName( 'epiTitle' );
    	my $episodeValue     = $episodeTag[0]->textContent;
		my @descTag     = $progArea->getElementsByTagName( 'description' );
    	my $description = $descTag[0]->textContent;

    	if ( $description eq "" ) {
    		$description  = 'No Description Available.'
    	}

       # my $completeId    = join ( '=', 'TMS ID', $idValue[0] );
        if ($prog eq "AMZONOV") { $prog = "AMAZON VIDEO"; }
        if ($prog eq "HULUOV") { $prog = "HULU"; }
        if ($prog eq "NETOV") { $prog = "NETFLIX"; }
	    $completeData  = "$completeData<strong>$prog - \"$titleValue\"</strong><p><b>Episode:</b> $episodeValue</p> <p><b>Available:</b> $AirDate</p> <p>$description</p>"

	   # push ( @results, $completeData );
    }
}

#print join ( "\n", @results ), "\n";
return($completeData);
}
sub AdvancedPlannerLookup {
my $tag = $_[0];
my $tagValue = $_[1];
my @tagValues = split "\-",$tagValue;
#my @OTTlist = ("AMZONOV","HULUOV","NETOV");
#print "Searching for $title in the language $lang\n";
($mday,$mon,$year) = (localtime)[3..5];
$ymd      = sprintf( "%04d%02d%02d",$year+1900,$mon+1,$mday );
my $completeData;
$filename = "/Library/WebServer/FF2/ONXML/on_tv_advance_planner.xml";
#$title    = '21 jum';

$parser   = XML::LibXML->new();
$doc      = $parser->parse_file( $filename );
$xpc      = XML::LibXML::XPathContext->new( $doc );
$query    = "//events/$tag";
#print "Query is $query\n";
@nodes    = $xpc->findnodes($query);
my @results;
foreach (@tagValues) {
	    	if ($_ eq "AMZONOV") { $header = "AMAZON VIDEO"; }
   	 	    if ($_ eq "HULUOV") { $header = "HULU"; }
    	    if ($_ eq "NETOV") { $header = "NETFLIX"; }
	    	my $header;
	    	$header = $_;
			$completeData = "$completeData<center><strong>$header</strong></center><br><br>";
		foreach $nodes ( @nodes ) {
		$prog       = $nodes->textContent;
		#print "$prog <br>";
		 my $lcprog = lc($prog);
		 my $lctagValue = lc($tagValue);
		#print "Looking for $prog in @tagValues<br>";
		if ($prog =~ /$_/ ) {
		#print $prog;
 		   	my $progArea    = $nodes->parentNode;
    		#my @idTag       = $progArea->getElementsByTagName( 'TMSId' );
    		#my @idValue     = $idTag[0]->textContent;
      		my @titleTag       = $progArea->getElementsByTagName( 'progTitle' );
    		my $titleValue     = $titleTag[0]->textContent;
  			my @AirDateTag  = $progArea->getElementsByTagName( 'airDate' );
  			my $AiringY  =  $AirDateTag[0]->textContent;
      		my @AiringDate = split " ", $AiringY;
			my $AirDate = "$AiringDate[1]\/$AiringDate[2]\/$AiringDate[0]";
     	 	my @networkTag       = $progArea->getElementsByTagName( 'network' );
    		my $networkTag     = $networkTag[0]->textContent;
			my @episodeTag       = $progArea->getElementsByTagName( 'epiTitle' );
    		my $episodeValue     = $episodeTag[0]->textContent;
			my @descTag     = $progArea->getElementsByTagName( 'description' );
    		my $description = $descTag[0]->textContent;

    		if ( $description eq "" ) {
    			$description  = 'No Description Available.'
    		}

     	  # my $completeId    = join ( '=', 'TMS ID', $idValue[0] );
    	    if ($networkTag eq "AMZONOV") { $networkTag = "AMAZON VIDEO"; }
   	 	    if ($networkTag eq "HULUOV") { $networkTag = "HULU"; }
    	    if ($networkTag eq "NETOV") { $networkTag = "NETFLIX"; }
		    $completeData  = "$completeData<strong>$networkTag<br>\"$titleValue\"</strong><p><b>Episode:</b> $episodeValue</p> <p><b>Available:</b> $AirDate</p> <p>$description</p><br><br>"

		   # push ( @results, $completeData );
  	  }
	}
	}
#print join ( "\n", @results ), "\n";
return($completeData);
}
sub CelebLookup {
my $tmdIDfind = $_[0];
#my @OTTlist = ("AMZONOV","HULUOV","NETOV");
 #!/usr/bin/perl
#my @OTTlist = ("AMZONOV","HULUOV","NETOV");
#print "Searching for $tmdIDfind IDs\n";
($mday,$mon,$year) = (localtime)[3..5];
$ymd      = sprintf( "%04d%02d%02d",$year+1900,$mon+1,$mday );
my $completeData;
#$title    = '21 jum';
$filename     = "/Library/WebServer/FF2/ONXML/fancyCelebrity.xml";
$onFilename     = "/Library/WebServer/FF2/ONXML/on_celeb.xml";

$parser       = XML::LibXML->new();
$doc          = $parser->parse_file( $filename );
$onDoc        = $parser->parse_file( $onFilename );
$onXpc        = XML::LibXML::XPathContext->new( $onDoc );
$onQuery      = "//TMSIds/TMSId[contains(., '$tmdIDfind')]";
#@onNodes      = $onXpc->findnodes($onQuery);
my @results;
my @allNames;
#my $totalFinds = scalar(@onNodes);
#my $personCount = 0;
#print "There are $totalFinds Celebs associated with ID $tmdIDfind\n";

foreach  my $onNodes ( $onXpc->findnodes($onQuery) ) {
		$personCount++;
		my $tmsID = $onNodes->textContent;

		my $otmsIDNode      = $onNodes->parentNode;
		my $oproductionNode = $otmsIDNode->parentNode;
		my $omediaNode      = $oproductionNode->parentNode;
		my $opersonNode     = $omediaNode->parentNode;
		my @oPersonName     = $opersonNode->getElementsByTagName( 'personNames' );

		foreach  $oPersonName ( @oPersonName ) {
			my $olName;
			my $omName;
			my @ofirstName   = $oPersonName->getElementsByTagName( 'first' );
			my @omiddleName  = $oPersonName->getElementsByTagName( 'middle' );
			my @olastName    = $oPersonName->getElementsByTagName( 'last' );
			my $ofName       = $ofirstName[0]->textContent;
			my @ofullName    = $ofName;

			if ( scalar (@omiddleName) > 0 ) {
				$omName = $omiddleName[0]->textContent;
				push ( @ofullName, $omName );
			 }

			 if ( scalar (@olastName) > 0 ) {
				$olName = $olastName[0]->textContent;
				push ( @ofullName, $olName );
			 }
		#	 my $thisName = "$ofName|olName";
	 	#	my @allNames = (@allNames,$thisName);
			my $ocompleteName  = join ( ' ', @ofullName);
		###	my @production = $omediaNode->getElementsByTagName( 'production' );
			#print "Complete Name is $ocompleteName\n\n";
			#print "First: $ofName Middle: $omName Last: $olName\n";
			#push ( @results, ("$ocompleteName\n", "FILMOGRAPHY\n" ));
			#print "FILMOGRAPHY\n";
			my @production = $omediaNode->getElementsByTagName( 'production' );

			push ( @results, ("$ocompleteName\n", "FILMOGRAPHY\n" ));

			foreach  $production ( @production ) {
				my @onTitle  = $production->getElementsByTagName( 'title' );
				my $onYear   = $production->getElementsByTagName( 'year' );
				my $onCredit = $production->getElementsByTagName( 'credit' );

				foreach  $onTitle ( @onTitle ) {
					my $language    = $onTitle->getAttribute( 'lang' );
					my $goodOnTitle = $onTitle->textContent;

					if ( $language =~ 'en' || $language =~ 'es') {
						#print "Title: $goodOnTitle Year: $onYear Credits:$onCredit\n";
						push ( @results, "$goodOnTitle $onYear $onCredit\n" );
					}
				}

			}
		#print "\n\n\n";
			#if ($personCount == $totalFinds) {
			#	print "Got to the last one, now exiting\n";
			#	last;
			#}
#		foreach $thisName (@allNames) {
		#my $firstName,$lastName = split '\|',$thisName;
		#print "Looking for $ofName $olName\n";
		$xpc  = XML::LibXML::XPathContext->new( $doc );
		$query = "//NAMES/NAME/FIRST_NAME[text()='$ofName']/../LAST_NAME[text()='$olName']";
		foreach  my $nodes ( $xpc->findnodes($query) ) {
				my $lastName   = $nodes->textContent;
				my $parentName = $nodes->parentNode;
				my $firstName  = $parentName->getElementsByTagName( 'FIRST_NAME' );
				my $middleName = $parentName->getElementsByTagName( 'MIDDLE_NAME' );
				my @fullName   = ( $firstName, $lastName );

				#if ( length $middleName > 0 ) {
				#	splice @fullName, 1, 0, "$middleName";
				 #}
					my $namesNode        = $parentName->parentNode;
					my $personNode       = $namesNode->parentNode;
					my @awardNode        = $personNode->getElementsByTagName( 'AWARD' );
					my @milestoneNode    = $personNode->getElementsByTagName( 'MILESTONE' );
					my @highlightsNode   = $personNode->getElementsByTagName( 'HIGHLIGHT' );
					my @biographiesNode  = $personNode->getElementsByTagName( 'BIOGRAPHY' );

					foreach  $awardNode ( @awardNode ) {
						my $awardGroup    = $awardNode->getElementsByTagName( 'AWARD_GROUP' );
						my $awardYear     = $awardNode->getElementsByTagName( 'AWARD_YEAR' );
						my $awardResult   = $awardNode->getElementsByTagName( 'RESULT' );
						my $awardCatagory = $awardNode->getElementsByTagName( 'AWARD_CATEGORY' );
						my @projectNode   = $awardNode->getElementsByTagName( 'PROJECT_TITLE' );
						my $projectTitle  = $projectNode[0]->textContent;

						#print " AWARD: $awardGroup, $awardYear, $awardResult, $awardCatagory, $projectTitle\n";
						push ( @results, " AWARD: $awardGroup, $awardYear, $awardResult, $awardCatagory, $projectTitle\n" );
					}

					foreach  $milestoneNode ( @milestoneNode ) {
						my $beginDate    = $milestoneNode->getElementsByTagName( 'BEGIN_DATE' );
						my $thruDate     = $milestoneNode->getElementsByTagName( 'AWARD_YEAR' );
						my $description  = $milestoneNode->getElementsByTagName( 'DESCRIPTION' );

						#push ( @results, " MILESTONE:" );

						if ( length $beginDate > 0 ) {
						#	push ( @results, "$beginDate" );
						}

						if ( length $thruDate > 0 ) {
						#	push ( @results, "- $thruDate" );
						}

						#push ( @results, "$description\n" );
					}

					#print " HIGHLIGHTS:\n";
					foreach  $highlightsNode ( @highlightsNode ) {
						my $highlightText = $highlightsNode->getElementsByTagName( 'TEXT' );
						push ( @results, " HIGHLIGHT: $highlightText\n" );

					#	print " $highlightText\n";
					}

					#print " BIOGRAPHY:";
					foreach  $biographiesNode ( @biographiesNode ) {
						my $firstBio   = $biographiesNode->getElementsByTagName( 'FIRST' );
						my $secondBio  = $biographiesNode->getElementsByTagName( 'REST' );
						#print "$firstBio\n";

						push ( @results, " BIOGRAPHY: $firstBio\n" );

						if ( length $secondBio > 0 ) {
						#	push ( @results, "$secondBio\n" );
						}
					}
				}

#}
		}

}
my $completeData = join '<br>',@results;
#print join ( "\n", @results ), "\n";
return($completeData);
}
sub baselineLookup {
my $tag = $_[0];
my $tagValue = $_[1];
my @tagValues = split "\-",$tagValue;
#my @OTTlist = ("AMZONOV","HULUOV","NETOV");
#print "Searching for $title in the language $lang\n";
($mday,$mon,$year) = (localtime)[3..5];
$ymd      = sprintf( "%04d%02d%02d",$year+1900,$mon+1,$mday );
my $completeData;
$filename = "/Library/WebServer/FF2/ONXML/enhanced_celebrity.xml";
#$title    = '21 jum';

$parser   = XML::LibXML->new();
$doc      = $parser->parse_file( $filename );
$xpc      = XML::LibXML::XPathContext->new( $doc );
$query    = "//events/$tag";
#print "Query is $query\n";
@nodes    = $xpc->findnodes($query);
my @results;
foreach (@tagValues) {
	    	if ($_ eq "AMZONOV") { $header = "AMAZON VIDEO"; }
   	 	    if ($_ eq "HULUOV") { $header = "HULU"; }
    	    if ($_ eq "NETOV") { $header = "NETFLIX"; }
	    	my $header;
	    	$header = $_;
			$completeData = "$completeData<center><strong>$header</strong></center><br><br>";
		foreach $nodes ( @nodes ) {
		$prog       = $nodes->textContent;
		#print "$prog <br>";
		 my $lcprog = lc($prog);
		 my $lctagValue = lc($tagValue);
		#print "Looking for $prog in @tagValues<br>";
		if ($prog =~ /$_/ ) {
		#print $prog;
 		   	my $progArea    = $nodes->parentNode;
    		#my @idTag       = $progArea->getElementsByTagName( 'TMSId' );
    		#my @idValue     = $idTag[0]->textContent;
      		my @titleTag       = $progArea->getElementsByTagName( 'progTitle' );
    		my $titleValue     = $titleTag[0]->textContent;
  			my @AirDateTag  = $progArea->getElementsByTagName( 'airDate' );
  			my $AiringY  =  $AirDateTag[0]->textContent;
      		my @AiringDate = split " ", $AiringY;
			my $AirDate = "$AiringDate[1]\/$AiringDate[2]\/$AiringDate[0]";
     	 	my @networkTag       = $progArea->getElementsByTagName( 'network' );
    		my $networkTag     = $networkTag[0]->textContent;
			my @episodeTag       = $progArea->getElementsByTagName( 'epiTitle' );
    		my $episodeValue     = $episodeTag[0]->textContent;
			my @descTag     = $progArea->getElementsByTagName( 'description' );
    		my $description = $descTag[0]->textContent;

    		if ( $description eq "" ) {
    			$description  = 'No Description Available.'
    		}

     	  # my $completeId    = join ( '=', 'TMS ID', $idValue[0] );
    	    if ($networkTag eq "AMZONOV") { $networkTag = "AMAZON VIDEO"; }
   	 	    if ($networkTag eq "HULUOV") { $networkTag = "HULU"; }
    	    if ($networkTag eq "NETOV") { $networkTag = "NETFLIX"; }
		    $completeData  = "$completeData<strong>$networkTag<br>\"$titleValue\"</strong><p><b>Episode:</b> $episodeValue</p> <p><b>Available:</b> $AirDate</p> <p>$description</p><br><br>"

		   # push ( @results, $completeData );
  	  }
	}
	}
#print join ( "\n", @results ), "\n";
return($completeData);
}


sub SaveAdvancedPlannerLookup {
my $tag = $_[0];
my $tagValue = $_[1];
my @tagValues = split "\-",$tagValue;
#my @OTTlist = ("AMZONOV","HULUOV","NETOV");
#print "Searching for $title in the language $lang\n";
($mday,$mon,$year) = (localtime)[3..5];
$ymd      = sprintf( "%04d%02d%02d",$year+1900,$mon+1,$mday );
my $completeData;
$filename = "/Library/WebServer/FF2/ONXML/on_tv_advance_planner.xml";
#$title    = '21 jum';

$parser   = XML::LibXML->new();
$doc      = $parser->parse_file( $filename );
$xpc      = XML::LibXML::XPathContext->new( $doc );
$query    = "//events/$tag";
#print "Query is $query\n";
@nodes    = $xpc->findnodes($query);
my @results;
foreach (@tagValues) {
$completeData = "$completeData<center><strong>$_</strong></center><br>";
foreach $nodes ( @nodes ) {
	$prog       = $nodes->textContent;
	 my $lcprog = lc($prog);
	 my $lctagValue = lc($tagValue);
	#print "Looking for $prog in @tagValues<br>";
	if ($prog =~ /$_/ ) {
	#print $prog;
    	my $progArea    = $nodes->parentNode;
    	#my @idTag       = $progArea->getElementsByTagName( 'TMSId' );
    	#my @idValue     = $idTag[0]->textContent;
      	my @titleTag       = $progArea->getElementsByTagName( 'progTitle' );
    	my $titleValue     = $titleTag[0]->textContent;
  		my @AirDateTag  = $progArea->getElementsByTagName( 'airDate' );
  		my $AiringY  =  $AirDateTag[0]->textContent;
      	my @AiringDate = split " ", $AiringY;
		my $AirDate = "$AiringDate[1]\/$AiringDate[2]\/$AiringDate[0]";
      	my @networkTag       = $progArea->getElementsByTagName( 'network' );
    	my $networkTag     = $networkTag[0]->textContent;
		my @episodeTag       = $progArea->getElementsByTagName( 'epiTitle' );
    	my $episodeValue     = $episodeTag[0]->textContent;
		my @descTag     = $progArea->getElementsByTagName( 'description' );
    	my $description = $descTag[0]->textContent;

    	if ( $description eq "" ) {
    		$description  = 'No Description Available.'
    	}

       # my $completeId    = join ( '=', 'TMS ID', $idValue[0] );
        if ($networkTag eq "AMZONOV") { $networkTag = "AMAZON VIDEO"; }
        if ($networkTag eq "HULUOV") { $networkTag = "HULU"; }
        if ($networkTag eq "NETOV") { $networkTag = "NETFLIX"; }
	    $completeData  = "$completeData<strong>$networkTag<br>\"$titleValue\"</strong><p><b>Episode:</b> $episodeValue</p> <p><b>Available:</b> $AirDate</p> <p>$description</p><br>"

	   # push ( @results, $completeData );
    }
}
}
#print join ( "\n", @results ), "\n";
return($completeData);
}

sub AppleScript
{
	my($script) = shift @_;
#	print "\n$script\n";
	system("osascript -e '$script'");
}

sub zzzmountVolume
#requires volume name (parameter 1)
#optional second parameter for log file
{
	my @parameters = @_;
	my $volumeName = "$parameters[0]";
$local_mount_point='$volumeName';
$local_user='root';
$local_group='alaska';

$server_user="scripting";
$server_mountpoint="/$volumeName";
$server_ip="Macserver.tmsgf.trb";
$server_volume="$volumeName";


system ("sudo mkdir $local_mount_point");
system ("sudo chown $local_user:$local_group $local_mount_point");
system ("chmod +rwx $local_mount_point");
system ("sudo mount -t afp afp://$server_user:$server_pass@$server_ip/$server_volume $local_mount_point");
system ("diskutil -r");
}

sub mountScans {
	system("osascript -e /PerlLib/MountScans.scpt");

}
sub mountVolume
#requires volume name (parameter 1)
#optional second parameter for log file
{
	my @parameters = @_;
	my $volumeName = "$parameters[0]";
	print "Attempting to mount $volumeName\n";
	#my $volumeNameUNIX = makePathUNIX("$volumeName");
	my $mountLocal = "/Volumes/$volumeName";
	my $mountscript = "mount volume \"smb://macserver.tmsgf.trb/$volumeName\" as user name \"scripting\" with password \"alaska\"";
	#my $mountscript = "tell application \"Finder\" to mount volume \"afp://macserver.tmsgf.trb/Scans/\" as user name \"scripting\" with password \"alaska\"";
		unless(-e $mountLocal or mkdir $mountLocal) {
		die "Unable to create $directory\n";
	}
		#makesystem ("mkdir $mountLocal") or die;
#		system("$mountscript");
		AppleScript($mountscript);
}

1;
