#!/Users/scripting/perl5/perlbrew/perls/perl-5.24.0/bin/Perl
#
# This script breaks down the text file sent from becky "snapshot9.txt" file and also looks
# at the Cronacle files, placing both in SNAPSHOTS/alpha DB.
#
#use strict;
#use warnings;
use Tie::File;
use File::Find;
use Time::Piece;

#my $date = localtime;
#my $t = Time::Piece->strptime($date, '%b %d, %Y %I:%M %p');
#my $sqlTime = $t->strftime('%F %T');
use Time::Piece::MySQL;
my $sqlTime = localtime->mysql_datetime;
	#Make a list of all the queues so we can compare against it when we find it in the alphas. 
my $cronacleFailRpt = "/Library/WebServer/Cronacle/FailReport/FailReport.txt";
my $cronacleRunRpt = "/Library/WebServer/Cronacle/Running/RunningReport.txt";
my $cronacleLongRunning = "/Library/WebServer/Cronacle/Running/TVLongRunningReport.txt"; #NEW
my $cronacleComplete = "/Library/WebServer/Cronacle/Reports/Completed.txt";
my $cronacleSchedule = "/Library/WebServer/Cronacle/Reports/Scheduled.txt";
my $cronacleFailRipe = "/Library/WebServer/Cronacle/FailReport/TVFailReport.txt";
my $cronacleRunRipe = "/Library/WebServer/Cronacle/Running/TVRunningReport.txt";
my $ripeFailRpt = "/Library/WebServer/Becky/data_production_fail.electronic";
my $ripeRunRpt = "/Library/WebServer/Becky/data.production_status";
my @incidentCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","STAMP","STATE","LOG","ORIG_JOB");

