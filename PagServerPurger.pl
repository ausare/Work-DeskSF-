use Socket;
use Sys::Hostname;
use Time::Local;
use Mail::Send;
use warnings;
#SCRIPT NAME
$scriptName = "PagServer Purger";

$actualHost = hostname();
@hostNameParts = split(/\./,"$actualHost");
$hostname = "$hostNameParts[0]";
$addr = `ipconfig getifaddr en0`;
chop $addr;

$pemailAddresses = "TMSGF-SCRIPTS@gracenote.com";
$pSMTPmailhost = "mailhost.tis-in.trb";

$gLogFilePath = "";
$gTodaysDate = "";
$gItemCount = "";
$logsLocation = "/Perl/Logs/";



# Get the a ll the values for current time 
($second, $minute, $hour, $day, $month, $year, $daysOfWeek, $dayOfYear, $IsDST) = localtime(time) ; 

#Get the name of the Month
my @monthsOfYear = qw( January Febuary March April May June July August September October November December );
$monthAsWord = "$monthsOfYear[$month]";

#Get the day of the week
my @daysOfWeek = qw( Sunday Monday Tuesday Wednesday Thursday Friday Saturday );
$weekAsWord = "$daysOfWeek";

#Get the 4 digit year
$fullYear = $year + 1900;

#Get the 12 hour clock time
if($hour >= 13)
{
	$realHour = $hour - 12;
}
else
{
	$realHour = $hour;
}

#Get AM or PM
if($hour >= 12)
{
	$amToPm = "PM";
}
else
{
	$amToPm = "AM";
}

if($hour == 0)
{
	$realHour = 12;
	$amToPm = "AM";
}

#If needed add leading zero to minute
if($minute < 10)
{
	$realMinute = "0$minute";
}
else
{
	$realMinute = "$minute";
}

#Set 2 digit month
if($month < 10)
{
	$mm = "0$month";
}
else
{
	$mm = "$month";
}

#Set 2 digit month
if($day < 10)
{
	$dd = "0$day";
}
else
{
	$dd = "$day";
}

#Set 2 digit year
@yearList = split(/|/,"$fullYear");
$yy = "$yearList[2]$yearList[3]";

$mmddyy = "$mm$dd$yy";

$gTodaysDay = "$weekAsWord\, $monthAsWord $day\, $fullYear $realHour\:$realMinute $amToPm\n";

$gLogFilePath = "${logsLocation}LOG FILE -- PagServer Purger:$mmddyy $realHour$realMinute $amToPm\n";

#Open Log File / OVERWRITE
open(LOGFILE,">$gLogFilePath") || die("Cannot Open Log File");

$thisDirectory = `pwd`;
chop $thisDirectory;
print LOGFILE "$scriptName begun on $hostname($addr)\n\n";

	#print LOGFILE  "The following files/folders were deleted on YNI LOGS, over 7 days old:\n";
	#print   "The following files/folders were deleted on YNI LOGS, over 7 days old:\n";
	#runPurge("YNI GENERIC/WebDocs/YNI/logs/", 7 ,0);
	print LOGFILE  "\n\n";
	print LOGFILE  "The following files/folders were deleted on TurboEdit, over 5 days old:\n";
	print  "The following files/folders were deleted on TurboEdit, over 5 days old:\n";

	runPurge("TurboEdit", 5 ,1);
	print LOGFILE  "\n\n";
	print LOGFILE  "The following files/folders were deleted on APRecovery, over 21 days old:\n";
	print   "The following files/folders were deleted on APRecovery, over 21 days old:\n";

	runPurge("APRecovery", 21 ,1);
	print LOGFILE  "\n\n";
	print LOGFILE  "The following files/folders were deleted on PagBackup, over 12 days old:\n";
	print  "The following files/folders were deleted on PagBackup, over 12 days old:\n";

	runPurge("PagBackup", 12 ,1);
	print LOGFILE  "\n\n";
	print LOGFILE  "The following files/folders were deleted on PagBackup PC, over 14 days old:\n";
	print  "The following files/folders were deleted on PagBackup PC, over 14 days old:\n";

	runPurge("PagBackup PC", 14 ,1);
	#runPurge("Operations Support/Backups/ClientScripts", 30 ,0);
	#runPurge("XServ2/Library/WebServer/Scriptlogs", 30 ,0);

