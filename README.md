       mmm  mmm                                          mmm   mm 
      ###  ###              ##                          ###   ## 
      ########   m####m   #######    m#####m            ##"#  ## 
     ## ## ##  ##mmmm##    ##       " mmm##            ## ## ## 
     ## "" ##  ##""""""    ##      m##"""##   #####    ##  #m## 
    ##    ##  "##mmmm#    ##mmm   ##mmm###            ##   ### 
    ""    ""    """""      """"    """" ""            ""   """ 

An interactive picker, inspired by [ctrlp](https://github.com/kien/ctrlp.vim/) and [lash](https://github.com/siadat/lash/).

Work in progress!

## Features ##

* Good shell integration: usable in pipes and with command substitution (`$(mn)`).  Allows you to come up with new use cases on the fly.
* Slow/infinite input, such as `find /`.

## Getting started ##

Bind Meta-N i tmux:

    bind-key -n M-n split-window -l 10 "tmux select-window -t $(tmux list-windows | mn --print | cut -d: -f1)"

## Normal use-cases ##

Select window in `tmux`:

    bind-key -n M-n split-window -l 10 "tmux select-window -t $(tmux list-windows | mn --print | cut -d: -f1)"

Pick a host to connect to, from `known_hosts`:

    awk '-F[, ]' '{ print $1 }' < ~/.ssh/known_hosts | mn ssh

## Key bindings ##

### Editing the pattern ###
Ctrl-a, e, w, u: (Almost) as in readline

Left/right: Move cursor in the pattern

Ctrl-r, s: Load previous/next pattern from history

### Choosing ###

Up/Down: Move cursor between choices

Ctrl-z: Select

Ctrl-x: Change to the next pattern mode

Enter: Return data under cursor if no selections, otherwise return all choices chosen with Ctrl-z.

## Crazy examples ##

Pick a python-file in the current directory to run `ls -l` on:

    ls -1 *.py | mn -- ls -l

You can also use command substitution `$()` with `--print`.  Do not use this mode if you want to be able to abort with Ctrl-c!

    ls -l $(ls -1 *.py | mn --print)

...or `xargs -0`:

    find / -size +10M | mn --print0 | xargs -0 sudo gzip -v
