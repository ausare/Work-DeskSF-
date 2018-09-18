#!/Users/scripting/perl5/perlbrew/perls/perl-5.24.0/bin/Perl
#use warnings;
## Larry Gonyea - Gracenote
## This script (featuremanager.cgi) is a features controller for finding and organizing Feature text and Feature photos. 
## 	This will help users navigate to viewing an existing feature or starting a new feature by passing along CGI parameters to the 
##    script feature_editor.cgi
use strict;
use Tie::File;
use File::Copy;
use CGI;
use File::Find;
use utf8;
#use encoding 'UTF-8';
require("FF_common_func.cgi");
require("FF_web_elements.cgi");
my ($baseFEfolder,$FeatFolder) = getFilesLocal();
my ($homeIP,$systemType) = getHomeAddress();
my ($week7,$week6,$week5,$week4,$week3,$week2,$week1,$weeknow) = getweeks(); 
my @allsteps = getstatelist();
my @allbaseweeks = getweeks();
my @revBaseweeks = reverse(@allbaseweeks);
my @deadlines = getFeatDeadlines();
my $currenttime = GetDateTime();
my @featInEdit = getFeatInEdit(); #makes a list of features that are in the TEMP folder indicating that the feature is being edited.

my $mysearch = "";
my $step = "";
my $weekof = "";
my $writer = "";


my @daysOfWeek = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
my @shortdaysOfWeek = qw( Sun Mon Tue Wed Thu Fri Sat );
my @monthsOfYear = qw( January Febuary March April May June July August September October November December );
my @shortmonthsOfYear = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
my $homeDir = "$FeatFolder/";
my $templateDir = "$baseFEfolder/templates/";
my $selfPage = "$homeIP/cgi-bin/FE2/featuremanager.cgi";

#pickup any CGI parameters fed to the page
my $query = new CGI;
my $pageType = $query->param('pageType');
my $mysearch = $query->param('search');
my $featsearch = $query->param('feature');
my $step = $query->param('step');
my $weekof = $query->param('weekof');
my $writer = $query->param('writer');

makeHTML5type();
LoadCSS("featman2.css");
LoadJS();
#JQfadeIn("#Content","slow");
JQtoggleComplete(".ContentCardComplete","compbutton");
JQtoggleNS(".ContentCardNS","nsbutton");
JQtoggleST(".ContentCard","stbutton");
JQtoggleNF(".SidebarHide","nfbutton");
print "</script>";

HTMLtitle("Gracenote Feature Writer");
OpenDIV("ID","Header");
makeHeaderTopper();
ClosedDIV("class","HeaderLeft","Gracenote Features Content Manager - $systemType System");
my $AllFeatList = getFileList("$baseFEfolder/templates/","No");
EndDIV();

#start the navigation bar
OpenDIV("ID","Nav");
OpenDIV("class","NavLeft",);
## Create the drop down lists for filtering features.
makeNAVbar();
EndDIV();
EndDIV();

#############
#Begin building content area based on any filters applied
OpenDIV("ID","Container");

OpenDIV("ID","Sidebar");

ClosedDIV("class","SidebarTitle","Features in Edit","These features have been opened for editing and are locked. Resetting the feature will allow editing again.");

OpenDIV("class","SidebarGroup");
my $tmpcount = 0;
my @editingList = "";
foreach my $tmpfile (@featInEdit) { 
#	return format of getFeatInEdit: "storyname|step|path";
	if ($tmpfile ne "") {
		@editingList = (@editingList, $tmpfile);
		$tmpcount++;}
	}
ClosedDIV("class","SidebarStatHeader","Features being edited: $tmpcount");
if ($tmpcount > 0) {
	foreach (@editingList) {
		if ($_ ne "") {
				my @tmppart = split('\|',$_);				
				print "<form method=\"get\" action=\"http://$homeIP/cgi-bin/FE2/FF_mover.cgi\">\n";
				print "<input type=\"hidden\" name=\"oldstate\" value=\"reset\">";
				print "<input type=\"hidden\" name=\"newstate\" value=\"reset\">";
				print "<input type=\"hidden\" name=\"fileLoc\" value=\"$tmppart[2]\">";
				print "<input type=\"hidden\" name=\"story\" value=\"$tmppart[0]\">";
				my $SideStat = "<b>$tmppart[0]</b> is open in <b>$tmppart[1]</b>.<br><input type=\"submit\" value=\"Click to Reset $tmppart[0]\">";
				#print "$SideStat";
				ClosedDIV("class","SidebarChoice",$SideStat,"$tmppart[0] is open for editing. Resetting this will feature will allow editing again, but changes will not be saved.");
				print "</form>";
		}
	}
}
EndDIV();
EndDIV();


