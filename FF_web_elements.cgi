#!/Users/scripting/perl5/perlbrew/perls/perl-5.24.0/bin/Perl
##########################################
#
#	by Larry Gonyea
#      TMS
#  The Feature_Editor script creates new features as well as opens existing features.
#  It takes information from the template file to determine the field type and field name
#  If this is opening a feature already started, it will display information from the feature within the fieldname tags and place it in the correct form fields.
#  
###############################################

sub OpenDIV {
	my $divType = $_[0];
	my $divClass = $_[1];
	my $divContent = $_[2];
	my $divTitle = $_[3];
		print "<div $divType=\"$divClass\">${divContent}\n";
}

sub ClosedDIV {
	my $divType = $_[0];
	my $divClass = $_[1];
	my $divContent = $_[2];
	my $divTitle = $_[3];
	if ($divTitle ne "") {
	print "<span title=\"$divTitle\"><div $divType=\"$divClass\">${divContent}</div></span>\n";
	} else {
		print "<div $divType=\"$divClass\">${divContent}</div>\n";
	}
}

sub EndDIV {
print "</div>";
}

sub makeHTML5type {
print "Content-type: text/html; charset=utf-8\n\n";
print "<!DOCTYPE html>\n\n";
print "<html>\n";
print "<head>\n";
#print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />";
print "<meta charset=\"utf-8\">";
print "<META HTTP-EQUIV=\"Pragma\" CONTENT=\"no-cache\">";
print "<META HTTP-EQUIV=\"expires\" CONTENT=\"0\">";
#print "<meta charset=\"UTF-8\">";

}
sub makeHTMLuploadtype {
print "Content-type: text/html\n\n";
print "<!DOCTYPE html>\n\n";
print "<html>\n";
print "<head>\n";
print "<META HTTP-EQUIV=\"Pragma\" CONTENT=\"no-cache\">";
print "<META HTTP-EQUIV=\"expires\" CONTENT=\"0\">";
}
sub HTMLtitle {
# Param 1 is title of the page
my $thisTitle = $_[0];
my $thisFocus = $_[1];
print "<title>$thisTitle</title>\n";
print "<BODY>\n";
}
sub HTMLend {
# no params. Just ends the web page neatly.
print "</body>\n";
print "</html>\n";
}

## Loads the Style sheet file for the web pages.
sub LoadCSS {
my $CSSfile = $_[0];
if ($CSSfile eq '') {
	print "<link href=\"/featman2.css\" rel=\"stylesheet\" media=\"screen\">\n";
} else {
	print "<link href=\"/$CSSfile\" rel=\"stylesheet\" media=\"screen\">\n";
}
print "<link href=\"/print.css\" rel=\"stylesheet\" media=\"print\">\n";
}

## Loads the Style sheet file for Feature Editor web page.
### no longer used. See LoadCSS
sub LoadEditorCSS {
print "<link href=\"$ThisIP/feat_editor_style.css\" rel=\"stylesheet\" media=\"screen\">\n";
print "<link href=\"$ThisIP/print.css\" rel=\"stylesheet\" media=\"print\">\n";
}

## Loads the Style sheet file for Feature Editor web page.
#sub LoadEditorCSS {
#print "<link href=\"/feat_editor_style.css\" rel=\"stylesheet\" media=\"screen\">\n";
#print "<link href=\"/print.css\" rel=\"stylesheet\" media=\"print\">\n";
#}

## Loads the Javascript required to have ckeditor fields.
sub LoadJS {
print "<script src=\"../../ckeditor/ckeditor.js\">\n";
print "</script>\n";
print "<script type=\"text/javascript\" src=\"../../jquery/jquery-2.0.3.min.js\">\n";
print "</script>\n";

#print "<script type=\"text/javascript\">";
#print " document.getElementsByTagName(\"eventsource\")[0].";
#print "            addEventListener(\"server-time\", eventHandler, false);";
#print "   function eventHandler(event)";
#print "   {";
#print "       // Alert time sent by the server";
#print "       document.querySelector('#ticker').innerHTML = event.data;";
#print "   }";
#print "</script>";

print "<style>\n";
print "		.cke_focused,\n";
print "		.cke_editable.cke_focused\n";
print "		{\n";
print "			outline: 3px dotted blue !important;\n";
print "			*border: 3px dotted blue !important;	/* For IE7 */\n";
print "		} \n";
print "	\n";
print "	</style>\n";
print "</head>\n";
}
sub JavaUploader {
my $fadeDIV = $_[0];
my $fadeSpeed = $_[1];
print "<script src=\"../../uploader.js\">\n";
print "</script>\n";
}

sub javaPhotoToggle {
print "<script type=\"text/javascript\">\n";
print "$(\".PhotoContentCardHead\").click(function() { \n";
print "\$('.photo-thumb').toggle()\n";
print "</script>\n";

}

sub JQheightChange {
my $div_target = $_[0];
print "<script type=\"text/javascript\">\n";
print "$( \"$div_target\" ).click(function() {\n";
print "    if ( $(this).height() != 50)\n";
print "          $( this ).animate({ height: 50 }, 1000 );\n";
print "    else\n";
 print "         $( this ).animate({ height: 100 }, 1000 );\n";
print "});\n";
print "</script>\n";
}

