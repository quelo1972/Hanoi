#!/usr/bin/perl
use strict;
use warnings;
use Tk;
use Tk::Dialog;

my $mw = MainWindow->new;
$mw->title("Torre di Hanoi - Gioco Completo");

# ---------------- VARIABILI ----------------

my $num_disks = 4;
my @towers;
my $move_count = 0;
my $delay = 500;
my $selected_tower;
my $auto_mode = 0;

my @colors = qw(red orange yellow green cyan blue purple brown pink magenta);
my @tower_centers = (150, 300, 450);

# ---------------- UI ----------------

my $top = $mw->Frame()->pack(-side => 'top');

$top->Label(-text => "Dischi:")->pack(-side => 'left');

my $disk_entry = $top->Entry(-width => 5);
$disk_entry->insert(0, $num_disks);
$disk_entry->pack(-side => 'left');

$top->Button(-text => "Start Auto", -command => \&start_auto)->pack(-side => 'left');
$top->Button(-text => "Reset", -command => \&reset_game)->pack(-side => 'left');

$top->Label(-text => "Velocità")->pack(-side => 'left');

$top->Scale(
    -from => 100,
    -to => 1000,
    -orient => 'horizontal',
    -variable => \$delay
)->pack(-side => 'left');

my $move_label = $top->Label(-text => "Mosse: 0")->pack(-side => 'left');
my $min_label  = $top->Label(-text => "Minime: 0")->pack(-side => 'left');

my $canvas = $mw->Canvas(
    -width  => 600,
    -height => 400,
    -bg     => 'white'
)->pack;

# ---------------- LOGICA ----------------

sub init_towers {
    @towers = ([], [], []);
    for (my $i = $num_disks; $i >= 1; $i--) {
        push @{$towers[0]}, $i;
    }
    $move_count = 0;
    $selected_tower = undef;
    update_labels();
}

sub update_labels {
    $move_label->configure(-text => "Mosse: $move_count");
    my $min = 2**$num_disks - 1;
    $min_label->configure(-text => "Minime: $min");
}

sub draw_towers {
    $canvas->delete("all");

    for my $t (0..2) {

        my $pole_color = (defined $selected_tower && $selected_tower == $t)
                         ? 'red'
                         : 'black';

        # Palo
        $canvas->createRectangle(
            $tower_centers[$t] - 5, 100,
            $tower_centers[$t] + 5, 300,
            -fill => $pole_color
        );

        # Base
        $canvas->createRectangle(
            $tower_centers[$t] - 80, 300,
            $tower_centers[$t] + 80, 310,
            -fill => 'black'
        );

        # Dischi
        for my $i (0..$#{$towers[$t]}) {
            my $disk = $towers[$t][$i];
            my $width = $disk * 15;
            my $y = 290 - ($i * 20);

            $canvas->createRectangle(
                $tower_centers[$t] - $width,
                $y - 15,
                $tower_centers[$t] + $width,
                $y,
                -fill => $colors[$disk % @colors]
            );
        }
    }
}

sub valid_move {
    my ($from, $to) = @_;
    return 0 unless @{$towers[$from]};
    return 1 unless @{$towers[$to]};
    return $towers[$from][-1] < $towers[$to][-1];
}

sub move_disk {
    my ($from, $to) = @_;
    return unless valid_move($from, $to);

    my $disk = pop @{$towers[$from]};
    push @{$towers[$to]}, $disk;

    $move_count++;
    update_labels();
    draw_towers();
    check_win();
}

sub check_win {
    # Controlla le torri 1 e 2 (diverse da quella iniziale 0)
    for my $i (1..2) {
        if (@{$towers[$i]} == $num_disks) {
            my $min = 2**$num_disks - 1;

            $mw->Dialog(
                -title   => "Vittoria!",
                -text    => "Hai completato la torre!\n\nMosse: $move_count\nMinimo teorico: $min",
                -buttons => ["OK"]
            )->Show();

            # Blocca ulteriori selezioni dopo la vittoria
            $selected_tower = undef;
            $auto_mode = 1;

            return 1;
        }
    }
    return 0;
}

# ---------------- AUTO ----------------

sub hanoi_auto {
    my ($n, $from, $to, $aux) = @_;
    return if $n == 0;

    hanoi_auto($n-1, $from, $aux, $to);
    move_disk($from, $to);
    $mw->update;
    select(undef, undef, undef, $delay/1000);
    hanoi_auto($n-1, $aux, $to, $from);
}

sub start_auto {
    $auto_mode = 1;

    my $input = $disk_entry->get;
    return unless $input =~ /^\d+$/ && $input > 0 && $input < 10;

    $num_disks = $input;

    init_towers();
    draw_towers();

    $mw->after(500, sub {
        hanoi_auto($num_disks, 0, 2, 1);
        $auto_mode = 0;
    });
}

sub reset_game {
    $auto_mode = 0;

    my $input = $disk_entry->get;
    $num_disks = ($input =~ /^\d+$/) ? $input : 4;

    init_towers();
    draw_towers();
}

# ---------------- CLICK (SOLUZIONE ROBUSTA) ----------------

$canvas->CanvasBind('<Button-1>' => sub {

    return if $auto_mode;

    my $e = $canvas->XEvent;
    my $x = $e->x;

    my $tower;

    for my $i (0..2) {
        if (abs($x - $tower_centers[$i]) < 80) {
            $tower = $i;
            last;
        }
    }

    return unless defined $tower;

    if (!defined $selected_tower) {

        return unless @{$towers[$tower]};
        $selected_tower = $tower;

    } else {

        move_disk($selected_tower, $tower);
        $selected_tower = undef;
    }

    draw_towers();
});

# ---------------- AVVIO ----------------

init_towers();
draw_towers();
MainLoop;