OpenDIV("ID","Content");

## Display the options to create a new feature if selected. These are seperate 
if ($pageType eq "newFeat") {
ClosedDIV("class","ContentBoxPlain","Choose a feature in the drop down menus below to begin a new feature.<br> Note: if feature does not show in the drop down list here, then it has already been started for that week.");

foreach my $showWeek (@allbaseweeks) {
#my $showWeek = $week7;
my $weekfeatlist = getNewFeatslistoptions($showWeek);
	#		ClosedDIV("class","CardCatHead","Create a $week5 Feature");
	OpenDIV("class","ContentCardNSSH");
		ClosedDIV("class","ContentCardHead","Choose a $showWeek Feature");
	if ($weekfeatlist eq "No Features") {
			ClosedDIV("class","ContentCardBody","All Features started for $showWeek");
			ClosedDIV("class","ContentCardFooter","");
		} else {
			ClosedDIV("class","ContentCardBody","<form method=\"post\" action=\"http://$homeIP/cgi-bin/FE2/feature_editor.cgi\"><select name=\"story\">$weekfeatlist</select><input type=\"hidden\" name=\"status\" value=\"new\">");
			ClosedDIV("class","ContentCardFooter","<input type=\"submit\" value=\"Create This Feature\"></form>\n");	
		}
	EndDIV();
}

} elsif ($pageType eq "textSearch") {
	#Allow users to input text to search. This will search all current features for the text given. 
	ClosedDIV("class","ContentBoxCenterPlain","Search for text in features for the weeks of $week7, $week6, $week5, $week4, $week3, $week2, $week1 and $weeknow.<br>");
	ClosedDIV("class","ContentBoxCenterPlain","<form method=\"post\" name=\searchForm\" action=\"http://$homeIP/cgi-bin/FE2/featuremanager.cgi\"><input type=\"textarea\" rows=\"3\" name=\"search\" style=\"width:65%\" autofocus>\n");
	ClosedDIV("class","ContentBoxCenterPlain","<input type=\"submit\" value=\"Search Feature Text\"></form>\n");
} elsif ($mysearch ne "") {
	## Call the showFeatmanoptions to search all features for the $mysearch string passed by the form above in textsearch
	showFeatmanoptions("search","$mysearch");
} 
elsif (($step ne "") && ($weekof ne "")) {
	# show features for a certain step and week
	showFeatmanoptions("stepweek","$step|$weekof");
} 
elsif ($step ne "") {
	# Show all features for a certain step
	showFeatmanoptions("step","$step");
} 
elsif ($weekof ne "") {
	# show features for a particular week. 
		OpenDIV("class","ContentBoxPlain");
		ClosedDIV("class","FeatManButtons","<stbutton>Hide Started Features</stbutton>");
		ClosedDIV("class","FeatManButtons","<compbutton>Hide Completed Features</compbutton>");
		EndDIV();
	showFeatmanoptions("weekof","$weekof");
} 
	## Writer search not used any longer. This function can be completed in the Search Feature Text Menu
#elsif ($writer ne "") {
	#	showFeatmanoptions("writer","$writer");
#} 
elsif ($featsearch ne "") {
	# search all features that contain the featsearch string.  This is dictated by the drop menu option of sorting by Feature Name. 
	showFeatmanoptions("feature","$featsearch");
} 
else {
	# By default, all features are shown beginning with the furthest out week. Features that are not started are shown, but hidden.
	#	Javascript button <nsbutton> will toggle them into view. 

		OpenDIV("class","ContentBoxPlain");
		ClosedDIV("class","FeatManButtons","<nsbutton>Show Not Started Features</nsbutton>");
		ClosedDIV("class","FeatManButtons","<stbutton>Hide Started Features</stbutton>");
		ClosedDIV("class","FeatManButtons","<compbutton>Hide Completed Features</compbutton>");
		EndDIV();
		showFeatmanoptions("all","all");
}


EndDIV();
EndDIV();
HTMLend();