sub JQfadeIn {
my $fadeDIV = $_[0];
my $fadeSpeed = $_[1];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$('$fadeDIV').fadeIn('$fadeSpeed')\n";
print "});\n";
print "</script>\n";
}

sub JQtoggleComplete {
my $toggleDIV = $_[0];
my $clickName = $_[1];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$(\"$clickName\").click(function() {\n";
print "if (\$(this).text() == \"Hide Completed Features\"){\n";
print "\$(this).html(\"Show Completed Features\");}\n"; 
print "else{\n"; 
print "\$(this).html(\"Hide Completed Features\");};\n";
print "\$('$toggleClass').toggle()\n";
print "});\n";
print "});\n";
print "</script>\n";
}
sub JQPhototoggle {
my $toggleDIV = $_[0];
my $clickName = $_[1];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$(\"$clickName\").click(function() {\n";
print "if (\$(this).text() == \"Hide Photo Previews\"){\n";
print "\$(this).html(\"Show Photo Previews\");}\n"; 
print "else{\n"; 
print "\$(this).html(\"Hide Photo Previews\");};\n";
print "\$('$toggleDIV').toggle()\n";
print "});\n";
print "});\n";
print "</script>\n";
}

sub JQtoggleNS {
my $toggleDIV = $_[0];
my $clickName = $_[1];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$(\"$clickName\").click(function() {\n";
print "if (\$(this).text() == \"Hide Not Started Features\"){\n";
print "\$(this).text(\"Show Not Started Features\");}\n"; 
print "else{\n"; 
print "\$(this).text(\"Hide Not Started Features\");};\n";
print "\$('$toggleDIV').toggle()\n";
print "});\n";
print "});\n";
print "</script>\n";
}

sub JQtoggleST {
my $toggleDIV = $_[0];
my $clickName = $_[1];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$(\"$clickName\").click(function() {\n";
print "if (\$(this).text() == \"Hide Started Features\"){\n";
print "\$(this).text(\"Show Started Features\");}\n"; 
print "else{\n"; 
print "\$(this).text(\"Hide Started Features\");};\n";
print "\$('$toggleDIV').toggle()\n";
print "});\n";
print "});\n";
print "</script>\n";
}

sub JQtoggleNF{
my $toggleDIV = $_[0];
my $clickName = $_[1];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$(\"$clickName\").click(function() {\n";
print "if (\$(this).text() == \"Show New Features Menu\"){\n";
print "\$(this).text(\"Hide New Features Menu\");}\n"; 
print "else{\n"; 
print "\$(this).text(\"Show New Features Menu\");};\n";
print "\$('$toggleDIV').toggle()\n";
print "});\n";
print "});\n";
print "</script>\n";
}

sub JQtogglePreview {
my $toggleDIV = $_[0];
my $clickName = $_[1];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$(\"$clickName\").click(function() {\n";
print "	if (\$(this).text() == \"Show Photo Previews\"){\n";
print "		\$(this).text(\"Hide Photo Previews\");}\n"; 
print "	else{\n"; 
print "		\$(this).text(\"Show Photo Previews\");}\n"; 
print "		\$('$toggleDIV').toggle()\n";
print "	});\n";
print "});\n";
print "</script>\n";
}

sub JQtoggle{
my $toggleDIV = $_[0];
my $clickName = $_[1];
my $ini_text = $_[2];
my $alt_text = $_[3];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$(\"$clickName\").click(function() {\n";
print "if (\$(this).text() == \"$ini_text\"){\n";
print "\$(this).text(\"$alt_text\");}\n"; 
print "else{\n"; 
print "\$(this).text(\"$ini_text\");};\n";
print "\$('$toggleDIV').toggle()\n";
print "});\n";
print "});\n";
print "</script>\n";
}


sub JQtogglePhotoComplete {
my $toggleDIV = $_[0];
my $clickName = $_[1];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$(\"$clickName\").click(function() {\n";
print "if (\$(this).text() == \"Hide Uploaded Photos\"){\n";
print "\$(this).html(\"Show Uploaded Photos\");}\n"; 
print "else{\n"; 
print "\$(this).html(\"Hide Uploaded Photos\");};\n";
print "\$('$toggleDIV').toggle()\n";
print "});\n";
print "});\n";
print "</script>\n";
}

sub JQtogglePhotosST {
my $toggleDIV = $_[0];
my $clickName = $_[1];
print "<script type=\"text/javascript\">\n";
print "\$(document).ready(function() {\n";
print "\$(\"$clickName\").click(function() {\n";
print "if (\$(this).text() == \"Show Not Uploaded Photos\"){\n";
print "\$(this).text(\"Hide Not Uploaded Photos\");}\n"; 
print "else{\n"; 
print "\$(this).text(\"Show Not Uploaded Photos\");};\n";
print "\$('$toggleDIV').toggle()\n";
print "});\n";
print "});\n";
print "</script>\n";
}


sub PMaker {
my $paraG = $_[0];
print "<p>$paraG</p>\n";
}
1;