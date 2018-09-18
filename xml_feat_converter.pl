#!/Users/scripting/perl5/perlbrew/perls/perl-5.24.0/bin/Perl
##########################################
#
#	by Larry Gonyea
#      TMS
#   Common functions used by many scripts for the Features Editor Site.
#
#############################

use strict;
use warnings;
use Tie::File;
#use XML::Simple;
#use Data::Dumper;
#require("/Library/WebServer/CGI-Executables/FE2/FF_common_func.cgi");
my $baseFEfolder = "/Library/WebServer/CGI-Executables/FE2";
my $FeatFolder = "/Library/WebServer/FF2";
my ($baseFEfolder,$FeatFolder) = getFilesLocal();
my ($homeIP,$systemType) = getHomeAddress();
my ($c_second, $c_minute, $c_hour, $c_day, $c_month, $c_year, $c_weekDay, $c_dayOfYear, $IsDST) = localtime(time);
my $current_year = $c_year + 1900;
my $current_month = $c_month + 1;
#print "$current_year\n";
## For local machine
#my $baseFEfolder = "/Perl";
#my $FeatFolder = "/Perl/FF2";
##
my $templateDir = "$baseFEfolder/xmlTemplates/";
my $xmlDir = "$FeatFolder/xmlData/";
#my $baseFolder = "/Perl";
#my $templateFolder = "$baseFolder/xmlTemplates";
my ($week1,$week2,$week3,$week4,$week5,$week6,$week7) = getweeks(); 
my @allbaseweeks = ($week1,$week2,$week3,$week4,$week5,$week6,$week7);
#my $week1 = "517";
my $getstep = "Filtered";
my @xmlfeatlist;
my @xmltmplist;
				my @allFeatFolders;
					opendir(DIR, $FeatFolder);
					my @files = readdir DIR;
				    closedir(DIR);
					    foreach (@files) {
							if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
							next;
							} 
							else {
							#print "$_\n";
								 if ($_ =~ "^[1-9,o,d,n]") {
							 	 	@allFeatFolders = (@allFeatFolders,$_);
							 	}
							}  
		 				 }