print LOGFILE "\n\nScript: $scriptName completed!\n";
close(LOGFILE);

	sendLogEmail();
	
sub runPurge() #volumeName, days, purgeSubDirectories
{
	my @parameters = @_;
	print "$parameters[0]\n";
	my $volumeName = "$parameters[0]";
	my $volumeNameUNIX = makePathUNIX("/Volumes/$volumeName");

	print "Processing $volumeNameUNIX/ ...\n";

	my $daysOut = "$parameters[1]";
	my $purgeSubDirectories = $parameters[2];
	my $seconds_in_one_day = 86400;
	my $secondsBack = $seconds_in_one_day * $daysOut;
	my $theCurrentTime = time();
	my $theTimeSecondsBack = $theCurrentTime - $secondsBack;

	my $directoryPath = "$volumeNameUNIX";
	print "ls $directoryPath\n";
	my $directoryInfo = `ls $directoryPath`;
			opendir(DLDIR, "/Volumes/$volumeName");
			my @contents = readdir DLDIR;
			closedir(DLDIR);

	#@contents = split(/\n/,"$directoryInfo");
	#
	#DELETE FILES
	foreach (@contents) #(my $cntcou = 0;$cntcou < (@contents - 0);$cntcou++)
	{
		print "Searching Folder $_";
	#TheFindByContentFolder  TheVolumeSettingsFolder  Network Trash Folder
		if (($_ =~ /^\./m) || ($_ eq "") || (!defined($_))) {
		next; 
		} else 
		{
			#print "Working on $contents[$cntcou]\n";
			#my @parts = split(/\"/,"$contents[$cntcou]");
			my $pathToFileUNIX = makePathUNIX("/Volumes/$volumeName/$_");
			my $pathToFileLS = "/Volumes/$volumeName/$_";
			
			($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat("$pathToFileLS");
			
			my @CounterPathToVolume = split(/|/,"/Volumes/$volumeName");
			my @CounterPathToFile = split(/|/,"$pathToFileUNIX");
			my $lengthOfVolumePath = (@CounterPathToVolume - 0);
			my $lengthOfFilePath = (@CounterPathToFile - 0);
			print "    $lengthOfVolumePath $lengthOfFilePath\n";
			if($lengthOfFilePath > ($lengthOfVolumePath + 3))
			{
				#if($mtime < $theTimeSecondsBack)
				#{
				#	($m_second, $m_minute, $m_hour, $m_day, $m_month, $m_year, $daysOfWeek, $m_dayOfYear, $m_IsDST) = localtime($mtime);
				#	@monthsOfYear = qw( January Febuary March April May June July August September October November December );
				#	$m_monthAsWord = "$monthsOfYear[$m_month]";
				#	$realName = $_;
				#	$realName =~ s/\:/\//;
						
				#	if(-d "$pathToFileLS") #If path is a directory
				#	{
				#		print LOGFILE  "(Modified on $m_monthAsWord $m_day) /Volumes/$volumeName/$realName\n";
				#		print LOGFILE  "     rm -R -f  $pathToFileUNIX\n";
				#		print   "     rm -R -f  $pathToFileUNIX\n";
				#		print "DELETE DIRECTORY: $volumeNameUNIX/$pathToFileUNIX\n";
				#		$errMessage = `rm -R -f  $volumeNameUNIX/$pathToFileUNIX`;
				#		if(!("$errMessage" eq ""))
				#		{
				#			print LOGFILE  "ERROR: $errMessage\n";
				#		}
				#		$errMessage = "";
				#	}
				#	else
				#	{
				#		print LOGFILE  "(Modified on $m_monthAsWord $m_day) /Volumes/$volumeName/$realName\n";
				#		print LOGFILE  "     rm -R -f $pathToFileUNIX)\n";
				#		print "DELETE FILE: $pathToFileUNIX\n";
				#		$errMessage = `rm -R -f  $pathToFileUNIX`;
				#		if(!("$errMessage" eq ""))
				#		{
				#			print LOGFILE  "ERROR: $errMessage\n";
				#		}
				#		$errMessage = "";
				#	}
				if((-d "$pathToFileLS") && ($purgeSubDirectories == 1))
				{
					print "Do Sub Purge $pathToFileLS\n";
					runSubPurge("$pathToFileLS", $daysOut);
				}
				elsif((-d "$pathToFileLS") && ($purgeSubDirectories == 0))
				{
					print "";
				}
				elsif(-f "$pathToFileLS")
				{
					print "";
				}
				else
				{
					print "ERROR -d $pathToFileLS\n";
				}
			}
			else
			{
				#print LOGFILE  "File or directory ignored because of short name: $pathToFileUNIX\n";
				#print "\n\n File or directory ignored because of short name: $pathToFileUNIX\n\n";
			}
		}	
		
	}
	
}

sub runSubPurge() #volumeName, days, isSubDirectory
{
	my @parameters = @_;
	#print "$parameters[0]\n";
	my $pathName = "$parameters[0]";
	my $pathNameUNIX = makePathUNIX("$pathName");
	my $daysOut = "$parameters[1]";

	my $seconds_in_one_day = 86400;
	my $secondsBack = $seconds_in_one_day * $daysOut;
	my $theCurrentTime = time();
	my $theTimeSecondsBack = $theCurrentTime - $secondsBack;

	print "ls $pathNameUNIX\n";
	my $directoryInfo = `ls $pathNameUNIX`;
			#opendir(DLDIR, $directoryPath);
			#my @contents = readdir DLDIR;
			#closedir(DLDIR);

	#@subcontents = split(/\n/,"$directoryInfo");
			opendir(DLDIR, "$pathName");
			my @subcontents = readdir DLDIR;
			closedir(DLDIR);
	#my @contents = split(/\n/,"$directoryInfo");
	print  "Files in $pathName:\n";
	print  join('\n',"@subcontents");
	#DELETE FILES
	for(my $cntcou = 0;$cntcou < (@subcontents - 0);$cntcou++)
	{
	#TheFindByContentFolder  TheVolumeSettingsFolder  Network Trash Folder
		if (($subcontents[$cntcou] =~ /^\./m) || ($subcontents[$cntcou] =~ /Icon/m) || ($subcontents[$cntcou] eq "") || (!defined($subcontents[$cntcou]))) {
			next; 
		} else 	{
			print "Working on $pathName/$subcontents[$cntcou]\n";
			#my @parts = split(/\"/,"$contents[$cntcou]");
			my $pathToFileUNIX = makePathUNIX("$pathName/$subcontents[$cntcou]");
			my $pathToFileLS = "$pathName/$subcontents[$cntcou]";
			($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat("$pathToFileLS");
			
			my @CounterPathToVolume = split(/|/,"$pathName");
			my @CounterPathToFile = split(/|/,"$pathToFileUNIX");
			my $lengthOfVolumePath = (@CounterPathToVolume - 0);
			my $lengthOfFilePath = (@CounterPathToFile - 0);
			if($lengthOfFilePath > ($lengthOfVolumePath + 3))
			{
				if($mtime < $theTimeSecondsBack)
				{
					($m_second, $m_minute, $m_hour, $m_day, $m_month, $m_year, $m_daysOfWeek, $m_dayOfYear, $m_IsDST) = localtime($mtime);
					@monthsOfYear = qw( January Febuary March April May June July August September October November December );
					$m_monthAsWord = "$monthsOfYear[$m_month]";
					$realName = $subcontents[$cntcou];
					$realName =~ s/\:/\//;
					print "checking $pathToFileLS\n";
					if(-d "$pathToFileLS") #If path is a directory
					{
						print LOGFILE  "(Modified on $m_monthAsWord $m_day) $pathName/$realName\n";
						print "DELETE SUB DIRECTORY: $pathToFileUNIX\n";
						$errMessage = `rm -R -f  $pathToFileUNIX`;
						if(!("$errMessage" eq ""))
						{
							print LOGFILE  "ERROR: $errMessage\n";
						}
						$errMessage = "";
					}
					else
					{
						print "";
					$errMessage = `rm -R -f  $pathToFileUNIX`;
					}
				}
				else
				{
					print "DON'T DELETE SUB-SUB DIRECTORY: -d $pathToFileUNIX\n";
					print "";
				}
			}
			else
			{
				#print LOGFILE  "Sub-file or directory ignored because of short name: $pathToFileUNIX\n";
				#print "\n\n File or directory ignored because of short name: $pathToFileUNIX\n\n";
			}
		}	
		
	}
	

}

sub emptyTrash()
{
	my $script = qq|
	ignoring application responses
		tell application "Finder"
			empty trash
			put away (every disk whose local volume is false)
		end tell
	end ignoring
	|;

	AppleScript($script);
}

sub AppleScript
{
	my($script) = shift @_;
#	print "\n$script\n";
	system(qq|osascript -e '$script'|);
}

sub makePathUNIX()
{
	my @parameters = @_;
	my $path = "$parameters[0]";
	my @pathParts = split(/|/,"");

#filter spaces
	@pathParts = split(/ /,"$path");
	my $pathUNIX = "";

	if(! ((@pathParts - 1) == 0) )
	{
		for(my $counter = 0;$counter < (@pathParts - 0);$counter++)
		{
			if(! ($counter == (@pathParts - 1)))
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]\\\ ";
			}
			else
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]";
			}
		}	
	}
	else
	{
		$pathUNIX = "$pathUNIX$pathParts[0]";
	}
