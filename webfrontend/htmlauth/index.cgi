#!/usr/bin/perl

use File::HomeDir;
use CGI qw/:standard/;
use HTML::Entities;
use String::Escape qw( unquotemeta );
use warnings;
no strict "refs"; # we need it for template system
use LoxBerry::System;
use LoxBerry::IO;

my $mqttcred = LoxBerry::IO::mqtt_connectiondetails();
my  $home = File::HomeDir->my_home;
my  $lang;
my  $installfolder;
my  $cfg;
my  $conf;
our $psubfolder;
our $template_title;
our $namef;
our $value;
our %query;
our $cache;
our $helptext;
our $language;	
our $select_language;
#our $debug;
#our $select_debug;
our $do;
our $select_ms;
our $savedata;

our $lookup_timeout;
our $loop_time;
our $rediscover_time;
our $auto_mode;
our $loop_mode;
our $remote_lock;
our $time_zone;
our $mqtt_broker;
our $mqtt_port;
our $mqtt_clientid;
our $mqttname;
our $mqtt_username;
our $mqtt_password;
our $mqtt_topic_prefix;
our $mqtt_retain;
our $mqtt_qos;
our $broadlink_thermostatstatus;


# Read Settings
$cfg             = new Config::Simple("$lbsconfigdir/general.cfg");
$installfolder   = $cfg->param("BASE.INSTALLFOLDER");
$lang            = $cfg->param("BASE.LANG");



print "Content-Type: text/html\n\n";

# Parse URL
foreach (split(/&/,$ENV{"QUERY_STRING"}))
{
  ($namef,$value) = split(/=/,$_,2);
  $namef =~ tr/+/ /;
  $namef =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $query{$namef} = $value;
}

# Set parameters coming in - GET over POST
#if ( !$query{'miniserver'} ) { if ( param('miniserver') ) { $miniserver = quotemeta(param('miniserver')); } else { $miniserver = $miniserver;  } } else { $miniserver = quotemeta($query{'miniserver'}); }

if ( !$query{'lookup_timeout'} ) { if ( param('lookup_timeout') ) { $lookup_timeout = quotemeta(param('lookup_timeout')); } else { $lookup_timeout = "20"; } } else { $lookup_timeout = quotemeta($query{'lookup_timeout'}); }
if ( !$query{'loop_time'} ) { if ( param('loop_time') ) { $loop_time = quotemeta(param('loop_time')); } else { $loop_time = "10"; } } else { $loop_time = quotemeta($query{'loop_time'}); }
if ( !$query{'rediscover_time'} ) { if ( param('rediscover_time') ) { $rediscover_time = quotemeta(param('rediscover_time')); } else { $rediscover_time = "600"; } } else { $rediscover_time = quotemeta($query{'rediscover_time'}); }
if ( !$query{'remote_lock'} ) { if ( param('remote_lock') ) { $remote_lock = quotemeta(param('remote_lock')); } else { $remote_lock = "0"; } } else { $remote_lock = quotemeta($query{'remote_lock'}); }
if ( !$query{'time_zone'} ) { if ( param('time_zone') ) { $time_zone = quotemeta(param('time_zone')); } else { $time_zone = "Europe/Berlin"; } } else { $time_zone = quotemeta($query{'time_zone'}); }
if ( !$query{'mqtt_broker'} ) { if ( param('mqtt_broker') ) { $mqtt_broker = quotemeta(param('mqtt_broker')); } else { $mqtt_broker = $mqttcred->{brokerhost}; } } else { $mqtt_broker = quotemeta($query{'mqtt_broker'}); }
if ( !$query{'mqtt_port'} ) { if ( param('mqtt_port') ) { $mqtt_port = quotemeta(param('mqtt_port')); } else { $mqtt_port = $mqttcred->{brokerport}; } } else { $mqtt_port = quotemeta($query{'mqtt_port'}); }
if ( !$query{'mqtt_clientid'} ) { if ( param('mqtt_clientid') ) { $mqtt_clientid = quotemeta(param('mqtt_clientid')); } else { $mqtt_clientid = "broadlink"; } } else { $mqtt_clientid = quotemeta($query{'mqtt_clientid'}); }
if ( !$query{'mqttname'} ) { if ( param('mqttname') ) { $mqttname = quotemeta(param('mqttname')); } else { $mqttname = "mqtt"; } } else { $mqttname = quotemeta($query{'mqttname'}); }
if ( !$query{'mqtt_username'} ) { if ( param('mqtt_username') ) { $mqtt_username = quotemeta(param('mqtt_username')); } else { $mqtt_username = $mqttcred->{brokeruser}; } } else { $mqtt_username = quotemeta($query{'mqtt_username'}); }
if ( !$query{'mqtt_password'} ) { if ( param('mqtt_password') ) { $mqtt_password = quotemeta(param('mqtt_password')); } else { $mqtt_password = $mqttcred->{brokerpass}; } } else { $mqtt_password = quotemeta($query{'mqtt_password'}); }
if ( !$query{'mqtt_topic_prefix'} ) { if ( param('mqtt_topic_prefix') ) { $mqtt_topic_prefix = quotemeta(param('mqtt_topic_prefix')); } else { $mqtt_topic_prefix = "broadlink"; } } else { $mqtt_topic_prefix = quotemeta($query{'mqtt_topic_prefix'}); }
if ( !$query{'mqtt_retain'} ) { if ( param('mqtt_retain') ) { $mqtt_retain = quotemeta(param('mqtt_retain')); } else { $mqtt_retain = "True"; } } else { $mqtt_retain = quotemeta($query{'mqtt_retain'}); }
if ( !$query{'mqtt_qos'} ) { if ( param('mqtt_qos') ) { $mqtt_qos = quotemeta(param('mqtt_qos')); } else { $mqtt_qos = "2"; } } else { $mqtt_qos = quotemeta($query{'mqtt_qos'}); }
if ( !$query{'auto_mode'} ) { if ( param('auto_mode') ) { $auto_mode = quotemeta(param('auto_mode')); } else { $auto_mode = "0"; } } else { $auto_mode = quotemeta($query{'auto_mode'}); }
if ( !$query{'loop_mode'} ) { if ( param('loop_mode') ) { $loop_mode = quotemeta(param('loop_mode')); } else { $loop_mode = "0"; } } else { $loop_mode = quotemeta($query{'loop_mode'}); }


