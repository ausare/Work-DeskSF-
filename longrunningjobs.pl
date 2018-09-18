#!/Users/scripting/perl5/perlbrew/perls/perl-5.24.0/bin/Perl
## Larry Gonyea - Gracenote
#use strict;
use warnings;
use Tie::File;
use File::Find;
use Time::Piece;

#my $date = localtime;
#my $t = Time::Piece->strptime($date, '%b %d, %Y %I:%M %p');
#my $sqlTime = $t->strftime('%F %T');
use Time::Piece::MySQL;
my $sqlTime = localtime->mysql_datetime;
my $systemStatus = "Dev";
my $rowID;
	## Find hung Backend Jobs
			use DBI;
			my $dbuser = "root";
			my $dbpass = "alaska";
			my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
			my $sth = $dbh->prepare("Select * from alphas WHERE TYPE = 'JOB' and QUEUE LIKE 'BACKEND%'");
			#my $sth = $dbh->prepare("Select * from alphas WHERE TYPE = 'JOB' and QUEUE = 'RIPE'");
			$sth->execute();
			while (my @row = $sth->fetchrow_array) {
				my $sth2 = $dbh->prepare("SELECT TIMESTAMPDIFF(MINUTE,STARTTIME,Stamp) from alphas WHERE JOBID = '$row[0]' ");
				$sth2->execute();
				my $timediff = $sth2->fetchrow_array;
				#	if ($timediff > 120) {
				if ($timediff > 60) {
					my $sth3 = $dbh->prepare("SELECT * from alphas WHERE JOBID = '$row[0]' ");
					$sth3->execute();
						my @allrow = $sth3->fetchrow_array; 
						my @colsarr = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STATE","LOG","ORIG_JOB");
						my $idSave = $allrow[0];
						my $sub = "Batch Job alert!! $row[2] has been running for $timediff miunutes\n";
						my $bod = "Batch Job $row[2] has been running on $row[5] for $timediff minutes. Please check if it is hung.";
						#shift @allrow;
						#my @toInput = (@allrow,$idSave);				
						@colsarr = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STATE","LOG","ORIG_JOB","USER");
						@toInput = ($allrow[1],$allrow[2],$allrow[3],$allrow[4],$allrow[5],$allrow[6],$allrow[7],$allrow[8],$allrow[9],$allrow[10],$allrow[11],$allrow[12],$allrow[13],$allrow[14],"NOW()","NEW",$bod,$idSave,"System");
						#CheckIncidents for previously reported. 
						my $reportThis = checkForIncident("ORIG_JOB",$idSave);
						if (($reportThis eq "Yes") && ($allrow[3] ne 'retained')) {
							print "Batch Job alert!! $row[2] has been running for $timediff miunutes\n";
							my $bod = "Batch Job $row[2] has been running on $row[5] for $timediff minutes. Entry Number is $allrow[4]. Please check if it is hung.";
							my $sub = "Batch alert!! $row[2] has been running for $timediff minutes\n";
							insertTABLE("incidents","INCIDENTS",\@colsarr,\@toInput);
							emailnotifier($sub,$bod);
						} else {
							print "Batch Job $row[2] has been reported already\n";
						
						}
						$sth3->finish();	
					
				}
				$sth2->finish();				
			}	
			$sth->finish();	
##Find Late2Clients
			$sth = $dbh->prepare("Select * from alphas WHERE TYPE = 'JOB' and STATUS = 'retained'");
			#my $sth = $dbh->prepare("Select * from alphas WHERE TYPE = 'JOB' and QUEUE = 'RIPE'");
			$sth->execute();
			while (my @allrow = $sth->fetchrow_array) {
						my @headers;
						my @colsarr = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STATE","LOG","ORIG_JOB");
						my $idSave = $allrow[0];
						#my $bod = "Incident $allrow[2]. Please check if it is hung.";
						@headers = IncidentTranslator(@allrow);
						@colsarr = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STATE","LOG","ORIG_JOB","USER");
						@toInput = ($allrow[1],$allrow[2],$allrow[3],$allrow[4],$allrow[5],$allrow[6],$allrow[7],$allrow[8],$allrow[9],$allrow[10],$allrow[11],$allrow[12],$allrow[13],$allrow[14],"NOW()","NEW",$bod,$idSave,"System");
						#CheckIncidents for previously reported. 
						my $reportThis = checkForIncident("ORIG_JOB",$idSave);
						if ($reportThis eq "Yes")  {
							print "Incident!! $allrow[2]\n";
							insertTABLE("incidents","INCIDENTS",\@colsarr,\@toInput);
							INCemailnotifierII(\@headers,\@allrow);
						} 
			}
			$sth->finish();	