open LOG,">/PerlTemp/testsnaplog.txt";
			use DBI;
			my $dbuser = "root";
			my $dbpass = "alaska";
			my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
			my $sth = $dbh->prepare("Select JOBID, TYPE, NAME FROM alphas where TYPE = ? OR TYPE = ?");
			$sth->execute("GenQue","BatchQue");
			my @QueueList;
			my %QueueID;
			my @jobList;
			my %jobID;
		while (my @row = $sth->fetchrow_array) {
			my $keyID = "$row[1]\|$row[2]";
			#print LOG "@row\n";
			@QueueList = (@QueueList,$keyID);
			$QueueID{$keyID} = $row[0];		
		}
			$sth->finish();
			my $sth2 = $dbh->prepare("Select JOBID, ENTRY, NAME FROM alphas where TYPE = 'JOB'");
			$sth2->execute();
		while (my @row = $sth2->fetchrow_array) {
			my $keyID = "$row[1]\|$row[2]";
			#print "$keyID\n";
			@jobList = (@jobList,$keyID);
			$jobID{$keyID} = $row[0];		
		}
		foreach my $key (keys %QueueID) {
			 print LOG "$key = $QueueID{$key}\n";
		}
		foreach my $key (keys %jobID) {
			 print LOG "$key = $jobID{$key}\n";
		}			
			#print LOG join ("\n",@jobList);
			#print LOG join ("\n",@QueueList);
			#print LOG "\n\n\n";
			$sth2->finish();	
			$dbh->disconnect();
			
			### Get current INCIDENTS list
			my @incList;
			my $dbh = DBI->connect("DBI:mysql:incidents;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
			my $sth = $dbh->prepare("Select JOBID, TYPE, NAME FROM INCIDENTS WHERE STATUS != 'RESOLVED'");
			$sth->execute();
		while (my @row = $sth->fetchrow_array) {
			my $keyID = "$row[1]\|$row[2]";
			@incList = (@incList,$keyID);
		}
			$sth->finish();	
			$dbh->disconnect();

	my $alphas = "/Library/WebServer/Becky/snapshot9.txt";
	#ClosedDIV("class","$snapLast[0]","AV MONITOR $snapLast[1]");	
	tie my @records, 'Tie::File', $alphas;
	my $fullFile = join "\n",@records;
	untie @records;
	$fullFile =~ s/  Entry  Jobname         Username             Status\n//g;
	$fullFile =~ s/  -----  -------         --------             ------\n//g;
	$fullFile =~ s/       %SYSTEM-F-ABORT, abort\n//g;
while ($fullFile =~ m/\n\s/g) {
	#$fullFile =~ s/\n\s\s/\n/g;
	#$fullFile =~ s/\n\s\s/\n/g;
 	$fullFile =~ s/\n\s/\n/g;
} 	 
	$fullFile =~ s/::\n/::/g;
	$fullFile =~ s/ +/ /g;
	$fullFile =~ s/\n(\/|\"|\<|\()/ /g;
	$fullFile =~ s/(Batch queue.*)\n/\@$1 \n\@/g;
	#$fullFile =~ s/\nBatch/\n\@Batch/g;
	$fullFile =~ s/(Generic batch.*)\n/\@$1 \n\@/g;
	#$fullFile =~ s/(Printer.*)\n/\@$1 \n\@/g;
	#$fullFile =~ s/(Printer.*)\n/\@$1 \n\@/g;
	$fullFile =~ s/Printer.*\n//g;
	$fullFile =~ s/Logical.*\n//g;
	$fullFile =~ s/(COM;\d+.*\n)/COM\n\@/g;
	$fullFile =~ s/COM;\d+/COM\@/g;
	$fullFile =~ s/\n\@(Completed.*\n)/ $1 \n\@/g;
	$fullFile =~ s/\n\@(TURBOX.*\n)/ $1 \n\@/g;
	$fullFile =~ s/\@\@/\@/g;
	$fullFile =~ s/\n/ /g;
	$fullFile =~ s/\@/\n/g;
#open FH,">/PerlTemp/testalphas.txt";
#print FH $fullFile;
#close FH;


my @allbatch_queues;
my $Questopped = 0;
my $ExecTot = 0;
my $PendTot = 0;
my $HoldTot = 0;
my $FailTot = 0;
my @allJobs;
my @ignore_X2 = ("TURBOX2_MAC3","TURBOX2_MAC4","TURBOX2_MAC5","TURBOX2_MAC6","TURBOX2_MAC7","TURBOX2_MAC8","TURBOX2_MAC9");
my @ignore_adgen = ("TURBOX6ADGEN_MAC3","TURBOX6ADGEN_MAC4");
my @ignore_x6 = ("TURBOX6_MACD","TURBOX6_MAC12");
my @ignore_xq = ("TURBOXQ_MAC4","TURBOXQ_MAC3");
my @ignore_x = ("TURBOX_MAC3","TURBOX_MAC4","TURBOX_MAC5");
my @ignore_alpha = ("EDDIE_ELEC_EXT","XXX","ZIP9","RIPE_EXT_DEVRIPE10","RIPE_EXT_DEVRIPE04");
my @ignore_queues = (@ignore_X2,@ignore_adgen,@ignore_x6,@ignore_xq,@ignore_x,@ignore_alpha);
my @ignore_generic = ("GENERIC_SAMPLES_EXT");
my @HeaderNames = ("Customer","Script Name","Listing Date","Status","Due","Job");
my @headerSizes = ("25","25","12","12","12","7","12","10");
my $colCount = 0;
my ($PARAM1,$PARAM2,$PARAM3,$PARAM4,$PARAM5,$PARAM6,$PARAM7,$PARAM8);
my $updateID;

my @allLines = split("\n",$fullFile);
open FH,">/PerlTemp/testalphas.txt";
foreach (@allLines) {
print FH $_ . "\n";
}
close FH;

	my $queu_tracker;
	my $now_queue;
	my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
	
my @jobsDONE;
		my $now_queue;
	#print join " ",@found_batchQs;
	foreach (@allLines) {
	#print LOG $_ . "\n";
		if ($_ =~ m/GENERIC=/) {
			#print LOG "$_\n";
			my @Gen_que_parts = split(' ',$_);
			my $this_GQ = $Gen_que_parts[3];
			if ($this_GQ ~~ @ignore_generic) {next; }
			my $gen_batch_qs = $_;
			$now_queue = $this_GQ;
			print LOG "Current queue is $now_queue\n";
				if ($gen_batch_qs =~ m/TURBOX2_GENERIC/) {
					$gen_batch_qs =~ s/.*GENERIC=\((.*)\)\sOWNER.*/$1/;
				} else {
					$gen_batch_qs =~ s/.*GENERIC=\((.*)\)\s\/OWNER.*/$1/;			
				}
			$gen_batch_qs =~ s/\s| //g;
			my @Batch_q_list = split(',',$gen_batch_qs);
			my $recordThis = "GenQue|$this_GQ";
			my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
			my @insertThis = ("GenQue","$this_GQ","","","$this_GQ","$gen_batch_qs","","","","","","","","","NOW()");
			my %updatehash;
			@updatehash{@insertCols} = @insertThis;	
			if ("GenQue\|$this_GQ" ~~ @QueueList) {
				print "Updating GenQue\|$this_GQ\n";
				my $updateID = $QueueID{"GenQue\|$this_GQ"};
				updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$updateID");
				print LOG "Updating $this_GQ\n";
			} else {
			my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
				my @addstarttime = (@insertThis,"NOW()");
				print "Inserting GenQue\|$this_GQ\n";
				insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@addstarttime);
				print LOG "Added $this_GQ\n";
			}
			@allJobs = (@allJobs,$recordThis);			
###
		} elsif ($_ =~ /^Batch queue/) {
				#print LOG "$_\n";
				#my $now_queue;
				my @batch_q_parts = split(',',$_);
				my $bq_status = $batch_q_parts[1];
				$bq_status =~ s/\s//;
				my @batch_name_parts = split(' ',$batch_q_parts[0]);
				my $batch_name = $batch_name_parts[2];
				$now_queue = $batch_name;
				if ($batch_name ~~ @ignore_queues) { next;}
				print LOG "Current queue is $now_queue\n";
			#if ($batch_name ~~ @found_batchQs) { next; }
				my $find_limit = $_;
				my $find_limit = /JOB_LIMIT\=(.*)\s/;
				my $job_limit = $1;
				if ($job_limit =~ /\//g) {
					my @limit_parts = split('\s',$job_limit);
					$job_limit = $limit_parts[0];
				}
				my $updateID;
				if ($now_queue eq "") {next;}
					my $recordThis = "BatchQue|$now_queue";
					my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
					my @insertThis = ("BatchQue","$now_queue","$bq_status","","$job_limit","","","","","","","","","","NOW()");
					my %updatehash;
					@updatehash{@insertCols} = @insertThis;	
				#	my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"NAME|$now_queue");					
					if ("BatchQue\|$now_queue" ~~ @QueueList) {
						print "Updating BatchQue\|$now_queue\n";
						print LOG "Updating $now_queue\n";
						my $updateID = $QueueID{"BatchQue\|$now_queue"};
						my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$updateID");
					} else {
						my @addstarttime = (@insertThis,"NOW()");
						print "Inserting BatchQue\|$now_queue\n";
						my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
						my %user_info = insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@addstarttime);
						print LOG "Adding $now_queue\n";
					}
					@allJobs = (@allJobs,$recordThis);						
		} elsif ($_ =~ /^\d/) {
				my ($PARAM1,$PARAM2,$PARAM3,$PARAM4,$PARAM5,$PARAM6,$PARAM7,$PARAM8);
				my $IFPARAMS;
				my @getParams;
				my $job_state;
				my $these_params;
				my @job_parts = split(' ',$_);
				my $job_num = $job_parts[0];
				my $job_name = $job_parts[1];
				my $script_status = $job_parts[3];
				my $params = $_;
				if ($_ =~ m/PARAM/) {
						$params =~ /PARAM\=(.*)PRIORITY/;
						$these_params = $1;
						$these_params =~ s/\(//g;
						$these_params =~ s/\)//g;
						$these_params =~ s/\"//g;
						$these_params =~ s/\///g;
				} else {
						$these_params = "NO PARAMS";
				}
				if ($script_status =~ /Pending/) {
							$job_state = "Pending";
								#	OpenDIV("class","ApoRowWarn","");
							$PendTot++;
				} elsif  ($script_status eq "Holding") {
							$job_state = "Holding";
							#$HoldTot;
				} elsif  ($script_status =~ "Retain") {
								$job_state = "Holding";
								$FailTot++;						
				} else  {
								$job_state = "Executing";
								$ExecTot++;						
				}
				if ($these_params eq "NO PARAMS") {
					$IFPARAMS = "N";
					print "No Params\n";
					($PARAM1,$PARAM2,$PARAM3,$PARAM4,$PARAM5,$PARAM6,$PARAM7,$PARAM8) = ("","","","","","","","");
				} else {
					$IFPARAMS = "Y";
					@getParams = split(",",$these_params);	
					$_ //= "NA" for @getParams; 
					#print "@getParams\n";
					($PARAM1,$PARAM2,$PARAM3,$PARAM4,$PARAM5,$PARAM6,$PARAM7,$PARAM8) = @getParams;	
					
				}

				print LOG "Current job $job_name - queue is $now_queue\n";
				if ($now_queue ~~ @ignore_queues) { next;}

				my %updatehash;
			#	my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"NAME|$now_queue");					
				if ("$job_num\|$job_name" ~~ @jobList) {
					#print  "Updating $job_num $job_name\n";
				my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
				my @insertThis = ("JOB","$job_name","$script_status","$job_num","$now_queue","$IFPARAMS","$PARAM1","$PARAM2","$PARAM3","$PARAM4","$PARAM5","$PARAM6","$PARAM7","$PARAM8","NOW()");
				@updatehash{@insertCols} = @insertThis;	
					my $jobUPid = $jobID{"$job_num\|$job_name"};
					my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$jobUPid");
					@jobsDONE = (@jobsDONE,"$job_num|$job_name");					
					
					print LOG "Updating $job_num $job_name\n";
				
				} else {
				my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
				my @insertThis = ("JOB","$job_name","$script_status","$job_num","$now_queue","$IFPARAMS","$PARAM1","$PARAM2","$PARAM3","$PARAM4","$PARAM5","$PARAM6","$PARAM7","$PARAM8","NOW()","NOW()");
					#print  "Inserting $job_num $job_name\n";
						my %user_info = insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@insertThis);
						#if (($script_status =~ /^Retain/m) && ("$job_num\|$job_name" !~ @incList)) {
						#if ($script_status =~ /Retain/) {
							#print "Creating new incident\n";
							#my @incidentvals = (@insertThis,"NEW");
							#print "Incidents: @incidentCols\n";
							#my $incs = join ",",@incidentvals;
							#print "Values: $incs\n";
							#createIncident("Incidents","INCIDENTS",\@incidentCols,\@incidentvals);
						#}
						print LOG "Inserting $job_num $job_name\n";
						@jobsDONE = (@jobsDONE,"$job_num\|$job_name");					
				}
		#		my $recordThis = "JOB|$script_status|$now_queue|$job_num|$job_name|$these_params";
				my $recordThis = "$job_num|$job_name";
				#print "JOB|$this_BQ|$script_status|$job_num|$job_name|$these_params\n";
				if ($job_name =~ /^REGEN/) {
					next;
				} else {
					@allJobs = (@allJobs,$recordThis);
				}
				next;				
			
		}
	} #	foreach (@allLines) {
