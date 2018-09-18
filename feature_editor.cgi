#!/Users/scripting/perl5/perlbrew/perls/perl-5.24.0/bin/Perl
##########################################
#
#	by Larry Gonyea
#      Gracenote
#  The Feature_Editor script creates new features as well as opens existing features.
#  It takes information from the template file to determine the field type and field name
#  If this is opening a feature already started, it will display information from the feature within the fieldname tags and place it in the correct form fields.
#  
###############################################
use strict;
#use warnings;
use Tie::File;
use File::Copy;
use CGI;
use utf8;
use encoding 'UTF-8';
require("FF_common_func.cgi");
require("FF_web_elements.cgi");
my ($baseFEfolder,$FeatFolder) = getFilesLocal();
my ($homeIP,$systemType) = getHomeAddress();
my @statelist = getstatelist();


my $CanCopy;
my $copyTmp;
my $hasPhotos;
my ($fieldType,$fieldName,$fieldMarkup,$fieldText);
my $NotesOnTheSide = "";
my $PhotoOnTheSide = "";


my $selfPage = "http://$homeIP/cgi-bin/FE2/feature_editor.cgi";
my $homeDir = "$FeatFolder/";
my $templateDir = "$baseFEfolder/templates/";
my $specDir = "$baseFEfolder/specs/";
my $liveList = "$baseFEfolder/liveFeatList.txt";

## CGI PARAMS
my $query = new CGI;
my $thisfile = $query->param('fileLoc');
my $statParam = $query->param('status');
my $thisstory = $query->param('story');
my $viewStyle = $query->param('viewtype');
my $prevFilter = $query->param('backlink');
my $mod_time = $query->param('modtime');


my @storyparts = split(/\./,$thisstory);
my $storyname = $storyparts[0];
my $thistmp = "${storyname}.tmp";
my $featdate = $storyparts[1];

# Determines files to be used in the course of building a feature. the current feature, template file and spec file are all used.
my $specFile = "${specDir}${storyname}.spc";
my $featureFile = "$FeatFolder/Temp/$statParam/$thisstory";
my $templatefile = "${templateDir}${storyname}.tmp";


# Check the feature's spec file for specifics for the particular feature. Like if it can copy has photos and whether it's live. 

my %FeatSpecs = hashAFile($specFile);
my $checkCopy = $FeatSpecs{'copy'};
if ($checkCopy ne "") {
 $CanCopy = "TRUE";
} else {
 $CanCopy = "FALSE"; 
}
my $checkPhotos = $FeatSpecs{'photo'};
if ($checkPhotos ne "") {
	$hasPhotos = "TRUE";
} else { 
	$hasPhotos = "FALSE"; 
}
my $fieldOption;
my $FeatStatus = $FeatSpecs{'status'};
if ($FeatStatus eq "live") {
	$FeatStatus = "Live";
} else {
	$FeatStatus = "Test";
}

## BEGIN BUILDING WEBPAGE
makeHTML5type();
LoadCSS();
LoadJS();
JQfadeIn("#Content","slow");
HTMLtitle("Gracenote Feature Writer");
OpenDIV("ID","Header","");

if ($viewStyle eq "ViewOnly") {
	makeHeaderTopper();
} else {
	ClosedDIV("class","HeaderTopper","Gracenote Features Editor $systemType"); 	
}
ClosedDIV("class","HeaderLeft","$thisstory <br>Current status is $statParam.");
EndDIV();
#End of Header
# Start of Navigation Bar
OpenDIV("ID","Nav");
OpenDIV("class","NavLeft",);

