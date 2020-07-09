#!/usr/bin/perl -w 

# rsync -ave ssh System.pl web-x1:$HOME/scripts/crons/System.pl
# for x in `cat $HOME/xxx/web`; do rsync -ave ssh System.pl $x:$HOME/scripts/crons/System.pl; done

use lib qw(.);

use JSON;
use strict;
use DB::DBISimple;
use POSIX qw(strftime); 

my $db   = DB::DBISimple->new();
my $json = JSON->new();

# Ex:  191001.log
my $todays_log = strftime( '%y%m%d', localtime() ) . ".log";

my $host = `hostname -s`;
chomp $host;
$host =~ s/.+-(.+)/$1/;

# System stats.
{
	my $ref      = {};
	$ref->{cpu}  = cpu_percent();
	$ref->{mem}  = mem_percent();
	$ref->{swap} = swap_percent();
	$ref->{disk} = disk_percent();

	my $json_string = $json->encode( $ref );

	save_system_json( json_string => $json_string, host => $host, type => 'm' );
}

# Insert into the db.
sub save_system_json {
	my ( %args ) = @_;

	my $type        = $args{type};
	my $host        = $args{host};
	my $json_string = $args{json_string};

	if ( $json_string ) {

		my $db_name = 'default-config';
		my $sql     = qq~select count(1) count from SystemStats where host = ? and type = '$type'~;
		my $fetch   = $db->fetch( { sql => $sql, values => $host, db_name => $db_name, single => 1 } );
		my $count   = $fetch->{count};

		my @binds = ();

		if ( $count ) {
			$sql   = qq~update SystemStats set json = ? where host = ? and type = '$type'~;
			@binds = ( $json_string, $host );
		} else {
			$sql   = qq~insert into SystemStats (host, json, type) values(?, ?, '$type')~;
			@binds = ( $host, $json_string );
		}

		if ( @binds ) {
			$db->write( { sql => $sql, values => \@binds, db_name => $db_name } );
		}
	}
}

sub swap_percent {
	my ( %args ) = @_;

	my $swaps = `tail -1 /proc/swaps`;
	$swaps    =~ s/\s+/ /g;
	my @swaps = split ' ', $swaps;
	
	my $swap_total = $swaps[2];
	my $swap_used  = $swaps[3];
	my $swap_avail = $swap_total - $swap_used;
	my $diff       = $swap_total - $swap_avail;

	$diff = ( $diff / $swap_total ) * 100;

	my $percent_used = sprintf( "%.2f", $diff ); 

	return $percent_used;
}

# Percentage used combined with buffer usage.
sub mem_percent { 
	my ( %args ) = @_;

	my $mem_total = `cat /proc/meminfo | grep MemTotal | gawk -F":" {'print \$2'}`;
	my $mem_free  = `cat /proc/meminfo | grep MemAvailable | gawk -F":" {'print \$2'}`;

	# Support old systems that don't have MemAvailable.
	if ( !$mem_free ) {
		$mem_free  = `free | grep buffers | gawk -F" " {'print \$4'} | grep -P '[0-9]+'`;
	}

	$mem_total =~ s/kb//i;
	$mem_free  =~ s/kb//i;
	$mem_total = int ( $mem_total / 1024 );
	$mem_free  = int ( $mem_free / 1024 );

	my $used = $mem_total - $mem_free;

	$used = ( $used / $mem_total ) * 100;
	$used = sprintf( "%.2f", $used ); 

	return $used;
}

sub disk_percent { 
	my ( %args ) = @_;

	my $disk_used = `df -h / | tail -1`;
	my $disk_size = '';

	$disk_used = trim( $disk_used );
	$disk_used =~ s/\s+/ /g;

	my @disk_used = split ' ', $disk_used;
	$disk_used    = $disk_used[ $#disk_used -1 ];
	$disk_used    =~ s/\%//g;
	$disk_used    = sprintf( "%.2f", $disk_used ); 

	return $disk_used;
}

sub cpu_percent { 
	my ( %args ) = @_;

	my $cpu_count = `cat /proc/cpuinfo | grep -c ^processor`;
	my $cpu_load  = `cat /proc/loadavg`;
	( $cpu_load ) = ( $cpu_load =~ /([0-9\.]+)\s/ );

	chomp $cpu_count;

	my $cpu_used = ( $cpu_load / $cpu_count ) * 100;
	$cpu_used    = sprintf( "%.2f", $cpu_used ); 

	return $cpu_used;
}

sub trim {
	my $input = $_[0];

	if ( $input ) {
		$input =~ s/^\s+|\s+$//g;
	}

	return $input;
}
