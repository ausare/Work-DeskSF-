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
use CGI::Session;
use File::Find;
use utf8;
#use encoding 'UTF-8';
require("PD_common_func2.cgi");
require("PD_web_elements.cgi");
my $homeIP = "pmsgf.tmsgf.trb";
my $currenttime = GetDateTime();
my $pageMode = "";
my @daysOfWeek = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
my @shortdaysOfWeek = qw( Sun Mon Tue Wed Thu Fri Sat );
my @monthsOfYear = qw( January Febuary March April May June July August September October November December );
my @shortmonthsOfYear = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
my $selfPage = "http://$homeIP/cgi-bin/Operations/healthmonitorv2.cgi";
   my $Fname;
   my $Lname;
   my $user_dept;
   my $user_email;
   my $last_login;
   my $user_role;
   my $user_name;
#pickup any CGI parameters fed to the page
my $query = new CGI;
my $pageType = $query->param('pageType');
my $pageMode = $query->param('pageMode');
my $mysearch = $query->param('search');
my $prodType = $query->param('prodType');
my $pageStatus = $query->param('refresh');
my $screenMode = $query->param('screenMode');
my $username = $query->param('user');
my $password = $query->param('pass');
my $theCookie = $query->cookie('prod_mon');
my $switchRefresh;
if ($prodType eq "") {
	$prodType = "PRINT";
}
if ("$theCookie") {
   my @user_parts = split(",",$theCookie);
   $Fname = $user_parts[1];
   $Lname = $user_parts[2];
   $user_dept = $user_parts[3];
   $user_role = $user_parts[4];
   $user_email = $user_parts[8];
	$user_name = $user_parts[5];
  $last_login = $user_parts[7];   #print $theCookie;
} else {
	my $url = 'http://pmsgf.tmsgf.trb/cgi-bin/Operations/login.cgi';
	print $query->redirect(-location=>$url);
}
my $dbuser = "root";
my $dbpass = "alaska";
if ($prodType ne "CronacleSched") {
	$pageMode = "Monitor";
}
makeHTML5type($pageMode);
LoadCSS("operations.css");
LoadJS();

if ($screenMode ne "BIG") {
	JQfadeIn("#Content","slow");
} else {
	JQfadeIn("#ContentBig","slow");
}
JQtoggleAPhold(".APHolding","APbutton");
if (lc($pageMode) =~ /monitor/) {
	$switchRefresh = "<a href=$selfPage?pageType=$pageType&search=$mysearch&prodType=$prodType&screenMode=$screenMode&refresh=$pageStatus>Turn off Refresh</a>";
} else {
	$switchRefresh = "<a href=$selfPage?pageType=$pageType&pageMode=monitor&search=$mysearch&prodType=$prodType&screenMode=$screenMode&refresh=$pageStatus>Turn on Refresh</a>";
}
#print "</script>";

HTMLtitle("Gracenote Operations Monitor");
OpenDIV("ID","Header");
makeHeaderTopperIII("$theCookie");
ClosedDIV("class","HeaderLeft","Gracenote Operations Monitor - $currenttime");
EndDIV();
OpenDIV("ID","Container");

if ($screenMode ne "BIG") {

	#start the navigation bar
	OpenDIV("ID","Nav");
	OpenDIV("class","NavLeft",);
	makeNAVbarNEW("$user_role","$user_name");
	EndDIV();
	EndDIV();
}
#############

#if ($screenMode ne "BIG") {
#	OpenDIV("ID","Content");
#} else {
#	OpenDIV("ID","ContentBig");
#}
	  	 my @fieldsB;
	  	 my @fieldValsB;
	  	 my %fieldContentB;
	#OpenDIV("ID","flexfull");
#PRINT PRODUCTION
	#OpenDIV("ID","flexcolumn");
		#ClosedDIV("class","UserRow","PRINT PRODUCTION FLOW");
	my @genqueues = ("GENERIC_ELEC_EXT|RIPE_PRT_EXT","BACKEND_ELEC","PACKAGE|PACKAGE_SINGLE","TURBOX6_GENERIC","TURBOX2_GENERIC|TURBOX_GENERIC|TURBOXQ_GENERIC|TURBOX6ADGEN_GENERIC|TURBOX2STV_GENERIC","VERIFY_BECKY|VERIFY_NORM");
	my @ripeSystems = ("ripe01|ripe02","ripe03|ripe04","ripe05|ripe06","ripe07|ripe08|ripe09","VERIFY_BECKY|VERIFY_NORM");
	my @cronacleSystems = ("qbrwagentprod01","qbrwagentprod02","ripe01|ripe02|ripe03|ripe04|ripe05","ripe06|ripe07|ripe08|ripe09");
	my @CCEqueues2 = ("PROD_GENERIC","PROD_S3_GENERIC","ARCHIVE_GENERIC","BA4_GENERIC","PACKAGE_HY","SCIATL3","VERIFY_BECKY|VERIFY_NORM");
	my @Editqueues = ("BECKY_ESP","MAINT_BECKY_APOLLO","LHU_BECKY","LHU_NORM");
	my @maint_queues = ("MAINT_GENERIC","SYS_OPS","BECKY\$BATCH|NORM\$BATCH","REPORT_GENERIC","BACKUP_BECKY|BACKUP_NORM","STATS_BECKY|STATS_NORM","EMAIL_CLIENTDB_BECKY","USERS_BECKY|USERS_NORM");
	my @Cronacle = ("qbrwagentprod01","qbrwagentprod02","ripe01|ripe02|ripe03|ripe04|ripe05","ripe06|ripe07|ripe08|ripe09");