if ($viewStyle eq "ViewOnly") {
#	OpenDIV("class","NavLeft",);
	print "<nav>\n";
	print "	<ul>\n";
	print "	<li><a href=\"http://$homeIP/cgi-bin/FE2/featuremanager.cgi\">Return to Main Page</a>\n";
	print "	<li><a href=\"http://$homeIP/cgi-bin/FE2/feature_editor.cgi?tmp=$templatefile&modtime=$mod_time&fileLoc=$thisfile&status=$statParam&story=$thisstory&viewtype=Edit\">Edit $thisstory</a>\n";
	##The option to Copy a feature is only available after it has been filtered. 
	if (($CanCopy eq "TRUE") && ($statParam eq "Filtered")) {
		my $CopyTo = $FeatSpecs{'copy'};
		my @copyList = split(/\,/,$CopyTo);
		foreach my $copyThis (@copyList) {
			my $copyCheck = checkforFeat("$copyThis.$featdate");
			my $copyFile = "$FeatFolder/$featdate/In Progress/$copyThis.$featdate";
			my $newFileLoc = "$FeatFolder/$featdate/Filtered/$thisstory";
			my $copyTMP = "$baseFEfolder/templates/$storyname.tmp";
			my $newfeat = "$copyThis.$featdate";
			if ($copyCheck ne "TRUE") {
				print "	<li><a href=\"http://$homeIP/cgi-bin/FE2/FF_mover.cgi?tmp=$copyTMP&fileLoc=$newFileLoc&newstate=copy&story=$newfeat\">Copy to $newfeat\</a>\n";
			} else {
				print "	<li>$newfeat already exists\n";
			}
		} #foreach @copyList {
	}
	if ($hasPhotos eq "TRUE") {
		print "	<li><a href=\"http://$homeIP/cgi-bin/FE2/featurePhotos.cgi?tmp=$specFile&fileLoc=$featdate&status=$statParam&story=$thisstory&viewtype=Edit\">Get $thisstory Photos</a>\n";
	}
	print "	</ul>\n";
	print "</nav>\n";
} else {
	print "<nav>\n";
	print "	<ul>\n";
	print "	<li><a href=\"http://$homeIP/cgi-bin/FE2/FF_mover.cgi?backlink=$prevFilter&tmp=$templatefile&oldstate=$statParam&newstate=reset&fileLoc=$featureFile&story=$thisstory\">Quit without saving</a>\n";
	print "	<li><a target=\"_blank\" href=\"http://$homeIP/cgi-bin/FE2/FCM_Backend.cgi?pageType=IDFINDER\">TMSID Lookup</a>\n";
	print "	</ul>\n";
	print "</nav>\n";
}
EndDIV();

EndDIV();

OpenDIV("ID","Container");

#If this is a new feature make a new feature with blank fields.
# if there's a default text in the TMP file, it wil add that to the correct field.
OpenDIV("ID","Content");