#filter parens
	@pathParts = split(/\(/,"$pathUNIX");
	my $pathUNIX = "";

	if(! ((@pathParts - 1) == 0) )
	{
		for(my $counter = 0;$counter < (@pathParts - 0);$counter++)
		{
			if(! ($counter == (@pathParts - 1)))
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]\\\(";
			}
			else
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]";
			}
		}	
	}
	else
	{
		$pathUNIX = "$pathUNIX$pathParts[0]";
	}
	@pathParts = split(/\)/,"$pathUNIX");
	my $pathUNIX = "";

	if(! ((@pathParts - 1) == 0) )
	{
		for(my $counter = 0;$counter < (@pathParts - 0);$counter++)
		{
			if(! ($counter == (@pathParts - 1)))
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]\\\)";
			}
			else
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]";
			}
		}	
	}
	else
	{
		$pathUNIX = "$pathUNIX$pathParts[0]";
	}
#filter ampersands
	@pathParts = split(/\&/,"$pathUNIX");
	my $pathUNIX = "";
	if(! ((@pathParts - 1) == 0) )
	{
		for(my $counter = 0;$counter < (@pathParts - 0);$counter++)
		{
			if(! ($counter == (@pathParts - 1)))
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]\\\&";
			}
			else
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]";
			}
		}	
	}
	else
	{
		$pathUNIX = "$pathUNIX$pathParts[0]";
	}