open FH,">/PerlTemp/alljobs.txt";
print FH $fullFile;
foreach (@allJobs) {
#print FH "$_\n";
}
close FH;

close LOG;

open RLOG,">/PerlTemp/newRipelog.txt";
			use DBI;
			my $dbuser = "root";
			my $dbpass = "alaska";
			my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
			#my $sth = $dbh->prepare("Select JOBID, NAME, ENTRY FROM alphas where QUEUE = ?");
			my $sth = $dbh->prepare("SELECT * FROM alphas WHERE QUEUE = ? or QUEUE = ?");
			$sth->execute("RIPE","CRONACLE");
			#my @jobList;
			print RLOG "Ripe\n\n";
			#my %jobID;
		while (my @row = $sth->fetchrow_array) {
			my $keyID = "$row[2]\|$row[4]";
			print RLOG "Found job $keyID\n";
			@jobList = (@jobList,$keyID);
			$jobID{$keyID} = $row[0];		
		}
			#foreach my $key (keys %jobID) {
			# print RLOG "$key = $jobID{$key}\n";
			#}
			
			#print LOG join ("\n",@jobList);
			$sth->finish();	
			$dbh->disconnect();

	my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
	my $inHungProc = "FALSE";
	my @RipeFails;
	my $fullFile;
	tie my @records, 'Tie::File', $ripeFailRpt;
	#my $fullFile = join "\n",@records;
	my ($PartOneLine,$PartTwoLine,$restOfLine,$notes);
	#print LOG "$fullFile";
	foreach $fullFile (@records) {
		my $notes = "";
		if ($fullFile =~ /^ POSSIBLE/) {last;}
		if (($fullFile =~ /^( ------------|\(|    |\n| +\n| \n| FAILED| PRODUCTION)/) || ($fullFile eq "")) {next;}
		$notes = substr($fullFile,85,14);
		$notes =~ s/ +/ /g;
		$notes =~ s/ /-/g;
		my $PartOneLine = substr($fullFile,0,84);
		my $PartTwoLine = substr($fullFile,103,(length($fullFile)));
		if ($notes eq "-") {$notes = "NOTES";}
		my $restOfLine = "$PartOneLine $notes $PartTwoLine";
		$restOfLine =~ s/ +/ /g;
		$restOfLine =~ s/ _____________ //g;
		$restOfLine =~ s/'//g;
		$restOfLine =~ s/"//g;
		if ($restOfLine =~ m/^\d/) {
			print RLOG "FAILURES\n";
			print RLOG $restOfLine . "\n";
			#print LOG "$restOfLine\n";
			@RipeFails = (@RipeFails,$restOfLine);
		}
 	}
	#print LOG "Fail Report: $fullFile";
	untie @records;
#	@RipeFails = split("\n",$fullFile);
	
	tie my @records, 'Tie::File', $ripeRunRpt;
	my $runFile = join "\n",@records;
	untie @records;
	$runFile =~ s/ -------.*\n//g;
	$runFile =~ s/ +/ /g;
	$runFile =~ s/ PRODUCTION STATUS REPORT: LOGS \n//g;
	$runFile =~ s/\(0 rows affected\)//g;
	$runFile =~ s/\(\d (rows|row) affected\)\n//g;
	$runFile =~ s/\(\d\d rows affected\)\n//g;
	$runFile =~ s/ \n \n/\n/g;	  
	$runFile =~ s/ \n /\n/g;	  
	my @RipeRuns = split("\n",$runFile);
		#print RLOG $runFile . "\n";

	my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
	my $inHungProc = "FALSE";
	my @CronFails;
	my @CronRuns;
	my @CronRipeFails;
	my @CronRipeRuns;
	my @CronLongRunning;

	my $fullFile;
	tie my @records, 'Tie::File', $cronacleFailRpt;
	foreach my $CronFile (@records) {
		if ($CronFile =~ m/^Job Id|\n/) {next;}
			@CronFails = (@CronFails,$CronFile);
 	}
	untie @records;

	tie my @records, 'Tie::File', $cronacleLongRunning; #NEW
	foreach my $CronFile (@records) {
		if ($CronFile =~ m/^Job Id|\n/) {next;}
			@CronLongRunning = (@CronLongRunning, $CronFile);
 	}
	untie @records;
	# Test Section
	open FILE, '>', "test.txt";
	print FILE @CronLongRunning;
	close FILE;

	tie my @records, 'Tie::File', $cronacleFailRipe;
	foreach my $CronFile (@records) {
		if ($CronFile =~ m/^Job Id|\n/) {next;}
			@CronRipeFails = (@CronRipeFails,$CronFile);
 	}
	untie @records;
	
	tie my @records, 'Tie::File', $cronacleRunRpt;
	my $runFile = join "\n",@records;
	foreach my $CronFile (@records) {
		if ($CronFile =~ m/^Job Id|\n/) {next;}
			@CronRuns = (@CronRuns,$CronFile);
 	}
	untie @records;

	tie my @records, 'Tie::File', $cronacleRunRipe;
	my $runFile = join "\n",@records;
	foreach my $CronFile (@records) {
		if ($CronFile =~ m/^Job Id|\n/) {next;}
			@CronRipeRuns = (@CronRipeRuns,$CronFile);
 	}
	untie @records;

	my $keyID;
	my @ignoreSystems = ("qaripe01","regripe01");
	my ($schedID,$prodID,$custCode,$product,$date1,$notes,$system,$step,$errcode,$startdate,$starttime,$enddate,$endtime,$duetime) = ("","","","","","","","","","","","","","");

foreach (@CronFails) {
		my @CronLines = split('\|',$_);
		my @insertCols =  ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
		my @toInput = ("JOB",$CronLines[3],"Retained",$CronLines[0],"CRONACLE","",$CronLines[5],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],$CronLines[9],"NOW()");
		my %updatehash;
		@updatehash{@insertCols} = @toInput;	
		if ("$toInput[1]|$toInput[3]" ~~ @jobList) {
				print  "Updating $toInput[1] $toInput[3]\n";
				my $jobUPid = $jobID{"$toInput[1]\|$toInput[3]"};
				my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$jobUPid");
		} else {
				my @insertCols =  ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
				my @toInput = ("JOB",$CronLines[3],"Retained",$CronLines[0],"CRONACLE","",$CronLines[5],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],$CronLines[9],"NOW()","NOW()");
				insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@toInput);
				my @incidentInput = (@toInput,"NEW");
				my $keyID = "$toInput[1]|$toInput[3]";
			}
				@jobsDONE = (@jobsDONE,"$toInput[1]|$toInput[3]");					
}