#foreach my $thisweek (@allbaseweeks) {
foreach my $thisweek (@allFeatFolders) {
	my $featureFolder = "$FeatFolder/$thisweek/$getstep";
	#my $featureFolder = "$baseFolder/$week1/$getstep/";
	# get a list of all feature in the filtered folder
					my @xmlfeatlist;
					if (-d $featureFolder) {
					opendir(DIR, $featureFolder);
					my @files = readdir DIR;
				    closedir(DIR);
					    foreach (@files) {
							if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
								next;
							} 
								else {
								#print "$_\n";
								@xmlfeatlist = (@xmlfeatlist,$_);
							}  
			 				 }
		 			 }
	##### get list of templates to tell what files to convert to XML
					my @xmltmplist;
					if (-d $templateDir) {
					opendir(DIR, $templateDir);
					my @TemplateFiles = readdir DIR;
				    closedir(DIR);
					    foreach (@TemplateFiles) {
							if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
							next;
							} 
							else {
							#print "$_\n";
							 @xmltmplist = (@xmltmplist,$_);
							}  
		 				 }
		 			 }
	############
	my $correct_year = $current_year;
	my $fourCharWeek;
	my $checkWeek = $thisweek;
	my $dayOf = substr $checkWeek,1,2; #skips the first letter or number, exp. 410, d12 for file extension
	#print "__${thisweek}__\n\n";
	if ($checkWeek =~ /^[9]/) || ($checkWeek =~ /^[n]/) || ($checkWeek =~ /^[d]/) || ($checkWeek =~ /^[o]/) && (($current_month == 01) || ($current_month == 02)){
		$correct_year = $current_year -1; #The problem!
	}
	if(($checkWeek =~ /^[1]/) || ($checkWeek =~ /^[2]/) && (($current_month == 11) || ($current_month == 12)) {
		$correct_year = $current_year +1;
	}
	if ($checkWeek =~ /^d/) {
		$fourCharWeek = "12$dayOf";
	 } elsif ($checkWeek =~ /^o/) {
		 $fourCharWeek = "10$dayOf";
	  } elsif ($checkWeek =~ /^n/) {
		 $fourCharWeek = "11$dayOf";
	} else {
		#if ($thisweek =~ /^[1-9]/) {
	 	 $fourCharWeek = "0$thisweek"; 
	}
	
	my $xml_withyear = "$thisweek$correct_year";
	my $xmlFile = "${xmlDir}$correct_year/features$fourCharWeek$correct_year.xml";
	open XMLOUT,">",$xmlFile;
	print XMLOUT "\<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n";
	print XMLOUT "<features>\n";
	# loop through template files. Try to match up with a feature that exists
	foreach my $xmlTempFile (@xmltmplist) {
		#print "$xmlTempFile\n";
		my @storyparts = split('\.',$xmlTempFile);
		my $featName = $storyparts[0];
		my $thisTemplate = "$templateDir$xmlTempFile";
		my $findFeat = "$featureFolder/$featName.$thisweek";

		#print "Looking for $findFeat\n";
		#print "Looking at template $featName for $thisweek\n";
		my $foundFeat = "FALSE";
		# loop though the existing features and find the one that matches the xml template
		foreach (@xmlfeatlist) {
			my @featparts = split('\.',$_);
			my $thisFeat = $featparts[0];
			if ($featName eq $thisFeat) {
				#print "Feature is $featName looking for $thisFeat\n";
				#my $featTags;
				$foundFeat = "TRUE";
				open FH, $findFeat; #Get existing feature and put all together to grab text between name tags
				my @records = <FH>;
				close FH;
				my $allrecords = join "", @records;	
				#print "Found files \n $allrecords\n";
				#my @featureTags = arrayFile($findFeat);
				my @xmlTags = arrayFile("$thisTemplate");
				foreach (@xmlTags) {
					my $wholeFeat = $allrecords;
					my @tagger = split('\|',$_);
					my $tagName = $tagger[0];
					my $tagType = $tagger[1];
					if (!defined($tagType)) {
					 	my $tagType = "None";
					}
					#print "tag name is $tagName\n tag type is $tagType\n";
					if (($tagType eq "Start") || (lc($tagType) eq "group")) {
						print XMLOUT "<$tagName>"; 
					} elsif ($tagType eq "End") {
						print XMLOUT "</$tagName>\n";
					} elsif (lc($tagType) eq "ungroup") {
						print XMLOUT "</$tagName>";	
					} elsif ($tagName eq "EP") { 
							print XMLOUT "\n";
					} else {
						#print "Looking for text in $tagName\n";
						$wholeFeat =~ /\<$tagName\>(.*)\<\/$tagName\>/; 
						my $record = $1;
						my $print_to = "";
							#print "Record is \n $record";
						my $print_to = htmltoXML($record);
						$tagName =~ s/\s//g; 
						if ($tagName =~ /^Copy/) {
							$print_to = "&#169; $print_to";
						}
						#print XMLOUT "<$tagName>\n"; 
						#chomp($record);
						if ($tagType eq "NL") {
							print XMLOUT "<$tagName>$print_to\n</$tagName>\n";
						} elsif ($tagType eq "NB") {
							print XMLOUT "<$tagName>$print_to</$tagName>";
						} else {
							print XMLOUT "<$tagName>$print_to</$tagName>\n";
						}
						#print XMLOUT "</$tagName>\n";

					}
				}
			}
		}

	if ($foundFeat eq "FALSE") {
		print XMLOUT "<$featName>\n";
		print XMLOUT "\t\t$featName.$thisweek not ready for production.\n";
		print XMLOUT "<\/$featName>\n";
	}
	}
	print XMLOUT "<\/features>\n";
	close XMLOUT;
}



sub tagFinder {
	my $tmpline = $_[0];
	my $returnTags;
	my @eachSentence = split('\. ',$tmpline);

}
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