#filter semicolons
	@pathParts = split(/\;/,"$pathUNIX");
	my $pathUNIX = "";
	if(! ((@pathParts - 1) == 0) )
	{
		for(my $counter = 0;$counter < (@pathParts - 0);$counter++)
		{
			if(! ($counter == (@pathParts - 1)))
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]\\\;";
			}
			else
			{
				$pathUNIX = "$pathUNIX$pathParts[$counter]";
			}
		}	
	}
	else
	{
		$pathUNIX = "$pathUNIX$pathParts[0]";
	}

	my @allcharacters = split(/|/,"$pathUNIX");
	my $lastcharacterindex = (@allcharacters - 1);
	if("$allcharacters[$lastcharacterindex]" eq "/")
	{
		chop $pathUNIX;
	}
#	print "\n$path\n$pathUNIX\n\n";
	return "$pathUNIX";
}

sub sendLogEmail()
{
	my $runninglog = "";
	open (LOGFILE, "$gLogFilePath") || die "Could not open log file to email!";
	while ($line = <LOGFILE>)
	{
		$runninglog = "$runninglog$line";
	}

   close(LOGFILE);
    
    my $msg = new Mail::Send;
    $msg->to('bnelson@gracenote.com','klewis@gracenote.com','lrgonyea@gracenote.com','jagifford@gracenote.com');
  #  $msg->to('klewis@gracenote.com');
  #  $msg->to('lrgonyea@gracenote.com');
    $subject = "PagServer Purger Log: $mmddyy $realHour\:$realMinute";
    $msg->subject($subject);
#    $from = "$hostname\@$addr";
    $from = "PagServer\@gracenote.com";
    $msg->set('From',$from);
#    print "$hostname\n";
    # Launch mailer and set headers. 
    # The filehandle returned by open() is an instance of the Mail::Mailer class.
    my $fh = $msg->open;
    print $fh qq|$runninglog|;
    $fh->close;         # complete the message and send it
}