#if statement added to exclude EDIT jobs 5318 KRS
foreach (@CronLongRunning) {
		# Job Id|Cust Code|Product Lookup|System|Step|Date|Job Chain
		my @CronLines = split('\|',$_);
		if ($CronLines[1] ne 'EDIT') {
			my @insertCols =  ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
			my @toInput = ("JOB",$CronLines[2],"Retained",$CronLines[0],"CRONACLE","","Long Running Jobs",$CronLines[5],$CronLines[3],$CronLines[4],$CronLines[6],"","","","NOW()");
			my %updatehash;
			@updatehash{@insertCols} = @toInput;	
			if ("$toInput[1]|$toInput[3]" ~~ @jobList) {
				print  "Updating $toInput[1] $toInput[3]\n";
				my $jobUPid = $jobID{"$toInput[1]\|$toInput[3]"};
				my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$jobUPid");
			} else {
			if (@toInput[1] !~ m/48533$|49294$/){
				my @insertCols =  ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
				my @toInput = ("JOB",$CronLines[2],"Retained",$CronLines[0],"CRONACLE","","Long Running Jobs",$CronLines[5],$CronLines[3],$CronLines[4],$CronLines[6],"","","","NOW()","NOW()");
				insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@toInput);
				my @incidentInput = (@toInput,"NEW");
				my $keyID = "$toInput[1]|$toInput[3]";
				}
			}
				@jobsDONE = (@jobsDONE,"$toInput[1]|$toInput[3]");	
		}				
}