sub	htmltoXML {
	my $tmpline = $_[0];
	my $qswitch = "start";
	#utf8::encode($tmpline);
	my %xmlConverter = (
	"\&lsquo;" => "\'",
	"\&shy;" => "",	
	"\&quot;" => "\"",
	"\&ldquo;" => "\"",
	"\&rsquo;" => "\'",
	"\&rdquo;" => "\"",
	"\&nbsp;" => " ",
	"\&iexcl;" => "&#161;",
	"\&pound;" => "&#163;",
	"\&copy;" => "&#169;",
	"¿" => "&#191;",
	"\&iquest;" => "&#191;",
	"\&Agrave;" => "&#192;",
	"À" => "\"&#192",
	"\&Aacute;" => "&#193;",
	"Á" => "&#193;",
	"\&Acirc;" => "&#194;",
	"Â" => "&#194;",
	"\&Atilde;" => "&#195;",
	"Ã" => "&#195;",
	"\&Auml;" => "&#196;",
	"Ä" => "\&#196;",
	"\&Aring;" => "&#197;",
	"Å" => "&#197;",
	"\&AElig;" => "&#198;",
	"Æ" => "&#198;",
	"\&Ccedil;" => "&#199;",
	"Ç" => "&#199;",
	"\&Egrave;" => "&#200;",
	"È" => "&#200;",
	"\&Eacute;" => "&#201;",
	"É" => "&#201;",
	"\&Ecirc;" => "&#202;",
	"Ê" => "&#202;",
	"\&Egrave;" => "&#200;",
	"È" => "&#200;",
	"\&Euml;" => "&#203;",
	"Ë" => "&#203;",	
	"\&Igrave;" => "&#204;",
	"Ì" => "&#204;",
	"\&Iacute;" => "&#205;",
	"Í" => "&#205;",
	"\&Icirc;" => "&#206;",
	"Î" => "&#206;",
	"\&Iuml;" => "&#207;",
	"Ï" => "&#207;",
	"\&Ntilde;" => "&#209;",
	"Ñ" => "&#209;",
	"\&Ograve;" => "&#210;",
	"Ò" => "&#210;",	
	"\&Oacute;" => "&#211;",
	"Ó" => "&#211;",
	"\&Ocirc;" => "&#212;",
	"Ô" => "&#212;",	
	"\&Ouml;" => "&#214;",
	"Ö" => "&#214;",
	"\&Ugrave;" => "&#217;",
	"Ù" => "&#217;",		
	"\&Uacute;" => "&#218;",
	"Ú" => "&#218;",					
	"\&Ucirc;" => "&#219;",
	"Û" => "&#219;",		
	"\&Uuml;" => "&#220;",
	"Ü" => "&#220;",		
	"\&Yacute;" => "&#221;",
	"Ý" => "&#221;",		
	"\&agrave;" => "&#224;",
	"à" => "&#224;",		
	"\&aacute;" => "&#225;",
	"á" => "&#225;",
	"\&acirc;" => "&#226;",
	"â" => "&#226;",
	"\&atilde;" => "&#227;",
	"ã" => "&#227;",	
	"\&auml;" => "&#228;",
	"ä" => "&#228;",
	"\&ccedil;" => "&#231;",
	"ç" => "&#231;",
	"\&egrave;" => "&#232;",
	"è" => "&#232;",		
	"\&eacute;" => "&#233;",
	"é" => "&#233;",		
	"\&ecirc;" => "&#234;",
	"ê" => "&#234;",		
	"\&euml;" => "&#235;",
	"ë" => "&#235;",		
	"\&igrave;" => "&#236;",
	"ì" => "&#236;",			
	"\&iacute;" => "&#237;",
	"í" => "&#237;",			
	"\&icirc;" => "&#238;",
	"î" => "&#238;",			
	"\&iuml;" => "&#239;",
	"ï" => "&#239;",			
	"\&ntilde;" => "&#241;",
	"ñ" => "&#241;",	
	"\&ograve;" => "&#242;",
	"ò" => "&#242;",		
	"\&oacute;" => "&#243;",
	"ó" => "&#243;",	
	"\&ocirc;" => "&#244;",
	"ô" => "&#244;",	
	"\&otilde;" => "&#245;",
	"õ" => "&#245;",	
	"\&ouml;" => "&#246;",
	"ö" => "&#246;",	
	"\&ugrave;" => "&#249;",
	"ù" => "&#249;",		
	"\&uacute;" => "&#250;",
	"ú" => "&#250;",	
	"\&ucirc;" => "&#251;",
	"û" => "&#251;",	
	"\&uuml;" => "&#252;",
	"ü" => "&#252;",	
	"\&yacute;" => "v",
	"ý" => "&#253;",	
	"\&yuml;" => "&#255;",
	"ÿ" => "&#255;",	
	"\&ndash;" => "\-",
	#"$" => "\&\#36\;",
	"&bull;" => "\&\#149\;",
	"\&#39;" => "\ʼ",
	"\&hellip;" => "\.\.\.",
	"\&mdash;" => "\-\-",
	"\<span style=\"(.*)\"\>" => "",
	"\<span style=``(.*)\'\'\>" => "",
	"\<strong style=\"(.*)\"\>" => "",
	"\<p style=``(.*)right(.*)''\>" => "",
	"\<p style=``(.*)justify(.*)''\>" => "",
	"\<\/span\>" => "",
	"\<p>" => "",
	"\<\/p\> " => "\n",
	#"\<\/p\>" => "",
	"\n+" => "\n",
	"<br>" => "\n",
	"<\/em>" => "<\/i>",
	"<em>" => "<i>",
	"<9>" => "&#169;",
	"<strong>" => "<b>",
	"</strong>" => "</b>",
	"& " => "&#38; ",
		);
	while ( my ($key, $value) = each %xmlConverter ) {
	#print "replacing $key with $value\n";
	$tmpline =~ s/$key/$value/g;
	}
	chomp($tmpline);
return($tmpline);
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

	return($weekup7,$weekup6,$weekup5,$weekup4,$weekup3,$weekup2,$weekup1,$thisweek);
}

sub getFilesLocal {
my $CGIscriptslocal = "/Library/WebServer/CGI-Executables/FE2";
my $FeatureFilesLocal = "/Library/WebServer/FF2";
return($CGIscriptslocal,$FeatureFilesLocal)
}

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