if ($statParam eq "new") { 

#Feature file is new and needs to be reassigned to an In Progress state.
	my $featureFile = "$FeatFolder/$featdate/In Progress/$thisstory";

ClosedDIV("class","ContentInfo","<center><h1><b>Currently editing $thisstory </b></h1></center>");
ClosedDIV("class","clearFloat","");

	print "<form id=\"Mover\" method=\"post\" action=\"http://$homeIP/cgi-bin/FE2/FF_mover.cgi\">\n";
	print "<input type=\"hidden\" name=\"backlink\" value=\"$prevFilter\">";
	print "<input type=\"hidden\" name=\"fileLoc\" value=\"$featureFile\">";
	print "<input type=\"hidden\" name=\"tmp\" value=\"$templatefile\">";
	open FH,"<:encoding(UTF-8)",$templatefile or die $!;
	my @fieldlists = <FH>;
	close(FH);

		foreach my $line (@fieldlists) {
			my @featfield = split('\|',$line);
 			my $fieldName = $featfield[0]; #Name of the field and tag within the feature.
 			my $fieldType = $featfield[1]; #The type of field to use. i.e. textarea, ckeditor, static
 			my $fieldMarkup = $featfield[2]; #The markup to be used in the filtered product. This line will also determine how the feature is previewed on the site. For example centered, bold, etc.
 			my $fieldText = $featfield[3]; #Any default text value for the field is in this slot.
 			my $fieldPlacer = $featfield[4]; #Where the field should be placed. Some examples are Sidebar (display in the sidebar) and Content (Display, but will not be filtered in the end product)
 			
 			chomp($fieldPlacer);
 			## Skip Sidebar fields until later. 
 			if ($fieldPlacer eq "SideBar") {
 				next;
 			}
 			# FieldPlacer of Content allows content in the main feature and allows us to skip it when the feature is filtered.
 			my ($fieldHeader, $FormName, $FormField, $FieldGroup);
			if ($fieldPlacer eq "Content") {
				$fieldHeader = "$fieldName (Not Filtered)";
				$FormName = "ContentAltFormName";
			 	$FieldGroup = "ContentAltForm";
				$FormField = "ContentAltFormField";
			} else {
			 	$fieldHeader = $fieldName;
			 	$FormName = "ContentFormName";
			 	$FieldGroup = "ContentForm";
				$FormField = "ContentFormField";
			}
			
			##Display the fields in a form based on the $fieldType in the template.
 		if (($fieldName ne "EOF") && ($fieldName ne "Notes") && ($fieldName ne "Photo")) {
 			if (($fieldType eq "static") && ($fieldName eq "Name")) {
 				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<input type=\"$fieldType\" size=\"100%\" name=\"$fieldName\" value='$thisstory\' readonly autofocus>");
				EndDIV();
			 } elsif ($fieldType eq "text") {
 				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				utf8::encode($fieldText);
				$fieldText = $query->escapeHTML($fieldText);
				ClosedDIV("class","$FormField","<textarea rows=\"2\" cols=\"110\" name=\"$fieldName\" spellcheck=\"true\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "shorttext") {
 				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				$fieldText = $query->escapeHTML($fieldText);
				ClosedDIV("class","$FormField","<textarea rows=\"1\" cols=\"110\" name=\"$fieldName\" spellcheck=\"true\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "ckeditor") {
 				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormField","$fieldHeader");
				ClosedDIV("class","$FormField","<textarea rows=\"15\" class=\"$fieldType\" name=\"$fieldName\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "static") {
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				$fieldText = $query->escapeHTML($fieldText);
				ClosedDIV("class","$FormField","<input type=\"text\" name=\"$fieldName\" value=\'$fieldText\' readonly>");
				EndDIV();
			}
		}
	}
	
	#Generate a view of the feature. This is the default when a feature is selected in the featuremanager. 
	# The option to edit will appear only on the view page
} elsif ($viewStyle eq "ViewOnly") {
	my @storyparts = split(/\./,$thisstory);
	my $storyname = $storyparts[0];
	my $featdate = $storyparts[1];
	my $OrigFile = "$FeatFolder/$featdate/$statParam/$thisstory";
	my $featureFile = "$FeatFolder/$featdate/$statParam/$thisstory";
	my $featPreview = MakeAPreview($templatefile,$OrigFile,$storyname);
	ClosedDIV("class","ContentEditFull","$featPreview");

	# Allows editors to recycle previously written features. This takes in the old feature and places the same tags in the same name fields into the new feature.
} elsif ($viewStyle eq "recycle") {
	ClosedDIV("class","ContentInfo","<center><h1><b>Currently editing $thisstory </b></h1></center>");
	ClosedDIV("class","clearFloat","");
	my $featureFile = "$FeatFolder/$featdate/In Progress/$thisstory";
	my $templateFile = "$baseFEfolder/templates/$thistmp";
	print "<input type=\"hidden\" name=\"fileLoc\" value=\"$featureFile\">";
	print "<input type=\"hidden\" name=\"tmp\" value=\"$templatefile\">";
	my $openXML = "$thisfile";

	$statParam = "new";
	print "<form method=\"post\" id=\"Mover\" action=\"http://$homeIP/cgi-bin/FE2/FF_mover.cgi\" accept-charset=\"utf-8\">\n";
	print "<input type=\"hidden\" name=\"fileLoc\" value=\"$featureFile\">";
	print "<input type=\"hidden\" name=\"tmp\" value=\"$templatefile\">";
		open FH, "<", $openXML; #Get 
		my @records = <FH>;
		my $allrecords = join "", @records;	
		my $fieldCheck = $allrecords;
		close FH;
		$allrecords =~  /\<$storyname\>(.*)\<\/$storyname\>/s;
		my $thisFeat = $1;

		open TH,"<:encoding(UTF-8)",$templateFile or die $!;
		my @fieldlists = <TH>;
		close(TH);

		foreach my $line (@fieldlists) {
			my @featfield = split('\|',$line);
 			my $fieldName = $featfield[0];
 			my $fieldType = $featfield[1];
 			my $fieldMarkup = $featfield[2];
 			my $fieldOption = $featfield[4];
 			chomp($fieldOption);
			if ($fieldOption eq "SideBar") {
			next; }
 			$thisFeat =~ /\<$fieldName\>(.*)\<\/$fieldName\>/s; 
			my $fieldText = $1;
			
			if ($fieldCheck !~ /<$fieldName>/s) {
				my $fieldText = "";
			}
 			my ($fieldHeader, $FormName, $FormField, $FieldGroup);
			if ($fieldOption eq "Content") {
				$fieldHeader = "$fieldName (Not Filtered)";
				$FormName = "ContentAltFormName";
			 	$FieldGroup = "ContentAltForm";
				$FormField = "ContentAltFormField";
			} else {
			 	$fieldHeader = $fieldName;
			 	$FormName = "ContentFormName";
			 	$FieldGroup = "ContentForm";
				$FormField = "ContentFormField";
			}

 		if (($fieldName ne "EOF") && ($fieldName ne "Notes") && ($fieldName ne "Photo")) {
 			if (($fieldType eq "static") && ($fieldName eq "Name")) {
 				#$fieldText = $query->escapeHTML($fieldText);
							$fieldText =~ s/\n/\<br\>/g;
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<input type=\"text\" rows=\"1\" cols=\"200\" name=\"$fieldName\" value=\'$thisstory\' readonly autofocus>");
				EndDIV();
			 } elsif ($fieldType eq "shorttext") {
 				utf8::encode($fieldText);
				#$fieldText = $query->escapeHTML($fieldText);
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<textarea rows=\"1\" cols=\"110\" name=\"$fieldName\" spellcheck=\"true\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "text") {
			 	#utf8::encode($fieldText);
				#$fieldText = $query->escapeHTML($fieldText);
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<textarea rows=\"2\" cols=\"110\" name=\"$fieldName\" spellcheck=\"true\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "ckeditor") {
				$fieldText =~ s/\n/\<br\>/g;
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","ContentCKField","<textarea class=\"ckeditor\" name=\"$fieldName\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "static") {
				#$fieldText = $query->escapeHTML($fieldText);
 				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<textarea readonly rows=\"2\" cols=\"110\" name=\"$fieldName\">$fieldText</textarea>");
				EndDIV();
			}
		}
	}

#If this is not a new feature, this opens and existing feature.
# This will move the feature to the TEMP area then place each tagged section into the matching for field. 
# At this point, the default text is not grabbed from within the TMP file, it has already been written to the feature. Any changes to the default text
#       Should be reflected when it's reopened. 
#  Here we also call the mover script to take the correct action based on the step selected.

} else { 

ClosedDIV("class","ContentInfo","<b>Currently editing $thisstory</b>");
ClosedDIV("class","clearFloat","");

	print "<form id=\"Mover\" method=\"post\" action=\"http://$homeIP/cgi-bin/FE2/FF_mover.cgi\" accept-charset=\"utf-8\">\n";
	my @storyparts = split(/\./,$thisstory);
	my $storyname = $storyparts[0];
	my $featdate = $storyparts[1];
	my $OrigFile = "$FeatFolder/$featdate/$statParam/$thisstory";
	my $featureFile = "$FeatFolder/Temp/$statParam/$thisstory";
	move($OrigFile,$featureFile);
	print "<input type=\"hidden\" name=\"backlink\" value=\"$prevFilter\">";
	print "<input type=\"hidden\" name=\"fileLoc\" value=\"$featureFile\">";
	print "<input type=\"hidden\" name=\"tmp\" value=\"$templatefile\">";
		open FH, "<:encoding(UTF-8)", $featureFile; #Get existing feature and put all together to grab text between name tags
		my @records = <FH>;
		my $allrecords = join "", @records;	
		my $fieldCheck = $allrecords;
		close FH;
	open TH,"<:encoding(UTF-8)",$templatefile or die $!;
	my @fieldlists = <TH>;
		close(TH);

		foreach my $line (@fieldlists) {
			my $fieldHeader = "";
			my @featfield = split('\|',$line);
 			my $fieldName = $featfield[0];
 			my $fieldType = $featfield[1];
 			my $fieldMarkup = $featfield[2];
 			my $fieldOption = $featfield[4];
 			chomp($fieldOption);
			if ($fieldOption eq "SideBar") {
			next; }
 			$allrecords =~ /\<$fieldName\>(.*)\<\/$fieldName\>/s; 
			my $fieldText = $1;
			
			if ($fieldCheck !~ /<$fieldName>/s) {
				my $fieldText = "";
			}

 			my ($fieldHeader, $FormName, $FormField, $FieldGroup);
			if ($fieldOption eq "Content") {
				$fieldHeader = "$fieldName (Not Filtered)";
				$FormName = "ContentAltFormName";
			 	$FieldGroup = "ContentAltForm";
				$FormField = "ContentAltFormField";
			} else {
			 	$fieldHeader = $fieldName;
			 	$FormName = "ContentFormName";
			 	$FieldGroup = "ContentForm";
				$FormField = "ContentFormField";
			}

 		if (($fieldName ne "EOF") && ($fieldName ne "Notes") && ($fieldName ne "Photo")) {
 			if (($fieldType eq "static") && ($fieldName eq "Name")) {
 				$fieldText = $query->escapeHTML($fieldText);
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<input type=\"text\" rows=\"1\" cols=\"200\" name=\"$fieldName\" value=\'$thisstory\' readonly autofocus>");
				EndDIV();
			 } elsif ($fieldType eq "shorttext") {
 				utf8::encode($fieldText);
				$fieldText = $query->escapeHTML($fieldText);
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<textarea rows=\"1\" cols=\"110\" name=\"$fieldName\" spellcheck=\"true\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "text") {
			 	utf8::encode($fieldText);
				$fieldText = $query->escapeHTML($fieldText);
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<textarea rows=\"2\" cols=\"110\" name=\"$fieldName\" spellcheck=\"true\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "ckeditor") {
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","ContentCKField","<textarea class=\"ckeditor\" name=\"$fieldName\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "static") {
				$fieldText = $query->escapeHTML($fieldText);
 				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<textarea readonly rows=\"2\" cols=\"110\" name=\"$fieldName\">$fieldText</textarea>");
				EndDIV();
			} elsif ($fieldType eq "old" && $fieldName ne "") { # This is to show old fields that have been replace but you still want to view what they may have had in them. #
			 	utf8::encode($fieldText);
				$fieldText = $query->escapeHTML($fieldText);
				OpenDIV("class","$FieldGroup");
 				ClosedDIV("class","$FormName","$fieldHeader");
				ClosedDIV("class","$FormField","<textarea rows=\"2\" cols=\"110\" name=\"$fieldName\" spellcheck=\"true\">$fieldText</textarea>");
				EndDIV();}
		}
	}
} #end open existing feature