#if statement added to exclude EDIT jobs 5318 KRS
foreach (@CronRipeFails) {
		my @CronLines = split('\|',$_);
		if ($CronLines[1] ne 'EDIT') {
			#my ($schedID,$prodID,$custCode,$product,$date1,$notes,$system,$step,$errcode,$startdate,$starttime,$enddate,$endtime,$duetime) = @CronLines;
			my @insertCols =  ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
			#my @toInput = ("JOB",$CronLines[3],"Retained",$CronLines[0],"CRONACLE","",$CronLines[5],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],$CronLines[9],"NOW()");
			my @toInput = ("JOB",$CronLines[2],"Retained",$CronLines[0],"CRONACLE","RIPE",$CronLines[3],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],$CronLines[9],"NOW()","NOW()");
			my %updatehash;
				@updatehash{@insertCols} = @toInput;	
			if ("$toInput[1]|$toInput[3]" ~~ @jobList) {
					print  "Updating $toInput[1] $toInput[3]\n";
					my $jobUPid = $jobID{"$toInput[1]\|$toInput[3]"};
					my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$jobUPid");
			} else {
				my @insertCols =  ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
			my @toInput = ("JOB",$CronLines[2],"Retained",$CronLines[0],"CRONACLE","RIPE",$CronLines[3],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],$CronLines[9],"NOW()","NOW()");
				insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@toInput);
				my @incidentInput = (@toInput,"NEW");