##NEW Find Cronacle Long Running Jobs
			# $sth = $dbh->prepare("Select * from alphas WHERE TYPE = 'JOB' and STATUS = 'Long Running'");
			# $sth->execute();
			# while (my @allrow = $sth->fetchrow_array) {
			# 			my @headers;
			# 			@colsarr = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STATE","LOG","ORIG_JOB");
			# 			my $idSave = $allrow[0];
			# 			@headers = IncidentTranslator(@allrow);
			# 			@colsarr = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STATE","LOG","ORIG_JOB","USER");
			# 			@toInput = ($allrow[1],$allrow[2],$allrow[3],$allrow[4],$allrow[5],$allrow[6],$allrow[7],$allrow[8],$allrow[9],$allrow[10],$allrow[11],$allrow[12],$allrow[13],$allrow[14],"NOW()","NEW",$bod,$idSave,"System");
			# 			#CheckIncidents for previously reported. 
			# 			my $reportThis = checkForIncident("ORIG_JOB",$idSave);
			# 			if ($reportThis eq "Yes")  {
			# 				print "Incident!! $allrow[2]\n";
			# 				insertTABLE("incidents","INCIDENTS",\@colsarr,\@toInput);
			# 				INCemailnotifierII(\@headers,\@allrow);
			# 			} 
			# }
			# $sth->finish();	
			# $dbh->disconnect();