# Figure out in which subfolder we are installed
$psubfolder = abs_path($0);
$psubfolder =~ s/(.*)\/(.*)\/(.*)$/$2/g;

# Save settings to config file
if (param('savedata')) {
	
	open(my $DATEIHANDLER, ">$lbpconfigdir/broadlink-thermostat.cfg");
	print $DATEIHANDLER "lookup_timeout = " . unquotemeta($lookup_timeout) . "\n";
	print $DATEIHANDLER "loop_time = " . unquotemeta($loop_time) . "\n";
	print $DATEIHANDLER "rediscover_time = " . unquotemeta($rediscover_time) . "\n";
	print $DATEIHANDLER "remote_lock = " . unquotemeta($remote_lock) . "\n";
	print $DATEIHANDLER "time_zone = '" . unquotemeta($time_zone) . "'\n";
	print $DATEIHANDLER "mqtt_broker = '" . unquotemeta($mqtt_broker) . "'\n";
	print $DATEIHANDLER "mqtt_port = " . unquotemeta($mqtt_port) . "\n";
	print $DATEIHANDLER "mqtt_clientid = '" . unquotemeta($mqtt_clientid) . "'\n";
	print $DATEIHANDLER "mqttname = '" . unquotemeta($mqttname) . "'\n";
	print $DATEIHANDLER "mqtt_username = '" . unquotemeta($mqtt_username) . "'\n";
	print $DATEIHANDLER "mqtt_password = '" . unquotemeta($mqtt_password) . "'\n";
	print $DATEIHANDLER "mqtt_topic_prefix = '" . unquotemeta($mqtt_topic_prefix) . "'\n";
	print $DATEIHANDLER "mqtt_retain = " . unquotemeta($mqtt_retain) . "\n";
	print $DATEIHANDLER "mqtt_qos = " . unquotemeta($mqtt_qos) . "\n";
	print $DATEIHANDLER "auto_mode = " . unquotemeta($auto_mode) . "\n";
	print $DATEIHANDLER "loop_mode = " . unquotemeta($loop_mode) . "\n";
	close($DATEIHANDLER);
	
	system ("$installfolder/system/daemons/plugins/$psubfolder restart");
}