#insertTABLE("Incidents","INCIDENTS",\@incidentCols,\@incidentInput);
				my $keyID = "$toInput[1]|$toInput[3]";
				#print LOG join (" - ",@toInput) . "\n";
			}
				@jobsDONE = (@jobsDONE,"$toInput[1]|$toInput[3]");					
			#$jobID{$keyID} = $row[0];		
		}
}

foreach (@CronRuns) {
		my $notes = "";
		my @CronLines = split('\|',$_);
		my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
		my @toInput = ("JOB",$CronLines[3],"Executing",$CronLines[0],"CRONACLE","",$CronLines[5],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],"","NOW()");
				my %updatehash;
				@updatehash{@insertCols} = @toInput;	
				if ("$toInput[1]|$toInput[3]" ~~ @jobList) {
						print  "Updating $toInput[1] $toInput[3]\n";
					my $jobUPid = $jobID{"$toInput[1]|$toInput[3]"};
					my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$jobUPid");
				} else {
		my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
		my @toInput = ("JOB",$CronLines[3],"Executing",$CronLines[0],"CRONACLE","",$CronLines[5],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],"","NOW()","NOW()");
					insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@toInput);
					my $keyID = "$toInput[1]|$toInput[3]";
				@jobsDONE = (@jobsDONE,"$toInput[1]|$toInput[3]");					
			}
}

