#!/usr/bin/perl
use strict;
use warnings;

# Funzione ricorsiva per risolvere la Torre di Hanoi
sub hanoi {
    my ($n, $from, $to, $aux) = @_;

    if ($n == 1) {
        print "Sposta disco 1 da $from a $to\n";
        return;
    }

    hanoi($n - 1, $from, $aux, $to);
    print "Sposta disco $n da $from a $to\n";
    hanoi($n - 1, $aux, $to, $from);
}

# --- Programma principale ---

print "Inserisci il numero di dischi: ";
chomp(my $n = <STDIN>);

if ($n !~ /^\d+$/ || $n < 1) {
    die "Devi inserire un numero intero positivo!\n";
}

print "\nSoluzione per $n dischi:\n\n";
hanoi($n, 'A', 'C', 'B');

my $mosse = 2**$n - 1;
print "\nNumero totale di mosse: $mosse\n";
