#! /bin/perl
use File::Find;

# my $found = "";
# find(\&wanted,"/Users/admin/Desktop");


# sub wanted {
#     if($_ =~ "XMLandHTML"){
#         `mv $_ $_.`        
#     };
# }

*name   = *File::Find::name;
*dir    = *File::Find::dir;
*prune  = *File::Find::prune;

sub wanted;

# Traverse desired filesystems
File::Find::find({wanted => \&wanted}, '/');
exit;

sub wanted {
    my ($dev,$ino,$mode,$nlink,$uid,$gid);


    (($dev,$ino,$mode,$nlink,$uid,$gid) = lstat($_)) &&
    print("$name\n");
}

# Set the variable $File::Find::dont_use_nlink if you're using AFS,
# since AFS cheats.

# for the convenience of &wanted calls, including -eval statements:
use vars qw/$name $dir $prune/;
$name   = $File::Find::name;
$dir    = $File::Find::dir;
$prune  = $File::Find::prune;

sub wanted;

# Traverse desired filesystems
File::Find::find({wanted => \&wanted}, '/');
exit;

sub wanted {
    /Jason/s
    && print("$name\n");
}

print $found;