#if statement added to exclude EDIT jobs 5318 KRS
foreach (@CronRipeRuns) {
		my $notes = "";
		my @CronLines = split('\|',$_);
		if ($CronLines[1] ne 'EDIT') {
				my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
#		my @toInput = ("JOB",$CronLines[3],"Executing",$CronLines[0],"CRONACLE","",$CronLines[5],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],"","NOW()");
				my @toInput = ("JOB",$CronLines[2],"Executing",$CronLines[0],"CRONACLE","RIPE",$CronLines[3],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],"","NOW()");
				my %updatehash;
				@updatehash{@insertCols} = @toInput;	
				if ("$toInput[1]|$toInput[3]" ~~ @jobList) {
						print  "Updating $toInput[1] $toInput[3]\n";
					my $jobUPid = $jobID{"$toInput[1]|$toInput[3]"};
					my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$jobUPid");
				} else {
					my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
					my @toInput = ("JOB",$CronLines[2],"Executing",$CronLines[0],"CRONACLE","RIPE",$CronLines[3],$CronLines[1],$CronLines[2],$CronLines[4],$CronLines[6],$CronLines[7],$CronLines[8],"","NOW()","NOW()");
					insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@toInput);
					my $keyID = "$toInput[1]|$toInput[3]";
					@jobsDONE = (@jobsDONE,"$toInput[1]|$toInput[3]");					
				}
		}
}


foreach (@RipeFails) {
	if ($_ =~ m/^\d/) {
		my @ripeLines = split(" ",$_);
		my ($schedID,$prodID,$custCode,$product,$date1,$notes,$system,$step,$errcode,$startdate,$starttime,$enddate,$endtime,$duetime) = @ripeLines;
				my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
			my @toInput = ("JOB",$product,"Retained",$schedID,"RIPE","",$system,$custCode,$notes,$prodID,$step,"$startdate $starttime","$enddate $endtime","","NOW()");
				my %updatehash;
				@updatehash{@insertCols} = @toInput;	
			if ($system =~ /^qa|^re|^dev|^sta/) {next;}
			if (uc($notes) =~ /TEST/) {next;}
			if ((uc($notes) =~ /IF-ROUT/)  && ($step eq "ROUTE")){next;}
			if ("$toInput[1]\|$toInput[3]" ~~ @jobList) {
					print  RLOG "Updating $toInput[1]|$toInput[3]\n";
					my $jobUPid = $jobID{"$toInput[1]\|$toInput[3]"};
					my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$jobUPid");
			} else {
				my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
				print  RLOG "Inserting $toInput[1]|$toInput[3]\n";
				my @toInput = ("JOB",$product,"Retained",$schedID,"RIPE","",$system,$custCode,$notes,$prodID,$step,"$startdate $starttime","$enddate $endtime","","NOW()","NOW()");
				insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@toInput);
				#my @incidentcols = (@insertCols,"STATE");
				my @incidentInput = (@toInput,"NEW");
	#insertTABLE("Incidents","INCIDENTS",\@incidentCols,\@incidentInput);
				my $keyID = "$toInput[1]|$toInput[3]";
				#print LOG join (" - ",@toInput) . "\n";
			}
				@jobsDONE = (@jobsDONE,"$toInput[1]|$toInput[3]");					
			#$jobID{$keyID} = $row[0];		
		
	}
}
foreach (@RipeRuns) {
	if ($_ =~ m/^\d/) {
		my $notes = "";
		my @ripeLines = split(" ",$_);
		print RLOG "$_\n";
		my ($schedID,$custCode,$product,$system,$date1,$process,$continue,$step,$startdate,$starttime,$enddate,$endtime,$leftover) = @ripeLines;
			if ($process eq "Process") {
				my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp");
				my @toInput = ("JOB",$product,"Executing",$schedID,"RIPE","",$system,$custCode,"","",$step,"$startdate $starttime","$enddate $endtime","","NOW()");
				my %updatehash;
				@updatehash{@insertCols} = @toInput;	
				if ($system =~ /^qa|^re|^dev|^sta/) {next;}
				if (uc($notes) =~ /TEST/) {next;}
				if ((uc($notes) =~ /IF-ROUT/)  && ($step eq "ROUTE")){next;}
				if ("$toInput[1]\|$toInput[3]" ~~ @jobList) {
						print  LOG "Updating $toInput[1] $toInput[3]\n";
					my $jobUPid = $jobID{"$toInput[1]\|$toInput[3]"};
					my %user_info = updateTABLE("SNAPSHOTS","alphas",\%updatehash,"JOBID|$jobUPid");
				} else {
					my @toInput = ("JOB",$product,"Executing",$schedID,"RIPE","",$system,$custCode,"","",$step,"$startdate $starttime","$enddate $endtime","","NOW()","NOW()");
				my @insertCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STARTTIME");
				insertTABLE("SNAPSHOTS","alphas",\@insertCols,\@toInput);
					my $keyID = "$toInput[1]|$toInput[3]";
				@jobsDONE = (@jobsDONE,"$toInput[1]|$toInput[3]");					
			}
			}
			#@jobList = (@jobList,$keyID);
			#$jobID{$keyID} = $row[0];		
		
	}
}