#if ($prodType eq "PRINT") {
if ($prodType eq "PRINT")  {
	getAlphaQGroup(@genqueues);
} elsif ($prodType eq "ELECTRONICGLEN") {
	getAlphaQGroup(@CCEqueues2);
} elsif ($prodType eq "ELECTRONIC") {
	getAlphaQGroup(@ripeSystems);
}	elsif  ($prodType eq "EDITORIAL") {
	getAlphaQGroup(@Editqueues);
}  elsif  ($prodType eq "MAINT") {
	getAlphaQGroup(@maint_queues);
}  elsif  ($prodType eq "CRONACLE") {
	getAlphaQGroup(@Cronacle);
} elsif ($prodType eq "CronacleSched") {
	OpenDIV("ID","Content");
	my $chain_filter;
	my $chainTable;
	my $sth;
	my $dbh = DBI->connect("DBI:mysql:SCHEDULED;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
	if ($pageType eq  "ELEC") {
		if ($mysearch eq "custcode") {
			$sth = $dbh->prepare("SELECT JOBID as JOBID, CUSTCODE as CLIENTID, PRODUCTLOOKUP as ProductName, SYSTEM as SYSTEM, STARTTIME as STARTTIME, JOBCHAIN as JOBCHAIN from TVSCHEDULES WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = 'SCHEDULE_RIPE_BUILD' ORDER By CUSTCODE ASC");
		} elsif ($mysearch eq "jobid") {
			$sth = $dbh->prepare("SELECT JOBID as JOBID, CUSTCODE as CLIENTID, PRODUCTLOOKUP as ProductName, SYSTEM as SYSTEM, STARTTIME as STARTTIME, JOBCHAIN as JOBCHAIN from TVSCHEDULES WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = 'SCHEDULE_RIPE_BUILD' ORDER By JOBID ASC");
		} else {
			$sth = $dbh->prepare("SELECT JOBID as JOBID, CUSTCODE as CLIENTID, PRODUCTLOOKUP as ProductName, SYSTEM as SYSTEM, STARTTIME as STARTTIME, JOBCHAIN as JOBCHAIN from TVSCHEDULES WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = 'SCHEDULE_RIPE_BUILD' ORDER By STARTTIME ASC");
		}
	} elsif ($pageType eq  "ADGENPRINT") {
		if ($mysearch eq "custcode") {
		$sth = $dbh->prepare("SELECT JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, StartTime as STARTTIME, JobChain as JOBCHAIN from MOVIESCHEDULES WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = 'ELECTRONIC_ADGEN_CHAIN' ORDER By CustomerName ASC");
		} elsif ($mysearch eq "jobid") {
		$sth = $dbh->prepare("SELECT JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, StartTime as STARTTIME, JobChain as JOBCHAIN from MOVIESCHEDULES WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = 'ELECTRONIC_ADGEN_CHAIN' ORDER By JobId ASC");
		} else {
		$sth = $dbh->prepare("SELECT JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, StartTime as STARTTIME, JobChain as JOBCHAIN from MOVIESCHEDULES WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = 'ELECTRONIC_ADGEN_CHAIN' ORDER By STARTTIME ASC");
		}
	} elsif ($pageType eq  "ADGENELEC") {
		if ($mysearch eq "custcode") {
		$sth = $dbh->prepare("SELECT JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, StartTime as STARTTIME, JobChain as JOBCHAIN from MOVIESCHEDULES WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = 'ELECTRONIC_CHAIN' ORDER By CustomerName ASC");
		} elsif ($mysearch eq "jobid") {
		$sth = $dbh->prepare("SELECT JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, StartTime as STARTTIME, JobChain as JOBCHAIN from MOVIESCHEDULES WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = 'ELECTRONIC_CHAIN' ORDER By JobId ASC");
		} else {
		$sth = $dbh->prepare("SELECT JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, StartTime as STARTTIME, JobChain as JOBCHAIN from MOVIESCHEDULES WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = 'ELECTRONIC_CHAIN' ORDER By STARTTIME ASC");
		}
	} else {
		$sth = $dbh->prepare("SELECT * FROM (Select JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, StartTime as STARTTIME, JobChain as JOBCHAIN from MOVIESCHEDULES WHERE SCHEDDATE = CURDATE() UNION ALL Select JOBID as JOBID, CUSTCODE as CLIENTID, PRODUCTLOOKUP as ProductName, SYSTEM as SYSTEM, STARTTIME as STARTTIME, JOBCHAIN as JOBCHAIN from TVSCHEDULES WHERE SCHEDDATE = CURDATE()) AS tm ORDER By STARTTIME ASC");
	}
	my @headerSizes = ("12","10","20","17","10","20","12","12","7","12");
	my @rows;
#	my $sth = $dbh->prepare("Select MOVIESCHEDULES.JobId as JOBID, MOVIESCHEDULES.CustomerName as CLIENTID, MOVIESCHEDULES.ProductName as ProductName, MOVIESCHEDULES.System as SYSTEM, MOVIESCHEDULES.JobChain as JOBCHAIN, MOVIESCHEDULES.StartTime as STARTTIME from MOVIESCHEDULES WHERE SCHEDDATE = CURDATE() ORDER By STARTTIME ASC");
	$sth->execute();
	#my @fields =  @{ $sth->{NAME_uc} };
	my @fields = ("JOBID","CUSTCODE","PRODUCT","SYSTEM","STARTTIME","JOB CHAIN","STATUS");
	my $colCount = 0;
	OpenDIV("class","ApoHeader","");
	foreach my $header (@fields) {
		ClosedDIV("class","ApoCol$headerSizes[$colCount]","$header");
		$colCount++;
	}
	EndDIV();

	while (@rows = $sth->fetchrow_array) {
		my $colCount = 0;
		my $jobStatus;
		my @lineElements = @rows;
		if ($lineElements[0] =~ m/^Job Id/) {
			OpenDIV("class","ApoHeader","");
		} elsif ($lineElements[0] !~ m/^\d/) {
			next;
		} else {
			OpenDIV("class","ApoRow","");
		}
		my $jobStatus = find_jobstatus($lineElements[0]);
		@lineElements=(@lineElements,$jobStatus);
		foreach my $element (@lineElements) {

					ClosedDIV("class","ApoCol$headerSizes[$colCount]","$element");
			#}
			$colCount++;
		}
		EndDIV();
		print "<br>";
		if ($_ =~ m/^Job Id/) {
				print "<br><hr>";
		}
	}
			print "<br>";
			print "<br>";
		EndDIV();

	$sth->finish();
	$dbh->disconnect();

} elsif ($prodType eq "CronacleProd") {
	my $dbh = DBI->connect("DBI:mysql:SCHEDULED;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
	my @headerSizes = ("10","10","20","10","10","20","12","12","7","12");
	my @fields = ("JOBID","CUSTCODE","PRODUCT","SYSTEM","COMPLETED","ELAPSEDTIME","JOB CHAIN","STATUS");
	my $sth;
	if ($pageMode eq  "ELEC") {
		$sth = $dbh->prepare("SELECT JOBID as JOBID, CUSTCODE as CLIENTID, PRODUCTLOOKUP as ProductName, SYSTEM as SYSTEM, COMPLETED as COMPLETED, ELAPSEDTIME as ELAPSEDTIME, JOBCHAIN as JOBCHAIN from tvcomplete WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = \"RIPE_BUILD\"");
	} elsif ($pageMode eq  "ADGENPRINT") {
		$sth = $dbh->prepare("SELECT JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, CompletedDate as COMPLETED, ElapsedTime as ELAPSEDTIME, JobChain as JOBCHAIN from MOVIESCOMPLETE WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = \"ELECTRONIC_ADGEN_CHAIN\"");
	} elsif ($pageMode eq  "ADGENELEC") {
		$sth = $dbh->prepare("SELECT JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, CompletedDate as COMPLETED, ElapsedTime as ELAPSEDTIME, JobChain as JOBCHAIN from MOVIESCOMPLETE WHERE SCHEDDATE = CURDATE() AND JOBCHAIN = \"ELECTRONIC_CHAIN\"");
	} else {
#		$sth = $dbh->prepare("SELECT * FROM (Select JobId as JOBID, CustomerName as CLIENTID, ProductName as ProductName, System as SYSTEM, StartTime as STARTTIME, JobChain as JOBCHAIN from MOVIESCHEDULES WHERE SCHEDDATE = CURDATE() UNION ALL Select JOBID as JOBID, CUSTCODE as CLIENTID, PRODUCTLOOKUP as ProductName, SYSTEM as SYSTEM, STARTTIME as STARTTIME, JOBCHAIN as JOBCHAIN from TVSCHEDULES WHERE SCHEDDATE = CURDATE()) AS tm ORDER By STARTTIME ASC");
	}
	my @headerSizes = ("10","10","20","10","10","20","12","12","7","12");
	my @rows;
		my $colCount = 0;
	OpenDIV("class","ApoHeader","");
	foreach my $header (@fields) {
		ClosedDIV("class","ApoCol$headerSizes[$colCount]","$header");
		$colCount++;
	}
	EndDIV();
	$sth->execute();

	while (@rows = $sth->fetchrow_array) {
		my $colCount = 0;
		my $jobStatus;
		my @lineElements = @rows;
		if ($lineElements[0] =~ m/^Job Id/) {
			OpenDIV("class","ApoHeader","");
		} elsif ($lineElements[0] !~ m/^\d/) {
			next;
		} else {
			OpenDIV("class","ApoRow","");
		}
		my $jobStatus = find_jobstatus($lineElements[0]);
		@lineElements=(@lineElements,$jobStatus);
		foreach my $element (@lineElements) {

					ClosedDIV("class","ApoCol$headerSizes[$colCount]","$element");
			$colCount++;
		}
		EndDIV();
		print "<br>";
		if ($_ =~ m/^Job Id/) {
				print "<br><hr>";
		}
	}
			print "<br>";
			print "<br>";
		EndDIV();
	$sth->finish();
	$dbh->disconnect();

} else {
	my @headerSizes = ("20","20","20","20","19");
	OpenDIV("ID","flexcontainer");
	OpenDIV("class","group");
	my @rows;
	my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
	my $sth = $dbh->prepare("SELECT * FROM completed WHERE COMPLETED > NOW() - INTERVAL 30 MINUTE ORDER BY COMPLETED DESC LIMIT 100");
	$sth->execute();
	   	 my @fields =  @{ $sth->{NAME_uc} };
		while (@rows = $sth->fetchrow_array) {
 			my %fieldContentJob;
			for (@rows) { $_ = "&nbsp;" if $_ eq ''; }
			#map { $_ =~ s//&nbsp;/g; $_ } @rows;#print  "JOB Name $rows[1] date is $rows[15]\n<br>";
			@fieldContentJob{@fields} = @rows;
		 	my $type = $fieldContentJob{"QUEUE"};
			if ($type eq "CRONACLE") {
			#OpenDIV("ID","jobitemExecuting");
			OpenDIV("ID","ApoRow");
 			ClosedDIV("class","ApoCol$headerSizes[0]","$fieldContentJob{\"QUEUE\"}");
 			ClosedDIV("class","ApoCol$headerSizes[1]","$fieldContentJob{\"NAME\"}");
 	 		ClosedDIV("class","ApoCol$headerSizes[2]","$fieldContentJob{\"PARAM1\"}");
 	 		ClosedDIV("class","ApoCol$headerSizes[3]","$fieldContentJob{\"PARAM2\"}");
 	 		ClosedDIV("class","ApoCol$headerSizes[4]","Completed Approx $fieldContentJob{\"COMPLETED\"}");
			EndDIV();
 	 		}			#print "@rows\n";		 	if ($type eq "RIPE") {
			#OpenDIV("ID","jobitemExecuting");
			if ($type eq "RIPE") {
			OpenDIV("ID","ApoRow");
 			ClosedDIV("class","ApoCol$headerSizes[0]","$fieldContentJob{\"QUEUE\"}");
 			ClosedDIV("class","ApoCol$headerSizes[1]","$fieldContentJob{\"NAME\"}");
 	 		ClosedDIV("class","ApoCol$headerSizes[2]","$fieldContentJob{\"PARAM1\"}");
 	 		ClosedDIV("class","ApoCol$headerSizes[3]","$fieldContentJob{\"PARAM2\"}");
 	 		ClosedDIV("class","ApoCol$headerSizes[4]","Completed Approx $fieldContentJob{\"COMPLETED\"}");
			EndDIV();
 	 		}

		}
	$sth->finish();
	$dbh->disconnect();
	EndDIV();
	EndDIV();

}


sub getAlphaQGroup {
	OpenDIV("ID","flexcontainer");
# Whatever queue is being sent to this subroutine goes in the array below
my @genqueues = @_;
		my @av_list;
		my $thisAV;
		my $findQ = "CRONACLE";
if ($prodType eq "ELECTRONIC") {
	$findQ = "RIPE";
	}
foreach my $thisOne (@genqueues) {
		my $dbh;
		if (lc($thisOne) =~ m/^verify/) {
		# no div
		} else {
			OpenDIV("class","group");
		}
		use DBI;
	if (lc($thisOne) =~ m/^(ripe|qbrwagent)/) {
		my @combinedGeneric = split('\|',$thisOne);
			my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
		foreach my $thisGen (@combinedGeneric) {
		my $fieldName = uc($thisGen);
		ClosedDIV("class","genQ","$fieldName");
		my $sth = $dbh->prepare("SELECT * FROM alphas WHERE QUEUE = ? AND TYPE = ? AND PARAM1  = ?");
			$sth->execute($findQ,"JOB",$thisGen);
#			$sth->execute("JOB",$thisGen);
	   	 my @fields =  @{ $sth->{NAME_uc} };
	  		#my @fieldsJob =  @{ $sth->{NAME_uc} };
			#if ($returnNumber > 0) {ClosedDIV("class","onqueue","ON QUEUE");}
			while ( my @rows =  $sth->fetchrow_array() ) {
					#my @fieldValsJob = @rows;
				my %fieldContentJob;
				@fieldContentJob{@fields} = @rows;
				my $fullEntry = "$fieldContentJob{\"ENTRY\"}&nbsp;$fieldContentJob{\"NAME\"}&nbsp;$fieldContentJob{\"NAME\"}&nbsp;";
				if (($fieldContentJob{"STATUS"} eq "Executing") || ($fieldContentJob{"STATUS"} eq "Pending") || ($fieldContentJob{"STATUS"} eq "Retained"))  {
			#	print "$fieldContentJob{\"NAME\"} - $fieldContentJob{\"STATUS\"}\n<br>";
						ClosedDIV("class","jobitem$fieldContentJob{\"STATUS\"}","$fieldContentJob{\"PARAM2\"} - $fieldContentJob{\"ENTRY\"}<br>$fieldContentJob{\"NAME\"}");
				#ClosedDIV("class","jobitemfull","$fullEntry");
				}
			} #		while ( my @rows =  $sth->fetchrow_array() ) {

		$sth->finish;
		}
		$dbh->disconnect;
	EndDIV();
	} else {
		my @combinedGeneric = split('\|',$thisOne);
		foreach my $thisGen (@combinedGeneric) {
		my @findBQueues;
		my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
		my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND NAME  = ?");
		$sth->execute("GenQue",$thisGen);
	    my @fields =  @{ $sth->{NAME_uc} };
		my @fieldVals = $sth->fetchrow_array();
		my $returnCount = @fieldVals;
		my %findGenQueues;
		@findGenQueues{@fields} = @fieldVals;
		my $batchOnly = "FALSE";
		$sth->finish;
		#ClosedDIV("class","genQ","$findGenQueues{\"NAME\"}");
		if ($returnCount == 0) {
			@findBQueues = ($thisGen);
			$batchOnly = "TRUE";
		} else {
			ClosedDIV("class","genQ","$findGenQueues{\"NAME\"}");
			#print "$findBatchQueues{\"NAME\"}\n<br>";
			@findBQueues = split(",",$findGenQueues{"PARAMETERS"});
			my $sth2 = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND QUEUE  = ? AND (STATUS = ? or STATUS = ?)");
			$sth2->execute("JOB",$thisGen,"Retained","Pending");
			#if ($returnNumber > 0) {ClosedDIV("class","onqueue","ON QUEUE");}
			while (my @rows =  $sth2->fetchrow_array()) {
		  		my @fieldsGen =  @{ $sth2->{NAME_uc} };
				my @fieldValsGen = @rows;
				my %fieldContentG;
				@fieldContentG{@fieldsGen} = @fieldValsGen;

				if (($fieldContentG{"STATUS"} eq "Executing") || ($fieldContentG{"STATUS"} eq "Pending") || ($fieldContentG{"STATUS"} eq "Retained")) {
						OpenDIV("class","jobitem$fieldContentG{\"STATUS\"}","$fieldContentG{\"NAME\"}");
						#ClosedDIV("class","more","$fieldContentJob{\"ENTRY\"} $fieldContentJob{\"PARAM2\"}");
						EndDIV();
				}
			}
			$sth2->finish;
		}
			# Get all Batch queues for the current generic queue.
		foreach my $thisBatch (@findBQueues) {
			#print "Looking for batch queue $thisBatch\n";
			my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND NAME  = ?");
			$sth->execute("BatchQue",$thisBatch);
	  		 my @fieldsB =  @{ $sth->{NAME_uc} };
			my @fieldValsB = $sth->fetchrow_array();
			my %fieldContentB;
			@fieldContentB{@fieldsB} = @fieldValsB;
			#print "&#09;$fieldContentB{\"NAME\"} - $fieldContentB{\"STATUS\"}\n<br>";
			if ($fieldContentB{"NAME"} eq "") {next;}
			if ($fieldContentB{"NAME"} =~ /^VERIFY/) {
				#noheader vor AVs
			} else {
				ClosedDIV("class","item$fieldContentB{\"STATUS\"}","$fieldContentB{\"NAME\"}");
			}
			$sth->finish;
			my $findBatchJob = 	$fieldContentB{"NAME"};
			## get all jobs in batch queue
				my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND QUEUE  = ?");
				$sth->execute("JOB",$thisBatch);
	  			 my @fieldsJob =  @{ $sth->{NAME_uc} };
				while ( my @rows =  $sth->fetchrow_array() ) {
					#my @fieldValsJob = @rows;
					my %fieldContentJob;
					@fieldContentJob{@fieldsJob} = @rows;
				#	print "&#09;&#09;$fieldContentJob{\"NAME\"} - $fieldContentJob{\"STATUS\"}\n<br>";
					my @jobparts;
					my $getParts;
					if ($thisBatch =~ /^VERIFY/) {
						my @jobParts = split('_',$fieldContentJob{"NAME"});
						my $CID = $jobParts[1];
						my $dueTime = substr $jobParts[0],2,length($jobParts[0]);
						#print "$dueTime";
						my @custMaster = findCustomerDB($CID);
						my @thisLate = getHOWlate($dueTime);
						my $DivLate = $thisLate[1];
						my $HowLate =  $thisLate[0];
						my $fileName = $fieldContentJob{"PARAM2"};
						if (($DivLate ne "") && (($prodType eq "PRINT") && ($custMaster[0] eq "CCN"))){
							#ClosedDIV("class","jobitemVerify$DivLate","$fieldContentJob{\"PARAM2\"} <br>CID $CID Due at $dueTime");
							$thisAV = "$CID|$dueTime|$fieldContentJob{\"PARAM2\"}|$DivLate";
							@av_list = (@av_list, $thisAV);
						}
						if (($DivLate ne "") && ($fileName !~ m/gz$/) && ($prodType eq "ELECTRONICGLEN") && ($custMaster[0] eq "CCE")){
							#ClosedDIV("class","jobitemVerify$DivLate","$fieldContentJob{\"PARAM2\"} <br>CID $CID Due at $dueTime");
							$thisAV = "$CID|$dueTime|$fieldContentJob{\"PARAM2\"}|$DivLate";
							@av_list = (@av_list, $thisAV);
						}
						if (($DivLate ne "") && ($fileName =~ m/gz$/) && ($prodType eq "ELECTRONIC") && ($custMaster[0] eq "CCE")){
							#ClosedDIV("class","jobitemVerify$DivLate","$fieldContentJob{\"PARAM2\"} <br>CID $CID Due at $dueTime");
							$thisAV = "$CID|$dueTime|$fieldContentJob{\"PARAM2\"}|$DivLate";
							@av_list = (@av_list, $thisAV);
						}

					} elsif (($fieldContentJob{"STATUS"} eq "Executing") || ($fieldContentJob{"STATUS"} eq "Pending") || ($fieldContentJob{"STATUS"} eq "Retained")) {
						OpenDIV("class","jobitem$fieldContentJob{\"STATUS\"}","$fieldContentJob{\"NAME\"}");
						#ClosedDIV("class","more","$fieldContentJob{\"ENTRY\"} $fieldContentJob{\"PARAM2\"}");
						EndDIV();
					}
				}
				$sth->finish;


			}
		if ($batchOnly eq "FALSE") {
		my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
		my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND QUEUE  = ? AND (STATUS = ? OR STATUS = ?)");
		$sth->execute("JOB",$thisGen,"Pending","Retained");
	    my @fields =  @{ $sth->{NAME_uc} };
		my @checkNumber = $sth->fetchrow_array();
		my $returnNumber = scalar @checkNumber;
		$sth->finish;
		#my @fieldVals = $sth->fetchrow_array();
		my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND QUEUE  = ?");
		$sth->execute("JOB",$thisGen);
	    my @fields =  @{ $sth->{NAME_uc} };
	  	#my @fieldsJob =  @{ $sth->{NAME_uc} };
		#if ($returnNumber > 0) {ClosedDIV("class","onqueue","ON QUEUE");}
		while ( my @rows =  $sth->fetchrow_array() ) {
			my %fieldContentJob;
			@fieldContentJob{@fields} = @rows;
			my $fullEntry = "$fieldContentJob{\"ENTRY\"}&nbsp;$fieldContentJob{\"NAME\"}&nbsp;$fieldContentJob{\"NAME\"}&nbsp;";
			if (($fieldContentJob{"STATUS"} eq "Executing") || ($fieldContentJob{"STATUS"} eq "Pending") || ($fieldContentJob{"STATUS"} eq "Retained"))  {
			}
		} #		while ( my @rows =  $sth->fetchrow_array() ) {

		$sth->finish;

		} #if ($batchOnly eq "FALSE")
		$dbh->disconnect;
	}#		foreach my $thisBatch (@findBQueues) {
		if (lc($thisOne) =~ m/^verify/) {
			# no div. for verify. We do this later
		} else {
			EndDIV();
		}
} #	foreach my $thisGen (@combinedGeneric) {
} #if ripe
	if (($prodType eq "PRINT") || ($prodType eq "ELECTRONICGLEN") || ($prodType eq "ELECTRONIC")) {
		my $custName = "UNKNOWN";
		my @avsort = sort(@av_list);
		OpenDIV("class","group");
		ClosedDIV("class","itemidle","Late Files");
		my $oldCID = "";
		my $oldTime = "";
		my $allcidtime = "";
			foreach (@avsort) {
				my @avParts = split('\|',$_);
				my $newCID = $avParts[0];
				my $newTime = $avParts[1];
				my $newFile = $avParts[2];
				#print "$newCID - $oldCID, $newTime - $oldTime\n";
				#if ($oldCID ne "") { EndDIV(); }
				if (($newCID eq $oldCID) && ($newTime eq $oldTime)) {
					ClosedDIV("class","jobitemVerifyplain","<center>$newFile</center>");
				} else {
				my $dbh = DBI->connect("DBI:mysql:Customers;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
				my $sth = $dbh->prepare("SELECT NAME FROM customers WHERE CID = ?");
				$sth->execute($newCID);
				my $custName = $sth->fetchrow_array();
				$custName = substr($custName,0,15);
				$sth->finish;
				$dbh->disconnect;
					ClosedDIV("class","jobitemVerify$avParts[3]","<center>CID $newCID Due at $newTime<br>$custName</center>");
					ClosedDIV("class","jobitemVerifyplain","<center>$newFile</center>");
				}
				$oldCID = $newCID;
				$oldTime = $newTime;
			}
			#EndDIV();
		EndDIV();
	}
	EndDIV();

} #sub getAlphaQGroup {

	OpenDIV("ID","flexsidebar");
	#ClosedDIV("class","FlexSidebarItem","<a href=\"$selfPage\">LATEST COMPLETED</a>");
	print "<a style=\"display:block\" href=\"$selfPage?prodType=PRINT\">";
 	ClosedDIV("class","FlexSidebarItem","PRINT");
	print "</a>";
	my @sums = getAlphaQTotals((@genqueues,""));
	if ($sums[4] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Late2Client &nbsp;&rarr;&nbsp;$sums[4]");
	}
	if ($sums[1] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Retained Entries &nbsp;&rarr;&nbsp;$sums[1]");
	}
	if ($sums[3] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Stopped Queues &nbsp;&rarr;&nbsp;$sums[3]");
	}
	if ($sums[0] > 20){
	ClosedDIV("class","FlexSidebarSum","Lots of Pending! &nbsp;&rarr;&nbsp;$sums[0]");
	}
	#EndDIV();
	print "<a style=\"display:block\" href=\"$selfPage?prodType=ELECTRONICGLEN\">";
	ClosedDIV("class","FlexSidebarItem","ELECTRONIC GLEN");
	print "</a>";
	my @sums = getAlphaQTotals((@CCEqueues2,""));
	if ($sums[5] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Late2Client &nbsp;&rarr;&nbsp;$sums[5]");
	}
	if ($sums[1] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Retained Entries &nbsp;&rarr;&nbsp;$sums[1]");
	}
	if ($sums[3] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Stopped Queues &nbsp;&rarr;&nbsp;$sums[3]");
	}
	if ($sums[0] > 20){
	ClosedDIV("class","FlexSidebarSum","Lots of Pending! &nbsp;&rarr;&nbsp;$sums[0]");
	}
	print "<a style=\"display:block\" href=\"$selfPage?prodType=ELECTRONIC\">";
	ClosedDIV("class","FlexSidebarItem","RIPE");
	print "</a>";
	my @sums = getAlphaQTotals((@ripeSystems,"RIPE"));
	if ($sums[6] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Late2Client &nbsp;&rarr;&nbsp;$sums[6]");
	}
	if ($sums[1] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Retained Entries &nbsp;&rarr;&nbsp;$sums[1]");
	}
	if ($sums[3] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Stopped Queues &nbsp;&rarr;&nbsp;$sums[3]");
	}
	if ($sums[0] > 20){
	ClosedDIV("class","FlexSidebarSum","Lots of Pending! &nbsp;&rarr;&nbsp;$sums[0]");
	}
	print "<a style=\"display:block\" href=\"$selfPage?prodType=CRONACLE\">";
	ClosedDIV("class","FlexSidebarItem","CRONACLE");
	print "</a>";
	my @sums = getAlphaQTotals((@cronacleSystems,"CRONACLE"));
	if ($sums[5] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Late2Client &nbsp;&rarr;&nbsp;$sums[5]");
	}
	if ($sums[1] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Retained Entries &nbsp;&rarr;&nbsp;$sums[1]");
	}
	if ($sums[3] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Stopped Queues &nbsp;&rarr;&nbsp;$sums[3]");
	}
	if ($sums[0] > 20){
	ClosedDIV("class","FlexSidebarSum","Lots of Pending! &nbsp;&rarr;&nbsp;$sums[0]");
	}
	print "<a style=\"display:block\" href=\"$selfPage?prodType=EDITORIAL\">";
	ClosedDIV("class","FlexSidebarItem","EDITORIAL");
	print "</a>";
	my @sums = getAlphaQTotals((@Editqueues,""));
	if ($sums[1] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Retained Entries &nbsp;&rarr;&nbsp;$sums[1]");
	}
	if ($sums[3] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Stopped Queues &nbsp;&rarr;&nbsp;$sums[3]");
	}
	if ($sums[0] > 20){
	ClosedDIV("class","FlexSidebarSum","Lots of Pending! &nbsp;&rarr;&nbsp;$sums[0]");
	}
	print "<a style=\"display:block\" href=\"$selfPage?prodType=MAINT\">";
	ClosedDIV("class","FlexSidebarItem","MAINT QUES");
	print "</a>";
	my @sums = getAlphaQTotals((@maint_queues,""));
	if ($sums[1] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Retained Entries &nbsp;&rarr;&nbsp;$sums[1]");
	}
	if ($sums[3] > 0) {
	ClosedDIV("class","FlexSidebarSumBAD","Stopped Queues &nbsp;&rarr;&nbsp;$sums[3]");
	}
	if ($sums[0] > 20){
	ClosedDIV("class","FlexSidebarSum","Lots of Pending! &nbsp;&rarr;&nbsp;$sums[0]");
	}
	EndDIV();



HTMLend();

sub getHOWlate {
my $duetime = $_[0];
	my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
				my $nowtime = ($f_hour * 60) + $f_minute;
						my $AvDIV = "";
						my $dueHour = substr($duetime,0,2);
						my $dueMin = substr($duetime,3,2);
						my $whenDew = ($dueHour * 60) + $dueMin;
						#print "$nowtime - $whenDew";
						my $howLate = $nowtime - $whenDew;
						my $dueTime = "$dueHour:$dueMin";
						if ($howLate > 0) {
							if ($howLate > 15) {
								$AvDIV = "15";
							}
							if ($howLate > 30) {
								$AvDIV = "30";
							}
							if ($howLate > 60) {
								$AvDIV = "60";
							}
							if ($howLate > 120) {
								$AvDIV = "120";
							}
						}
return($howLate,$AvDIV);
}

sub getAlphaQTotals {
	my $pending = 0;
	my $retained = 0;
	my $executing = 0;
	my $stopped = 0;
	my $late2clientCCN = 0;
	my $late2clientCCE = 0;
	my $late2clientRIPE = 0;
	#OpenDIV("ID","flexcontainer");
my @genqueues = @_;
my $production = pop @genqueues;
foreach my $thisOne (@genqueues) {
		my @combinedGeneric = split('\|',$thisOne);
		use DBI;
	if (lc($thisOne) =~ m/^ripe|^qbrw/) {
		my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
		foreach my $thisGen (@combinedGeneric) {
			my $fieldName = uc($thisGen);
			#ClosedDIV("class","genQ","$fieldName");
			my $sth = $dbh->prepare("SELECT * FROM alphas WHERE TYPE = ? AND PARAM1  = ?");
			$sth->execute("JOB",$thisGen);
	   		 my @fields =  @{ $sth->{NAME_uc} };
	  		#my @fieldsJob =  @{ $sth->{NAME_uc} };
			#if ($returnNumber > 0) {ClosedDIV("class","onqueue","ON QUEUE");}
			while ( my @rows =  $sth->fetchrow_array() ) {
					#my @fieldValsJob = @rows;
				my %fieldContentJob;
				@fieldContentJob{@fields} = @rows;
				if ((($fieldContentJob{"QUEUE"} eq "CRONACLE") && ($production eq "CRONACLE")) || (($fieldContentJob{"QUEUE"} eq "RIPE") && ($production eq "RIPE"))) {
					my $fullEntry = "$fieldContentJob{\"ENTRY\"}&nbsp;$fieldContentJob{\"NAME\"}&nbsp;$fieldContentJob{\"NAME\"}&nbsp;";
					if ($fieldContentJob{"STATUS"} eq "Executing") {
						$executing++;
					}
					if ($fieldContentJob{"STATUS"} eq "Retained") {
						$retained++;
					}
				}
			} #		while ( my @rows =  $sth->fetchrow_array() ) {

			$sth->finish;
		}
		$dbh->disconnect;
	#EndDIV();
	} else {
		foreach my $thisGen (@combinedGeneric) {
			my @findBQueues;
			my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
			my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND NAME  = ?");
			$sth->execute("GenQue",$thisGen);
	    	my @fields =  @{ $sth->{NAME_uc} };
			my @fieldVals = $sth->fetchrow_array();
			my $returnCount = @fieldVals;
			my %findGenQueues;
			@findGenQueues{@fields} = @fieldVals;
			my $batchOnly = "FALSE";
			$sth->finish;
			#ClosedDIV("class","genQ","$findGenQueues{\"NAME\"}");
			if ($returnCount == 0) {
				@findBQueues = ($thisGen);
				$batchOnly = "TRUE";
			} else {
				@findBQueues = split(",",$findGenQueues{"PARAMETERS"});
			}
			# Get all Batch queues for the current generic queue.
			foreach my $thisBatch (@findBQueues) {
				#print "Looking for batch queue $thisBatch\n";
				my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND NAME  = ?");
				$sth->execute("BatchQue",$thisBatch);
	  			my @fieldsB =  @{ $sth->{NAME_uc} };
				my @fieldValsB = $sth->fetchrow_array();
				my %fieldContentB;
				@fieldContentB{@fieldsB} = @fieldValsB;
				if ($fieldContentB{"NAME"} eq "") {next;}
				if ($fieldContentB{"STATUS"} eq "stopped") {
					$stopped++;
				}
				$sth->finish;
				my $findBatchJob = 	$fieldContentB{"NAME"};
				my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND QUEUE  = ?");
				$sth->execute("JOB",$thisBatch);
	  			my @fieldsJob =  @{ $sth->{NAME_uc} };

				while ( my @rows =  $sth->fetchrow_array() ) {
					my %fieldContentJob;
					@fieldContentJob{@fieldsJob} = @rows;
					my @jobparts;
					my $getParts;
					if ($thisBatch =~ /^VERIFY/) {
						my @jobParts = split('_',$fieldContentJob{"NAME"});
						my $CID = $jobParts[1];
						my $dueTime = substr $jobParts[0],2,length($jobParts[0]);
						my @custMaster = findCustomerDB($CID);
						my @thisLate = getHOWlate($dueTime);
						my $DivLate = $thisLate[1];
						my $HowLate =  $thisLate[0];
						my $late_file = $fieldContentJob{"PARAM2"};
						if (($DivLate ne "") && ($custMaster[0] eq "CCN")){
							$late2clientCCN++;
						}
						if (($DivLate ne "") && ($custMaster[0] eq "CCE") && ($late_file !~ m/gz$/)){
							$late2clientCCE++;
						}
						if (($DivLate ne "") && ($custMaster[0] eq "CCE") && ($late_file =~ m/gz$/)){
							$late2clientRIPE++;
						}

					} elsif ($fieldContentJob{"STATUS"} eq "Executing") {
						$executing++;
					} elsif ($fieldContentJob{"STATUS"} eq "Pending") {
						$pending++;
					} elsif ($fieldContentJob{"STATUS"} eq "Retained") {
						$retained++;
						#OpenDIV("class","jobitem$fieldContentJob{\"STATUS\"}","$fieldContentJob{\"NAME\"}");
						#ClosedDIV("class","more","$fieldContentJob{\"ENTRY\"} $fieldContentJob{\"PARAM2\"}");
						#EndDIV();
					}
				}
				$sth->finish;


			}
		if ($batchOnly eq "FALSE") {
		my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
		my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND QUEUE  = ? AND (STATUS = ? OR STATUS = ?)");
		$sth->execute("JOB",$thisGen,"Pending","Retained");
	    my @fields =  @{ $sth->{NAME_uc} };
		my @checkNumber = $sth->fetchrow_array();
		my $returnNumber = scalar @checkNumber;
		$sth->finish;
		my $sth = $dbh->prepare("SELECT * FROM ALPHAS WHERE TYPE = ? AND QUEUE  = ?");
		$sth->execute("JOB",$thisGen);
	    my @fields =  @{ $sth->{NAME_uc} };
		while ( my @rows =  $sth->fetchrow_array() ) {
			my %fieldContentJob;
			@fieldContentJob{@fields} = @rows;
			my $fullEntry = "$fieldContentJob{\"ENTRY\"}&nbsp;$fieldContentJob{\"NAME\"}&nbsp;$fieldContentJob{\"NAME\"}&nbsp;";
			if ($fieldContentJob{"STATUS"} eq "Executing") {
				$executing++;
			} elsif ($fieldContentJob{"STATUS"} eq "Pending") {
				$pending++;
			} elsif ($fieldContentJob{"STATUS"} eq "Retained")  {
				$retained++;
			}
		} #		while ( my @rows =  $sth->fetchrow_array() ) {
		$sth->finish;
		} #if ($batchOnly eq "FALSE")
		$dbh->disconnect;
	}#		foreach my $thisBatch (@findBQueues) {
} #	foreach my $thisGen (@combinedGeneric) {
}
return($pending,$retained,$executing,$stopped,$late2clientCCN,$late2clientCCE,$late2clientRIPE);
} #sub getAlphaQGroup {


sub getHOWlate {
my $duetime = $_[0];
	my ($f_second, $f_minute, $f_hour, $f_day, $f_month, $f_year, $f_weekDay, $f_dayOfYear, $IsDST) = localtime(time);
				my $nowtime = ($f_hour * 60) + $f_minute;
						my $AvDIV = "";
						my $dueHour = substr($duetime,0,2);
						my $dueMin = substr($duetime,3,2);
						my $whenDew = ($dueHour * 60) + $dueMin;
						#print "$nowtime - $whenDew";
						my $howLate = $nowtime - $whenDew;
						my $dueTime = "$dueHour:$dueMin";
						if ($howLate > 0) {
							if ($howLate > 15) {
								$AvDIV = "15";
							}
							if ($howLate > 30) {
								$AvDIV = "30";
							}
							if ($howLate > 60) {
								$AvDIV = "60";
							}
							if ($howLate > 120) {
								$AvDIV = "120";
							}
						}
return($howLate,$AvDIV);
}

sub findCustomerDB {
	my $findCID = $_[0];
		my $dbh = DBI->connect("DBI:mysql:Customers;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
		my $sth = $dbh->prepare("SELECT * FROM customers WHERE CID = ?");
		$sth->execute($findCID);
	    my @fields =  @{ $sth->{NAME_uc} };
		my @rows =  $sth->fetchrow_array();
		my %fieldContent;
		@fieldContent{@fields} = @rows;
		$sth->finish;
		$dbh->disconnect;
return($fieldContent{"DEPT"},$fieldContent{"NAME"},$fieldContent{"ALERT_LEVEL"});
}

sub find_jobstatus {
#my $type = $_[0];
my $Val = $_[0];
my $returnVal = "Not Started";
my $sqlSnap = "SELECT ENTRY FROM alphas WHERE ENTRY = $Val AND DATE(Stamp) = CURDATE() AND STATUS = 'retained'";
my $sqlComp = "SELECT ENTRY FROM completed WHERE ENTRY =  $Val AND DATE(COMPLETED) = CURDATE()";
	use DBI;
	my $dbhi = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
	my $sthi = $dbhi->prepare($sqlSnap);
	$sthi->execute();
	my $foundcount = $sthi->rows();
	#print "Found $foundcount items\n";
	$sthi->finish();
	$dbhi->disconnect();
	#emailuser("new",\%userdata);
	#return(%userdata);
	my $returnVal = "Not Started";
	if ($foundcount > 0) {
		$returnVal = "FAILED";
	} else {
		$returnVal = "OKAY";

	}
	$sthi->finish;
	$dbhi->disconnect;
return($returnVal);

}

sub SanpshotTranslator {
	my @allVals = @_;
	my @returnHeaders = ("JOBID","TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME",);;
	my @TurbosCols = ("JOBID","TYPE","SCRIPT NAME","STATUS","ENTRY","QUEUE","PARAMETERS","SCRIPT NAME","LISTINGS DATE","CID","TIME OUT","SCRIPT TYPE","TIME","STATE");
	my @AVCols = ("JOBID","TYPE","AV NAME","STATUS","ENTRY","QUEUE","PARAMETERS","FILE LOCATION","FILE NAME","","","LOOK BACK","USERNAME","PASSWORD","AV STATUS","TIME");
	my @RIPECols = ("JOBID","TYPE","FORMAT","STATUS","SCHEDULE ID","QUEUE","PARAMETERS","SYSTEM","CUST CODE","NOTES","PRODUCT ID","STEP","START TIME","FAIL TIME","","TIME");
	#my @CronCols = ("JOBID","TYPE","FORMAT","STATUS","SCHEDULE ID","QUEUE","PARAMETERS","SYSTEM","CUST CODE","NOTES","PRODUCT ID","STEP","START TIME","FAIL TIME","","TIME","STATE","LOG","ORIG_JOB","USER");
	my $qName = $allVals[5];
	my $Q2 = $allVals[6];
	if ($qName eq "RIPE") {
		@returnHeaders = @RIPECols;
	} elsif ($qName =~ /^VERIFY/) {
		@returnHeaders = @AVCols;
	} elsif ($qName =~ /^TURBO/) {
		@returnHeaders = @TurbosCols;
	} else {

	}
return(@returnHeaders);
}