ClosedDIV("class","ContentInfoFoot","End of $thisstory");

EndDIV();
OpenDIV("ID","Sidebar");
	my @storyparts = split(/\./,$thisstory);
	my $storyname = $storyparts[0];
	my $featdate = $storyparts[1];

if ($viewStyle eq "ViewOnly") {
	my $OrigFile = "$FeatFolder/$featdate/$statParam/$thisstory";
	MakeASideBar($templatefile,$OrigFile,$storyname,"view");
	
} else {

	my $oldstate = $statParam;
	ClosedDIV("class","SidebarTitle","Save and change status to Feature");
	OpenDIV("class","SidebarGroup");
	print "<input type=\"hidden\" name=\"oldstate\" form=\"Mover\" value=\"$oldstate\">";
	my $statelist = makeStateRadio($statParam);
	print "$statelist";
	ClosedDIV("class","SidebarChoice","<input type=\"submit\" form=\"Mover\" name=\"actionDo\" value=\"Submit $thisstory\">");
	EndDIV();

	###  makes Sidebar from template. Parts labeled SideBar in the template are displayed here.
	my $featureFile = "$FeatFolder/Temp/$statParam/$thisstory";
	MakeASideBar($templatefile,$featureFile,$storyname,"edit");

}
print "</form>\n";

EndDIV();
EndDIV();

EndDIV();

HTMLend();