my $removeID;
#Look for jobs to delete from Database
my @ComCols = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","COMPLETED","STARTTIME","ORIG_JOB");
		my @rows;
 		my $dbh = DBI->connect("DBI:mysql:SNAPSHOTS;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
		my $sth = $dbh->prepare("SELECT * FROM alphas WHERE Stamp < ?");		
		$sth->execute($sqlTime);
		while (@rows = $sth->fetchrow_array) {
 			my $removeID = $rows[0];
 			print  "Removing JOBID $rows[0]\n";
 			print "@rows\n";
  			print "@ComCols\n";		
			insertTABLE("SNAPSHOTS","completed",\@ComCols,\@rows);
			my $sth2 = $dbh->prepare("DELETE FROM alphas WHERE JOBID = ?");
			$sth2->execute("$removeID");
		}
		$sth->finish();		
		$sth2->finish();
		$dbh->disconnect();

close RLOG;

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
		print "$key is $value\n";
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
	my $idSave = @valsarr[0];
	shift @valsarr;
	@valsarr = (@valsarr,$idSave);
}
#no incidents inserted from this script
if ($tablename eq "INCIDENTS") {
	my @colsarr = ("TYPE","NAME","STATUS","ENTRY","QUEUE","PARAMETERS","PARAM1","PARAM2","PARAM3","PARAM4","PARAM5","PARAM6","PARAM7","PARAM8","Stamp","STATE","LOG","ORIG_JOB");
	my $idSave = @valsarr[0];
	shift @valsarr;
	@valsarr = (@valsarr,$idSave);
}

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

	#my $username = $userdata{USERNAME};
	#my $sth2 = $dbh->prepare($sqlGet);
	#$sth2->execute($username);
	#my @fields =  @{ $sth2->{NAME_uc} };
	#my @user_row = $sth2->fetchrow_array;
	#my %userdata;
 	#@userdata{@fields} = @user_row;	
	#$sth2->finish();
	
	
	$dbh->disconnect();
	#emailuser("new",\%userdata);
	#return(%userdata);
}


#NOt creating Incidents from here. 

sub createIncident {
my ($dbname,$tablename,$colVals,$Vals) = @_;
my $dbuser = "root";
my $dbpass = "alaska";
my @colsarr = @$colVals;
my @valsarr = @$Vals;
my $valsto;
my %userdata;
  @userdata{@colsarr} = @valsarr;	
my $keycount = 0;
my $cols = join(",",@colsarr);
my $orig_number = @valsarr[0];
foreach (@valsarr) {
 if ($keycount == 0) {
		next;
	} elsif ($_ eq "NOW()") {
		$valsto = "$valsto,'$sqlTime'";
	} else {
		$valsto = "$valsto,'$_'";
	}
	$keycount++;
}
$valsto = "$valsto,'$orig_number'";
my $vals = join(",",@valsarr);
my $sqlUpdate = "INSERT INTO $tablename ($cols) VALUES ($valsto)";
#my $sqlGet = "SELECT * from  $tablename where USERNAME = ?";
	print "$sqlUpdate\n\n";
	use DBI;
	my $dbh = DBI->connect("DBI:mysql:$dbname;host=localhost",$dbuser,$dbpass,{RaiseError => 1});
	my $sth = $dbh->prepare($sqlUpdate);
	$sth->execute();
	$sth->finish();

	#my $username = $userdata{USERNAME};
	#my $sth2 = $dbh->prepare($sqlGet);
	#$sth2->execute($username);
	#my @fields =  @{ $sth2->{NAME_uc} };
	#my @user_row = $sth2->fetchrow_array;
	#my %userdata;
 	#@userdata{@fields} = @user_row;	
	#$sth2->finish();
	
	
	$dbh->disconnect();
	#emailuser("new",\%userdata);
	#return(%userdata);
}