### Auto resolve incidents that are no longer in the snapshots db.

			$dbh = DBI->connect("DBI:mysql:incidents;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
			$dbh2 = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
			$sth = $dbh->prepare("Select * from INCIDENTS WHERE NOT STATE = 'RESOLVED'");
			$sth->execute();
			my @fields =  @{ $sth->{NAME_uc} };
			my %fieldhash;
			while (my @checkrow = $sth->fetchrow_array) {
				@fieldhash{@fields} = @checkrow;
				$rowID = $fieldhash{"JOBID"};
				my $origID = $fieldhash{"ORIG_JOB"};
				@headers = IncidentTranslator(@checkrow);
				my $sth2 = $dbh2->prepare("Select * from alphas WHERE JOBID = ? AND STATUS = ?");
				$sth2->execute($origID,"Retained");
				my $total = $sth2->rows;
				$sth2->finish;
				print "Entries found for $origID = $total\n";
				if ($total == 0) {
					#Resolve the issue. 
					print "Incident Resolved - $checkrow[2]\n";
					my $update = $dbh->prepare("UPDATE INCIDENTS SET STATE = 'Resolved' WHERE ORIG_JOB = ?");
					$update->execute($origID);
					$update->finish();	
					my $sub = "RESOLVED $checkrow[2] has been Resolved.\n";
					my $bod = "Incident for $checkrow[2] has been auto resolved. Error no longer exists";
					INCemailnotifier(\@headers,\@checkrow);
				}

			}						
			$sth->finish;
			$dbh->disconnect();
			$dbh2->disconnect();

sub insertTABLE {
my ($dbname,$tablename,$colVals,$Vals) = @_;
my $dbuser = "root";
my $dbpass = "alaska";
my @colsarr = @$colVals;
my @valsarr = @$Vals;
my $valsto;
my %userdata;
  @userdata{@colsarr} = @valsarr;	
my $keycount = 0;
if ($tablename eq "completed") {
	my @colsarr = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","COMPLETED","STARTTIME","ORIG_JOB");
	my $idSave = $valsarr[0];
	shift @valsarr;
	@valsarr = (@valsarr,$idSave);
}
#if ($tablename eq "INCIDENTS") {
#	my @colsarr = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STATE","LOG","ORIG_JOB");
#	my $idSave = @valsarr[0];
#	shift @valsarr;
#	@valsarr = (@valsarr,$idSave);
#}

foreach (@valsarr) {
 if ($keycount == 0) {
		$valsto = "'$_'";
	} elsif ($_ eq "NOW()") {
		$valsto = "$valsto,'$sqlTime'";
	} else {
		$valsto = "$valsto,'$_'";
	}
	$keycount++;
}
@colsarr = (@colsarr);
$valsto = "$valsto";

my $cols = join(",",@colsarr);
my $vals = join(",",@valsarr);
my $sqlUpdate = "INSERT INTO $tablename ($cols) VALUES ($valsto)";
#my $sqlGet = "SELECT * from  $tablename where USERNAME = ?";
	print "$sqlUpdate\n\n";
	use DBI;
	my $dbh = DBI->connect("DBI:mysql:$dbname;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
	my $sth = $dbh->prepare($sqlUpdate);
	$sth->execute();
	$sth->finish();
	
	$dbh->disconnect();
	#emailuser("new",\%userdata);
	#return(%userdata);
}

sub GetRowID {
	my ($dbname,$tablename,$Col,$Val) = @_;
	my $dbuser = "root";
	my $dbpass = "alaska";
	my $sqlQuery = "SELECT JOBID FROM $tablename WHERE $Col = $Val";
	use DBI;
	my $dbh = DBI->connect("DBI:mysql:$dbname;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
	my $sth = $dbh->prepare($sqlQuery);
	$sth->execute();
	$rowID = $sth->fetchrow_array();
	$sth->finish();

	return($rowID);
}
#not used
sub emailnotifier {
		my $toLine = "lawrence.gonyea\@nielsen.com,judy.ovitt\@nielsen.com,jason.gifford\@nielsen,gnzztms.gf.sysops\@nielsen.com";
	my @parameters = @_;
	my $BCCLine = "qb-sysops\@gracenote.pagerduty.com";
	use MIME::Lite;

    my $msg = MIME::Lite->new (
  	  From    => "ProductionMonitor\@gracenote.com",
  	  To      => "$toLine",
  	  Bcc     => "$BCCLine",
  	  Subject => "$parameters[0]",
  	  Type    => "text/html",
  	  Data    => "$parameters[1]",

    );
	if ($systemStatus eq "Live"){
    $msg->send();
	}
	print "Notification sent\n$parameters[0]\n$parameters[1]"
}
sub INCemailnotifier {
	#	my $toLine = "lawrence.gonyea\@nielsen.com,judy.ovitt\@nielsen.com,jason.gifford\@nielsen,gnzztms.gf.sysops\@nielsen.com";
	my ($colVals,$Vals) = @_;
	my @colsarr = @$colVals;
	my @valsarr = @$Vals;
	shift @valsarr;
	my $Sub = "RESOLVED $colsarr[1] - $valsarr[1]";
	my $toLine = "jason.gifford\@nielsen.com";
	#my @parameters = @_;
	my $counter = 0;
	my $Bod;
	foreach (@colsarr) {
		if ($valsarr[$counter] ne "") {
			$Bod = $Bod . "<b>$colsarr[$counter]</b> - $valsarr[$counter] <br><br>";
		}
		$counter++;
	}
	my $BCCLine = "qb-sysops\@gracenote.pagerduty.com";
	use MIME::Lite;

    my $msg = MIME::Lite->new (
  	  From    => "ProductionMonitor\@gracenote.com",
  	  To      => "$toLine",
  	  Bcc     => "",
  	  Subject => "$Sub",
  	  Type    => "text/html",
  	  Data    => "$Bod",

    );
	if($systemStatus eq "Live"){
    $msg->send();
	}
	print "Notification sent\n$Sub\n"
}

sub INCemailnotifierII {
	#	my $toLine = "lawrence.gonyea\@nielsen.com,judy.ovitt\@nielsen.com,jason.gifford\@nielsen,gnzztms.gf.sysops\@nielsen.com";
	my ($colVals,$Vals) = @_;
	my @colsarr = @$colVals;
	my @valsarr = @$Vals;
	shift @valsarr;
	my $toLine = "jason.gifford\@nielsen.com,kalinn.saunders\@nielsen.com";
	my $Sub = "New Incident $colsarr[1] - $valsarr[1]";
	my $BCCLine = "";
	my $counter = 0;
	my $Bod;
	
	foreach (@colsarr) {
		if ($valsarr[$counter] ne "") {
			$Bod = $Bod . "<b>$colsarr[$counter]</b> - $valsarr[$counter] <br><br>";
		}
		$counter++;
	}

	my $alertTest = sysopAlert(@valsarr);

	if($alertTest == 1) {
	$Sub = "Pagerduty Alert - $valsarr[1]";
	$toLine = "qb-sysops\@gracenote.pagerduty.com";
	$BCCLine = "jason.gifford\@nielsen.com";
	}

	if($alertTest == 2) {
	$Sub = "Problem with the alert_list.txt file";
	$toLine = "jason.gifford\@nielsen.com,kalinn.saunders\@nielsen.com";
	$BCCLine = "";
	}
	
	use MIME::Lite;

    my $msg = MIME::Lite->new (
  	  From    => "ProductionMonitor\@gracenote.com",
  	  To      => "$toLine",
  	  Bcc     => "$BCCLine",
  	  Subject => "$Sub",
  	  Type    => "text/html",
  	  Data    => "$Bod",

    );
	if($systemStatus eq "Live"){
    $msg->send();
	}
	print "Notification sent\n$Sub\n"
}

sub checkForIncident {
my ($colName,$Val) = @_;
my $dbuser = "root";
my $dbpass = "alaska";
my $sqlExe = "SELECT * FROM INCIDENTS WHERE $colName = $Val";
	use DBI;
	my $dbhi = DBI->connect("DBI:mysql:incidents;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
	my $sthi = $dbhi->prepare($sqlExe);
	$sthi->execute();
	my $foundcount = $sthi->rows();
	print "Found $foundcount items\n";
	$sthi->finish();
	$dbhi->disconnect();
	#emailuser("new",\%userdata);
	#return(%userdata);
	my $returnVal;
	if ($foundcount > 0) {
		$returnVal = "No";
	} else {
		$returnVal = "Yes";
	}
}
sub updateTABLE {
my ($dbname,$tablename,$insertHash,$whereis) = @_;
my $dbuser = "root";
my $dbpass = "alaska";
my @whereParts = split('\|',$whereis);
my $whereCol = $whereParts[0];
my $whereVal = $whereParts[1];
#print "Where $whereCol is $whereVal<br>";
my %insert = %{$insertHash};
my $sqlUpdate = "UPDATE $tablename SET ";
my $username;
	my $keycount = 0;
	while ( my ($key, $value) = each %insert ) {
	
		if ($keycount == 0) {
			if (($key eq "LASTUPDATE") || ($value eq "NOW()")) {
				$sqlUpdate = "$sqlUpdate $key='$sqlTime'";			
			} else {
				$sqlUpdate = "$sqlUpdate $key='$value'";			
			}
		} elsif (($key eq "LASTUPDATE") || ($value eq "NOW()")) {
			$sqlUpdate = "$sqlUpdate , $key='$sqlTime'";			
		} else {
		$sqlUpdate = "$sqlUpdate , $key='$value'";		
		}
		$keycount++;
	}
		#ClosedDIV("class","ApoRowHead","$username updated");
	$sqlUpdate = "$sqlUpdate WHERE $whereCol = '$whereVal'";
	#print "$sqlUpdate";
	use DBI;
	my $dbh = DBI->connect("DBI:mysql:$dbname;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
	my $sth = $dbh->prepare($sqlUpdate);
	$sth->execute();
	$sth->finish();
	$dbh->disconnect();
	#emailuser("update",\%insert);
	return(%insert);
}

sub IncidentTranslator {
	my @allVals = @_;
	my @returnHeaders;
	my @colNames = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
	my @TurbosCols = ("TYPE","SCRIPT NAME","STATUS","ENTRY","QUEUE","PARAMETERS","SCRIPT NAME","LISTINGS DATE","CID","TIME OUT","SCRIPT TYPE","TIME");
	my @AVCols = ("TYPE","AV NAME","STATUS","ENTRY","QUEUE","PARAMETERS","FILE LOCATION","FILE NAME","","","LOOK BACK","USERNAME","PASSWORD","AV STATUS");
	my @RIPECols = ("TYPE","FORMAT","STATUS","SCHEDULE ID","QUEUE","PARAMETERS","SYSTEM","CUST CODE","NOTES","PRODUCT ID","STEP","START TIME","FAIL TIME","");
	my @CronCols = ("TYPE","FORMAT","STATUS","JOB ID","QUEUE","PARAMETERS","SYSTEM","CUST CODE","","JOB CHAIN","","","TIME");
	my $qName = $allVals[5];
	my $Q2 = $allVals[6];
	if ($qName eq "RIPE") {
		@returnHeaders = @RIPECols;
	} elsif ($qName =~ /^VERIFY/) {
		@returnHeaders = @AVCols;		
	} elsif ($qName =~ /^TURBO/) {
		@returnHeaders = @TurbosCols;		
	} else {
		@returnHeaders = @colNames;				
	}
return(@returnHeaders);
}

sub sysopAlert {
    # taking the column list sent to this subroutine and placing it
    # in columnList variable then getting the PARAM2 column from the 7th
    # position.
    my @columnList = @_;
    my $param2_col = $columnList[7];
	my $alert = 0;

    # Getting file contents and removing the newline
    open FH,"<","/PerlLib/alert_list.txt" or return 2;
     my @alert_list_file = <FH>;
     chomp(@alert_list_file);
    close FH;

	my $countArray = @alert_list_file;

    foreach (@alert_list_file) {
     if ($_ eq $param2_col){
        $alert = 1;
     } 
    }
	return $alert;
}