# Parse config file
$conf = new Config::Simple("$lbpconfigdir/broadlink-thermostat.cfg");
#$miniserver = encode_entities($conf->param('MINISERVER'));
$lang = encode_entities($conf->param('LANGUAGE'));	
$udp_port = encode_entities($conf->param('UDP_PORT'));
$lookup_timeout = encode_entities($conf->param('lookup_timeout'));
$loop_time = encode_entities($conf->param('loop_time'));
$rediscover_time = encode_entities($conf->param('rediscover_time'));
$remote_lock = encode_entities($conf->param('remote_lock'));
$time_zone = encode_entities($conf->param('time_zone'));
$mqtt_broker = encode_entities($conf->param('mqtt_broker'));
$mqtt_port = encode_entities($conf->param('mqtt_port'));
$mqtt_clientid = encode_entities($conf->param('mqtt_clientid'));
$mqttname = encode_entities($conf->param('mqttname'));
$mqtt_username = encode_entities($conf->param('mqtt_username'));
$mqtt_password = encode_entities($conf->param('mqtt_password'));
$mqtt_topic_prefix = encode_entities($conf->param('mqtt_topic_prefix'));
$mqtt_retain = encode_entities($conf->param('mqtt_retain'));
$mqtt_qos = encode_entities($conf->param('mqtt_qos'));
$loop_mode = encode_entities($conf->param('loop_mode'));
$auto_mode = encode_entities($conf->param('auto_mode'));


# Set Enabled / Disabled switch
#

#if ($debug eq "1") {
#	$select_debug = '<option value="0">off</option><option value="1" selected>on</option>';
#} else {
#	$select_debug = '<option value="0" selected>off</option><option value="1">on</option>';
#}


# ---------------------------------------
# Fill Miniserver selection dropdown
# ---------------------------------------
#for (my $i = 1; $i <= $cfg->param('BASE.MINISERVERS');$i++) {
#	if ("MINISERVER$i" eq $miniserver) {
#		$select_ms .= '<option selected value="'.$i.'">'.$cfg->param("MINISERVER$i.NAME")."</option>\n";
#	} else {
#		$select_ms .= '<option value="'.$i.'">'.$cfg->param("MINISERVER$i.NAME")."</option>\n";
#	}
#}


# ---------------------------------------
# Start Stop Service
# ---------------------------------------
# Should Broadlink_Thermostat Server be started

if ( param('do') ) { 
	$do = quotemeta( param('do') ); 
	if ( $do eq "start") {
		system ("$installfolder/system/daemons/plugins/$psubfolder start");
	}
	if ( $do eq "stop") {
		system ("$installfolder/system/daemons/plugins/$psubfolder stop");
	}
	if ( $do eq "restart") {
		system ("$installfolder/system/daemons/plugins/$psubfolder restart");
	}
}

# Title
$template_title = "broadlink_thermostat";
$broadlink_thermostatstatus = qx($installfolder/system/daemons/plugins/$psubfolder status);

# Create help page
$helptext = "<b>Hilfe</b><br>Wenn ihr Hilfe beim Einrichten benĂ¶tigt findet ihr diese im LoxWiki.";
$helptext = $helptext . "<br><a href='https://www.loxwiki.eu/display/LOXBERRY/broadlink_thermostat2lox' target='_blank'>LoxWiki - broadlink_thermostat2lox</a>";
#$helptext = $helptext . "<br><br><b>Debug/Log</b><br>Um Debug zu starten, den Schalter auf on stellen und speichern.<br>Die Log-Datei kann hier eingesehen werden. ";
#$helptext = $helptext . "<a href='/admin/system/tools/logfile.cgi?logfile=plugins/$psubfolder/broadlink_thermostat.log&header=html&format=template&only=once' target='_blank'>Log-File - broadlink_thermostat</a>";
#$helptext = $helptext . "<br><br><b>Achtung!</b> Wenn Debug aktiv ist werden sehr viele Daten ins Log geschrieben. Bitte nur bei Problemen nutzen.";


# Currently only german is supported - so overwrite user language settings:
$lang = "de";

# Load header and replace HTML Markup <!--$VARNAME--> with perl variable $VARNAME
open(F,"$lbstemplatedir/$lang/header.html") || die "Missing template system/$lang/header.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

# Load content from template
open(F,"$lbptemplatedir/$lang/content.html") || die "Missing template $lang/content.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

# Load footer and replace HTML Markup <!--$VARNAME--> with perl variable $VARNAME
open(F,"$lbstemplatedir/$lang/footer.html") || die "Missing template system/$lang/header.html";
  while (<F>) {
    $_ =~ s/<!--\$(.*?)-->/${$1}/g;
    print $_;
  }
close(F);

exit;
